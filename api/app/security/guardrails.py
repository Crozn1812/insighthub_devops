"""Deterministic, bounded guardrails; raw user/document content is never logged."""

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


def filter_contexts(contexts: list[dict]) -> tuple[list[dict], bool]:
    safe: list[dict] = []
    seen_texts: set[str] = set()
    filtered = False
    for context in contexts:
        text = str(context.get("chunk_text", ""))
        normalized = _normalized(text)
        dangerous = any(re.search(pattern, normalized, re.I | re.S) for pattern in _DIRECT)
        dangerous = dangerous or bool(
            re.search(r"\b(answer|respond|output)\b.{0,30}\b(only|exactly|with)\b", normalized)
        )
        if dangerous:
            filtered = True
            continue
        if normalized in seen_texts:
            continue
        seen_texts.add(normalized)
        safe.append(context)
    guardrail_decisions_total.labels(
        "retrieval", "filtered" if filtered else "allow", "indirect_injection" if filtered else "none"
    ).inc()
    return safe, filtered


def protect_output(answer: str) -> tuple[str, bool]:
    protected = answer.rsplit("</think>", 1)[-1].strip() if "</think>" in answer else answer
    protected = _EMAIL.sub("[REDACTED_EMAIL]", protected)
    protected = _PHONE.sub("[REDACTED_PHONE]", protected)
    protected = _SECRET.sub("[REDACTED_SECRET]", protected)
    leaked_prompt = bool(re.search(r"(?i)(system prompt|hidden instructions?)\s*[:=]", protected))
    if leaked_prompt:
        protected = REFUSAL
    changed = protected != answer
    guardrail_decisions_total.labels(
        "output", "redact" if changed else "allow", "policy" if leaked_prompt else "pii" if changed else "none"
    ).inc()
    return protected, changed
