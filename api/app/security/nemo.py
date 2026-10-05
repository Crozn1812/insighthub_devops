"""Optional authenticated NeMo IORails integration; errors fail closed."""

import httpx
from fastapi import HTTPException

from app.core.config import get_settings


def nemo_allowed(text: str, phase: str) -> bool:
    settings = get_settings()
    if not settings.nemo_guardrails_url:
        return True
    if not settings.nemo_guardrails_key:
        raise HTTPException(503, "guardrail_unavailable")
    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(
                settings.nemo_guardrails_url.rstrip("/") + "/check",
                headers={"X-Guard-Key": settings.nemo_guardrails_key},
                json={"text": text, "phase": phase},
            )
            response.raise_for_status()
            body = response.json()
        if not isinstance(body, dict) or type(body.get("allowed")) is not bool:
            raise ValueError("invalid guard response")
        return body["allowed"]
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "guardrail_unavailable") from None
