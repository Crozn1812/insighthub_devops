"""Redis-backed durable event queue, atomic deduplication, and retry schedule."""
import json
import time
from dataclasses import asdict, dataclass

from redis import Redis

from .config import Settings

ENQUEUE_ONCE = """
if redis.call('SET', KEYS[1], '1', 'NX', 'EX', ARGV[1]) then
  redis.call('RPUSH', KEYS[2], ARGV[2])
  return 1
end
return 0
"""

PROMOTE_RETRY = """
if redis.call('ZREM', KEYS[1], ARGV[1]) == 1 then
  redis.call('RPUSH', KEYS[2], ARGV[1])
  return 1
end
return 0
"""


@dataclass(frozen=True)
class ChatEvent:
    event_id: str
    user: str
    channel: str
    text: str
    event_ts: str
    attempt: int = 0


class EventQueue:
    def __init__(self, client: Redis, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def enqueue_once(self, event: ChatEvent) -> bool:
        payload = json.dumps(asdict(event), separators=(",", ":"), ensure_ascii=False)
        result = self.client.eval(ENQUEUE_ONCE, 2,
                                  f"{self.settings.dedup_prefix}:{event.event_id}",
                                  self.settings.queue_key,
                                  self.settings.dedup_ttl_seconds, payload)
        return bool(result)

    def dequeue(self, timeout: int = 1) -> ChatEvent | None:
        item = self.client.blmove(self.settings.queue_key, self.pending_key,
                                  timeout, src="LEFT", dest="RIGHT")
        return None if item is None else ChatEvent(**json.loads(item))

    @property
    def pending_key(self) -> str:
        return self.settings.queue_key + ":processing"

    def acknowledge(self, event: ChatEvent) -> None:
        payload = json.dumps(asdict(event), separators=(",", ":"), ensure_ascii=False)
        self.client.lrem(self.pending_key, 1, payload)

    def recover_pending(self) -> int:
        # Called only while holding the single-consumer lease.
        count = 0
        while self.client.lmove(self.pending_key, self.settings.queue_key,
                                src="RIGHT", dest="LEFT") is not None:
            count += 1
        return count

    def result(self, event: ChatEvent) -> str | None:
        return self.client.get(self.settings.dedup_prefix + ":result:" + event.event_id)

    def save_result(self, event: ChatEvent, result: str) -> None:
        self.client.set(self.settings.dedup_prefix + ":result:" + event.event_id,
                        result, ex=self.settings.dedup_ttl_seconds)

    def dead_letter(self, event: ChatEvent) -> None:
        self.client.rpush(self.settings.queue_key + ":failed",
                          json.dumps(asdict(event), separators=(",", ":"), ensure_ascii=False))

    def schedule_retry(self, event: ChatEvent, delay_seconds: float) -> None:
        payload = json.dumps(asdict(event), separators=(",", ":"), ensure_ascii=False)
        self.client.zadd(self.settings.retry_key, {payload: time.time() + delay_seconds})

    def promote_due_retries(self, *, now: float | None = None) -> int:
        due = self.client.zrangebyscore(self.settings.retry_key, "-inf",
                                        time.time() if now is None else now)
        moved = 0
        for payload in due:
            moved += int(self.client.eval(PROMOTE_RETRY, 2, self.settings.retry_key,
                                          self.settings.queue_key, payload))
        return moved
