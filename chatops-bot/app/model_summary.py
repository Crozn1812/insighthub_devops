"""Optional gateway summary of bounded facts; facts/permissions remain authoritative."""

import logging
import json

import httpx

from .config import Settings

logger = logging.getLogger("chatops-bot.model")


def summarize(facts: str, settings: Settings) -> str:
    if not settings.model_url:
        return facts
    if not settings.model_key or len(facts) > 2000:
        return facts + "\nAI summary unavailable."
    try:
        with httpx.Client(timeout=90, trust_env=False, follow_redirects=False) as client:
            def allowed(text, phase):
                if not settings.guard_url:
                    return True
                guard = client.post(settings.guard_url.rstrip("/") + "/check",
                                    headers={"X-Guard-Key": settings.guard_key},
                                    json={"text": text, "phase": phase})
                guard.raise_for_status()
                return guard.json().get("allowed") is True
            if not allowed(facts, "input"):
                raise ValueError("Guard blocked model input")
            response = client.post(settings.model_url.rstrip("/") + "/chat/completions",
                                   headers={"Authorization": "Bearer " + settings.model_key},
                                   json={"model": settings.model_name, "max_tokens": 128,
                                         "response_format": {"type": "json_schema", "json_schema": {
                                             "name": "fact_summary", "strict": True, "schema": {
                                                 "type": "object", "properties": {"summary": {"type": "string"}},
                                                 "required": ["summary"], "additionalProperties": False}}},
                                         "messages": [
                                             {"role": "system", "content":
                                              "Summarize observed read-only infrastructure facts in one sentence. "
                                              "Do not add facts, issue commands, claim actions or change permissions."},
                                             {"role": "user", "content": facts}]})
            response.raise_for_status()
            body = response.json()
            content = json.loads(body["choices"][0]["message"]["content"])
            summary = content["summary"]
            if not isinstance(summary, str) or not summary.strip() or len(summary) > 1500:
                raise ValueError("Invalid summary")
            if not allowed(summary, "output"):
                raise ValueError("Guard blocked model output")
        # Facts are retained even if model summary is inaccurate; this is not an executor.
        usage = body.get("usage") or {}
        logger.info("gateway_summary_completed input_tokens=%s output_tokens=%s",
                    usage.get("prompt_tokens"), usage.get("completion_tokens"))
        return facts + "\nAI summary (advisory): " + summary
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        logger.warning("gateway_summary_unavailable")
        return facts + "\nAI summary unavailable."
