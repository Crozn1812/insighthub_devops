import pytest

from app.intents import Intent, classify_intent


@pytest.mark.parametrize("text,expected", [
    ("InsightHub có healthy không?", Intent.HEALTH),
    ("InsightHub healthy không?", Intent.HEALTH),
    ("health", Intent.HEALTH),
    ("Hôm nay ingest bao nhiêu doc?", Intent.INGEST_TODAY),
    ("ingest today", Intent.INGEST_TODAY),
    ("Pod nào đang lỗi?", Intent.FAILING_PODS),
    ("pods failing", Intent.FAILING_PODS),
    ("xin chào", Intent.UNKNOWN),
])
def test_classification(text: str, expected: Intent) -> None:
    assert classify_intent(text) is expected
