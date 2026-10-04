"""Deterministic, bounded guardrails; raw user/document content is never logged."""

import hashlib
import re
import unicodedata
from dataclasses import dataclass

from app.core.metrics import guardrail_decisions_total

REFUSAL = "Yêu cầu bị từ chối bởi chính sách bảo mật của InsightHub."

_DIRECT = (
    r"\bignore\b.{0,40}\b(previous|prior|system|developer)\b.{0,30}\b(instruction|prompt|policy)",
    r"\b(reveal|show|print|extract|repeat)\b.{0,40}\b(system|hidden|developer)\b.{0,20}\b(prompt|instruction|policy)",
    r"\b(role|policy)\b.{0,20}\b(override|bypass|change|disable)",
    r"\b(disregard|forget)\b.{0,40}\b(instruction|policy|rules?)",
)
_AGENCY = re.compile(
    r"\b(delete|remove|scale|restart|deploy|execute|run|send|modify|change)\b.{0,50}"
    r"\b(pod|kubernetes|cluster|shell|command|slack|message|infrastructure|resource|cloud)\b",
    re.I | re.S,
)
_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{7,}\d)(?!\d)")
_SECRET = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\b\s*[:=]\s*[A-Za-z0-9_./+\-=]{8,}"
    r"|\b(?:AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|gh[pousr]_[A-Za-z0-9]{20,})\b"
)


@dataclass(frozen=True)
class Decision:
    allowed: bool
    category: str


def _normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def contains_pii(value: str) -> bool:
    return bool(_EMAIL.search(value) or _PHONE.search(value) or _SECRET.search(value))


def inspect_request(question: str) -> Decision:
    normalized = _normalized(question)
    if any(re.search(pattern, normalized, re.I | re.S) for pattern in _DIRECT):
        return Decision(False, "direct_injection")
    if contains_pii(question):
        return Decision(False, "pii")
    unavailable_action = re.search(
        r"\bactions?\b.{0,30}\b(model|assistant)\b.{0,20}\b(can not|can't|cannot)\b",
        normalized,
    )
    if _AGENCY.search(normalized) or unavailable_action:
        return Decision(False, "excessive_agency")
    return Decision(True, "none")


_SEGMENT_BOUNDARY = re.compile(r"(?:\r?\n)+|(?<=[.!?;])\s+")
_MAX_RETRIEVED_CHARS = 32768
_MAX_RETRIEVED_SEGMENTS = 256


def _malicious_retrieved_text(text: str) -> bool:
    normalized = _normalized(text)
    return (
        any(re.search(pattern, normalized, re.I | re.S) for pattern in _DIRECT)
        or bool(_AGENCY.search(normalized))
        or bool(re.search(r"\b(answer|respond|output)\b.{0,30}\b(only|exactly|with)\b", normalized))
    )


def sanitize_retrieved_text(text: str) -> tuple[str | None, bool]:
    """Remove unsafe sentences/lines; ambiguous cross-segment signals fail closed.

    Detection normalizes text, while benign content retains its original spelling.
    These bounded heuristics are a defense layer, not a complete injection detector.
    """
    if len(text) > _MAX_RETRIEVED_CHARS:
        return None, True
    segments = _SEGMENT_BOUNDARY.split(text, maxsplit=_MAX_RETRIEVED_SEGMENTS)
    if len(segments) > _MAX_RETRIEVED_SEGMENTS:
        return None, True
    unsafe = [_malicious_retrieved_text(segment) for segment in segments]
    if not any(unsafe):
        if _malicious_retrieved_text(text):
            return None, True
        return (text if any(char.isalnum() for char in text) else None), False
    cleaned = "\n".join(segment.strip() for segment, blocked in zip(segments, unsafe)
                        if not blocked and any(char.isalnum() for char in segment))
    if not cleaned or _malicious_retrieved_text(cleaned):
        return None, True
    return cleaned, True


def filter_contexts(contexts: list[dict]) -> tuple[list[dict], bool]:
    safe: list[dict] = []
    seen_texts: set[str] = set()
    filtered = False
    for context in contexts:
        text = str(context.get("chunk_text", ""))
        cleaned, changed = sanitize_retrieved_text(text)
        filtered = filtered or changed
        if cleaned is None:
            continue
        normalized = _normalized(cleaned)
        if normalized in seen_texts:
            continue
        seen_texts.add(normalized)
        safe.append({**context, "chunk_text": cleaned} if changed else context)
    guardrail_decisions_total.labels(
        "retrieval", "filtered" if filtered else "allow", "indirect_injection" if filtered else "none"
    ).inc()
    return safe, filtered


_CITATION = re.compile(r"\[(?:nguồn|source)\s*:\s*([^\]\r\n]{1,255})\]", re.I)
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def safe_source_label(source: object) -> str | None:
    """Return a bounded user-facing basename derived only from retrieval metadata."""
    raw = unicodedata.normalize("NFKC", str(source or "")).replace("\\", "/")
    name = raw.rsplit("/", 1)[-1].strip()
    name = _CONTROL.sub("", name)
    name = " ".join(name.split()).replace("[", "").replace("]", "").replace(":", "-")
    if not name or name in {".", ".."}:
        return None
    if len(name) > 120:
        name = name[:120].rstrip()
    if contains_pii(name):
        suffix = ""
        if "." in name:
            extension = name.rsplit(".", 1)[-1]
            if re.fullmatch(r"[A-Za-z0-9]{1,8}", extension):
                suffix = f".{extension.lower()}"
        digest = hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:8]
        return f"redacted-source-{digest}{suffix}"
    return name


def source_labels(contexts: list[dict]) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()
    for context in contexts:
        label = safe_source_label(context.get("source"))
        if label is None:
            continue
        key = label.casefold()
        if key not in seen:
            seen.add(key)
            labels.append(label)
    return labels


def normalize_source_citations(answer: str, contexts: list[dict]) -> tuple[str, list[str]]:
    """Canonicalize citations to retrieved sources and append any missing citations."""
    labels = source_labels(contexts)
    if not labels:
        return answer, []
    canonical = {label.casefold(): label for label in labels}
    seen: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        candidate = safe_source_label(match.group(1))
        if candidate is None:
            return ""
        key = candidate.casefold()
        if key not in canonical or key in seen:
            return ""
        seen.add(key)
        return f"[nguồn: {canonical[key]}]"

    normalized = _CITATION.sub(replace, answer).strip()
    missing = [label for label in labels if label.casefold() not in seen]
    if missing:
        citations = " ".join(f"[nguồn: {label}]" for label in missing)
        normalized = f"{normalized} {citations}".strip()
    return normalized, labels


def sanitize_context_sources(contexts: list[dict]) -> list[dict]:
    sanitized: list[dict] = []
    for context in contexts:
        copy = dict(context)
        label = safe_source_label(copy.get("source"))
        copy["source"] = label or "redacted-source"
        sanitized.append(copy)
    return sanitized


_MAX_OUTPUT_CHARS = 65536
_MAX_PROTECTED_CHARS = 32768
_MAX_PROTECTED_TEXTS = 8
_OVERLAP_GRAM = 40


def contains_protected_text(answer: str, protected_texts: tuple[str, ...]) -> bool:
    """Bounded normalized character shingles detect verbatim policy fragments.

    One 80-character run or 120 covered characters across distinct fragments
    blocks disclosure. Common short phrases do not meet either threshold.
    References and candidate content never enter logs or metric labels.
    """
    if len(answer) > _MAX_OUTPUT_CHARS or len(protected_texts) > _MAX_PROTECTED_TEXTS:
        return True
    candidate = _normalized(answer)
    covered = bytearray(len(candidate))
    for reference in protected_texts:
        if not isinstance(reference, str) or len(reference) > _MAX_PROTECTED_CHARS:
            return True
        normalized = _normalized(reference)
        grams = {normalized[i:i + _OVERLAP_GRAM]
                 for i in range(max(0, len(normalized) - _OVERLAP_GRAM + 1))}
        run_start = -1
        run_end = -1
        for i in range(max(0, len(candidate) - _OVERLAP_GRAM + 1)):
            if candidate[i:i + _OVERLAP_GRAM] not in grams:
                continue
            end = i + _OVERLAP_GRAM
            covered[i:end] = b"\x01" * _OVERLAP_GRAM
            if i > run_end:
                run_start = i
            run_end = end
            if run_end - run_start >= 80:
                return True
    return sum(covered) >= 120


def protect_output(answer: str, protected_texts: tuple[str, ...] = ()) -> tuple[str, bool]:
    leaked_prompt = contains_protected_text(answer, protected_texts)
    protected = answer.rsplit("</think>", 1)[-1].strip() if "</think>" in answer else answer
    protected = _EMAIL.sub("[REDACTED_EMAIL]", protected)
    protected = _PHONE.sub("[REDACTED_PHONE]", protected)
    protected = _SECRET.sub("[REDACTED_SECRET]", protected)
    leaked_prompt = leaked_prompt or bool(
        re.search(r"(?i)(system prompt|hidden instructions?)\s*[:=]", protected)
    )
    if leaked_prompt:
        protected = REFUSAL
    changed = protected != answer
    guardrail_decisions_total.labels(
        "output", "redact" if changed else "allow", "policy" if leaked_prompt else "pii" if changed else "none"
    ).inc()
    return protected, changed
