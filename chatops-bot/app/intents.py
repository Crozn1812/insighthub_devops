"""Deterministic, no-cost routing for the three required ChatOps intents."""
from enum import Enum
import re
import unicodedata


class Intent(str, Enum):
    HEALTH = "health"
    INGEST_TODAY = "ingest_today"
    FAILING_PODS = "failing_pods"
    UNKNOWN = "unknown"


def _normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.lower())
    return " ".join("".join(char for char in folded if not unicodedata.combining(char)).split())


def classify_intent(text: str) -> Intent:
    normalized = _normalize(text)
    if re.search(r"\b(health|healthy)\b", normalized) or (
        "insighthub" in normalized and "khoe" in normalized
    ):
        return Intent.HEALTH
    if ("ingest" in normalized and ("today" in normalized or "hom nay" in normalized)) or (
        "hom nay" in normalized and "bao nhieu doc" in normalized
    ):
        return Intent.INGEST_TODAY
    if ("pod" in normalized or "pods" in normalized) and any(
        word in normalized for word in ("loi", "failing", "failed", "unhealthy")
    ):
        return Intent.FAILING_PODS
    return Intent.UNKNOWN


HELP_TEXT = (
    "Supported: InsightHub có healthy không?; "
    "Hôm nay ingest bao nhiêu doc?; Pod nào đang lỗi?"
)
