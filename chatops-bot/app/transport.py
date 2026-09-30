"""Local-only result transports for Phase 5A."""
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
