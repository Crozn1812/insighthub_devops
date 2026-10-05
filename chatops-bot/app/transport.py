"""Explicit local capture or authenticated real Slack delivery."""
import json
from typing import Protocol

from redis import Redis

from .queue import ChatEvent


class ResultTransport(Protocol):
    def send(self, event: ChatEvent, result: str, *, status: str = "ok") -> None: ...


class NullTransport:
    def send(self, event: ChatEvent, result: str, *, status: str = "ok") -> None:
        return None


class CaptureTransport:
    def __init__(self, client: Redis, result_key: str) -> None:
        self.client = client
        self.result_key = result_key

    def send(self, event: ChatEvent, result: str, *, status: str = "ok") -> None:
        record = {"event_id": event.event_id, "channel": event.channel,
                  "status": status, "result": result, "attempt": event.attempt}
        self.client.rpush(self.result_key, json.dumps(record, separators=(",", ":")))


class SlackTransport:
    def __init__(self, token: str) -> None:
        from slack_sdk import WebClient

        if not token:
            raise ValueError("Slack token required for live transport")
        self.client = WebClient(token=token, timeout=15, retry_handlers=[])

    def send(self, event: ChatEvent, result: str, *, status: str = "ok") -> None:
        from slack_sdk.errors import SlackApiError

        try:
            self.client.chat_postMessage(channel=event.channel, text=result[:3500],
                                         thread_ts=event.event_ts)
        except (SlackApiError, OSError):
            # SDK exception strings can contain response details; sanitize completely.
            raise RuntimeError("Slack delivery unavailable") from None
