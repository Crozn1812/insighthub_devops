from fastapi.testclient import TestClient

from app.config import Settings
from app import main
from conftest import signed_request


class FakeRedis:
    def __init__(self) -> None:
        self.ids: set[str] = set()
        self.items: list[str] = []
        self.available = True

    def ping(self) -> bool:
        return self.available

    def eval(self, _script: str, _keys: int, dedup: str, _queue: str,
             _ttl: int, payload: str) -> int:
        if dedup in self.ids:
            return 0
        self.ids.add(dedup)
        self.items.append(payload)
        return 1


def settings(secret: str) -> Settings:
    return Settings(secret, "UBOT", "redis://unused", "test:events", "test:dedup",
                    "test:retry", "test:results", 86400, 3, 0.01, "local")


def client(monkeypatch, secret: str) -> tuple[TestClient, FakeRedis]:
    fake = FakeRedis()
    monkeypatch.setattr(main, "get_settings", lambda: settings(secret))
    monkeypatch.setattr(main, "get_redis", lambda _settings: fake)
    return TestClient(main.app), fake


def message(event_id: str = "Ev1", user: str = "U1") -> dict:
    return {"type": "event_callback", "event_id": event_id,
            "event": {"type": "message", "user": user, "channel": "C1",
                      "text": "status", "event_ts": "1.000"}}


def test_health_ready(monkeypatch, secret: str) -> None:
    http, _ = client(monkeypatch, secret)
    assert http.get("/healthz").json() == {
        "status": "ok", "ready": True, "transport": "local",
        "redis": "ok", "queue": "ready",
    }


def test_invalid_signature_gets_401_before_json(monkeypatch, secret: str) -> None:
    http, _ = client(monkeypatch, secret)
    response = http.post("/slack/events", content=b"not-json")
    assert response.status_code == 401
    assert response.json() == {"detail": "request authentication failed"}


def test_authenticated_url_challenge(monkeypatch, secret: str) -> None:
    http, _ = client(monkeypatch, secret)
    raw, headers = signed_request({"type": "url_verification", "challenge": "abc"}, secret)
    response = http.post("/slack/events", content=raw, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"challenge": "abc"}


def test_event_is_enqueued_once(monkeypatch, secret: str) -> None:
    http, fake = client(monkeypatch, secret)
    raw, headers = signed_request(message(), secret)
    first = http.post("/slack/events", content=raw, headers=headers)
    second = http.post("/slack/events", content=raw, headers=headers)
    assert first.json()["queued"] is True
    assert second.json()["duplicate"] is True
    assert len(fake.items) == 1


def test_self_and_bot_events_are_ignored(monkeypatch, secret: str) -> None:
    http, fake = client(monkeypatch, secret)
    for payload in (message(user="UBOT"),
                    {**message(), "event": {**message()["event"], "bot_id": "B1"}}):
        raw, headers = signed_request(payload, secret)
        assert http.post("/slack/events", content=raw, headers=headers).json()["accepted"] is False
    assert fake.items == []


def test_invalid_authenticated_event_gets_400(monkeypatch, secret: str) -> None:
    http, _ = client(monkeypatch, secret)
    raw, headers = signed_request({"type": "event_callback", "event_id": "Ev1", "event": {}}, secret)
    assert http.post("/slack/events", content=raw, headers=headers).status_code == 400
