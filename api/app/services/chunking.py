"""Logical chunk targets with conservative limits for bounded embedding models."""

import unicodedata

from app.core.config import Settings, get_settings

WORDS_PER_TOKEN = 0.75
# No tokenizer download: reserve 112 of mxbai's 512 positions. UTF-8 bytes after
# compatibility normalization deliberately overestimate ordinary wordpieces.
SAFE_INPUT_BUDGETS = {("ollama", "mxbai-embed-large"): 400}


def estimate_embedding_tokens(text: str) -> int:
    """Conservative estimator, not the provider's exact tokenizer."""
    return len(unicodedata.normalize("NFKC", text).encode("utf-8"))


def effective_embedding_budget(settings: Settings) -> int | None:
    limit = SAFE_INPUT_BUDGETS.get(
        (settings.embedding_provider, settings.resolved_embedding_model.split(":")[0])
    )
    return None if limit is None else min(settings.chunk_size, limit)


def _bounded_chunks(text: str, budget: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start
        used = 0
        while end < len(text):
            cost = estimate_embedding_tokens(text[end])
            if used + cost > budget:
                break
            used += cost
            end += 1
        if end == start:
            raise ValueError("Embedding budget cannot hold a Unicode character")
        if end < len(text):
            boundary = text.rfind(" ", start + 1, end + 1)
            if boundary > start and estimate_embedding_tokens(text[start:boundary]) >= budget // 2:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        following = end
        used = 0
        while following > start + 1:
            cost = estimate_embedding_tokens(text[following - 1])
            if used + cost > overlap:
                break
            used += cost
            following -= 1
        start = following
        while start < len(text) and text[start].isspace():
            start += 1
    return chunks


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    words = text.split()
    if not words:
        return []
    budget = effective_embedding_budget(settings)
    if budget is not None:
        return _bounded_chunks(
            " ".join(words), budget, min(settings.chunk_overlap, budget // 4)
        )
    chunk_words = max(int(settings.chunk_size * WORDS_PER_TOKEN), 1)
    overlap_words = int(settings.chunk_overlap * WORDS_PER_TOKEN)
    step = max(chunk_words - overlap_words, 1)
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + chunk_words]))
        if start + chunk_words >= len(words):
            break
    return chunks
