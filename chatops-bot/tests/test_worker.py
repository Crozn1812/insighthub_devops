from app.config import Settings
from app.queue import ChatEvent
from app.worker import TransientProcessingError, Worker
from app import worker as worker_module


class FakeQueue:
    def __init__(self) -> None:
        self.retries: list[tuple[ChatEvent, float]] = []

    def schedule_retry(self, event: ChatEvent, delay: float) -> None:
        self.retries.append((event, delay))


class Capture:
    def __init__(self) -> None:
        self.records: list[tuple[str, str]] = []

    def send(self, _event: ChatEvent, result: str, *, status: str = "ok") -> None:
        self.records.append((status, result))


def settings() -> Settings:
    return Settings("secret", None, "redis://unused", "q", "d", "r", "out",
                    86400, 3, 0.5, "local")


def event(attempt: int = 0) -> ChatEvent:
    return ChatEvent("Ev1", "U1", "C1", "hello", "1.0", attempt)


def test_success_is_captured(monkeypatch) -> None:
    queue, capture = FakeQueue(), Capture()
    monkeypatch.setattr(worker_module, "process_event",
                        lambda _event: "LOCAL_ACK event=Ev1 text_length=5")
    assert Worker(queue, capture, settings()).handle(event()) == "ok"
    assert capture.records == [("ok", "LOCAL_ACK event=Ev1 text_length=5")]


def test_transient_failure_schedules_exponential_retry(monkeypatch) -> None:
    queue, capture = FakeQueue(), Capture()
    monkeypatch.setattr(worker_module, "process_event",
                        lambda _event: (_ for _ in ()).throw(TransientProcessingError()))
    assert Worker(queue, capture, settings()).handle(event(1)) == "retry"
    assert queue.retries == [(event(2), 1.0)]
    assert capture.records == []


def test_retry_limit_is_bounded(monkeypatch) -> None:
    queue, capture = FakeQueue(), Capture()
    monkeypatch.setattr(worker_module, "process_event",
                        lambda _event: (_ for _ in ()).throw(TransientProcessingError()))
    assert Worker(queue, capture, settings()).handle(event(2)) == "failed"
    assert queue.retries == []
    assert capture.records == [("failed", "retry limit reached")]
