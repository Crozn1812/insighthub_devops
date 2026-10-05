"""Authenticated Slack ingress and fast durable acknowledgement for Day 5."""
import json

from fastapi import FastAPI, HTTPException, Request
from redis import Redis
from redis.exceptions import RedisError

from .config import Settings
from .queue import ChatEvent, EventQueue
from .slack_security import SlackAuthenticationError, verify_slack_request

app = FastAPI(title="InsightHub ChatOps", version="0.3.0")


def get_settings() -> Settings:
    return Settings.from_env()


def get_redis(settings: Settings) -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


@app.get("/healthz")
def health() -> dict[str, object]:
    settings = get_settings()
    try:
        ready = bool(get_redis(settings).ping())
    except RedisError:
        ready = False
    return {"status": "ok" if ready else "degraded", "ready": ready,
            "transport": settings.transport, "redis": "ok" if ready else "unavailable",
            "queue": "ready" if ready else "not_ready"}


@app.post("/slack/events")
async def slack_events(request: Request) -> dict[str, object]:
    settings = get_settings()
    raw_body = await request.body()
    try:
        verify_slack_request(raw_body,
                             request.headers.get("x-slack-request-timestamp"),
                             request.headers.get("x-slack-signature"),
                             settings.slack_signing_secret)
    except SlackAuthenticationError as exc:
        raise HTTPException(status_code=401, detail="request authentication failed") from exc
    try:
        payload = json.loads(raw_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="invalid JSON") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="invalid payload")
    if payload.get("type") == "url_verification":
        challenge = payload.get("challenge")
        if not isinstance(challenge, str):
            raise HTTPException(status_code=400, detail="invalid challenge")
        return {"challenge": challenge}
    if payload.get("type") != "event_callback":
        return {"ok": True, "accepted": False}
    event = payload.get("event")
    if not isinstance(event, dict):
        raise HTTPException(status_code=400, detail="invalid event")
    if event.get("subtype") == "bot_message" or event.get("bot_id"):
        return {"ok": True, "accepted": False, "reason": "bot_event"}
    if settings.slack_bot_user_id and event.get("user") == settings.slack_bot_user_id:
        return {"ok": True, "accepted": False, "reason": "self_event"}
    required = {
        "event_id": payload.get("event_id"),
        "user": event.get("user"),
        "channel": event.get("channel"),
        "text": event.get("text"),
        "event_ts": event.get("event_ts") or event.get("ts"),
    }
    if any(not isinstance(value, str) or not value for value in required.values()):
        raise HTTPException(status_code=400, detail="invalid event")
    queued = EventQueue(get_redis(settings), settings).enqueue_once(ChatEvent(**required))
    return {"ok": True, "accepted": True, "queued": queued, "duplicate": not queued}


async def handle_question(question: str) -> str:
    raise NotImplementedError("Phase 5B adds MCP-backed intent handling")
