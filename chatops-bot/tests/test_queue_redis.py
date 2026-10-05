"""Small integration checks against the isolated local Redis port-forward."""
import os
import time
import uuid

from redis import Redis

from app.config import Settings
from app.queue import ChatEvent, EventQueue


def isolated_queue() -> tuple[EventQueue, Redis, list[str]]:
    suffix = uuid.uuid4().hex
    root = f"insighthub:chatops:test:{suffix}"
    settings = Settings(
        "test-only", None,
        os.getenv("CHATOPS_TEST_REDIS_URL", "redis://127.0.0.1:16379/0"),
        f"{root}:events", f"{root}:dedup", f"{root}:retry", f"{root}:results",
        60, 3, 0.01, "local",
    )
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    return EventQueue(client, settings), client, [settings.queue_key, settings.retry_key,
                                                   queue_processing_key(settings.queue_key),
                                                   f"{settings.dedup_prefix}:Ev1"]


def queue_processing_key(key: str) -> str:
    return key + ":processing"


def test_queue_state_survives_queue_object_restart() -> None:
    queue, client, keys = isolated_queue()
    event = ChatEvent("Ev1", "U1", "C1", "hello", "1.0")
    try:
        assert queue.enqueue_once(event) is True
        restarted = EventQueue(client, queue.settings)
        assert restarted.enqueue_once(event) is False
        assert restarted.dequeue(timeout=1) == event
    finally:
        client.delete(*keys)


def test_retry_metadata_is_durable_and_promoted() -> None:
    queue, client, keys = isolated_queue()
    retry = ChatEvent("Ev1", "U1", "C1", "hello", "1.0", attempt=1)
    try:
        queue.schedule_retry(retry, 0)
        restarted = EventQueue(client, queue.settings)
        assert restarted.promote_due_retries(now=time.time() + 1) == 1
        assert restarted.dequeue(timeout=1) == retry
    finally:
        client.delete(*keys)


def test_worker_crash_recovers_unacknowledged_event_without_duplicate_enqueue() -> None:
    queue, client, keys = isolated_queue()
    ev = ChatEvent("Ev1", "U1", "C1", "hello", "1.0")
    try:
        assert queue.enqueue_once(ev)
        assert queue.dequeue(timeout=1) == ev
        restarted = EventQueue(client, queue.settings)
        assert restarted.recover_pending() == 1
        assert restarted.dequeue(timeout=1) == ev
        restarted.acknowledge(ev)
        assert restarted.recover_pending() == 0
        assert client.llen(queue.pending_key) == 0
    finally:
        client.delete(*keys)
