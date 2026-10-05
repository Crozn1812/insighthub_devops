from dataclasses import replace

import httpx
import pytest

from app.config import Settings
from app.model_summary import summarize
from app.queue import ChatEvent
from app.transport import SlackTransport


def settings():
    return Settings(None, None, "redis://unused", "q", "d", "r", "out",
                    86400, 3, 0.5, "local")


def test_live_transport_requires_credentials():
    with pytest.raises(ValueError, match="token required"):
        SlackTransport("")


def test_slack_delivery_retains_channel_and_thread(monkeypatch):
    calls = []
    monkeypatch.setattr("slack_sdk.WebClient.chat_postMessage",
                        lambda self, **kwargs: calls.append(kwargs))
    SlackTransport("synthetic-test-credential").send(
        ChatEvent("E", "U", "C", "status", "123.4"), "Ready")
    assert calls == [{"channel": "C", "text": "Ready", "thread_ts": "123.4"}]


def test_gateway_failure_preserves_authoritative_facts(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ConnectError("synthetic private response")
    monkeypatch.setattr(httpx.Client, "post", fail)
    configured = replace(settings(), model_url="http://example.invalid/v1",
                         model_key="synthetic-test-credential")
    assert summarize("pods_ready=3", configured) == "pods_ready=3\nAI summary unavailable."


def test_unconfigured_model_does_not_send_request(monkeypatch):
    monkeypatch.setattr(httpx.Client, "post", lambda *a, **k: pytest.fail("HTTP call"))
    assert summarize("pods_ready=3", settings()) == "pods_ready=3"


@pytest.mark.parametrize("block_phase", ["input", "output"])
def test_guard_blocks_summary_without_changing_facts(monkeypatch, block_phase):
    calls = []
    def respond(self, url, **kwargs):
        calls.append(url)
        payload = ({"allowed": kwargs["json"]["phase"] != block_phase}
                   if url.endswith("/check") else
                   {"choices": [{"message": {"content": '{"summary":"Observed pods ready."}'}}]})
        return httpx.Response(200, json=payload, request=httpx.Request("POST", url))
    monkeypatch.setattr(httpx.Client, "post", respond)
    configured = replace(settings(), model_url="http://example.invalid/v1", model_key="synthetic",
                         guard_url="http://guard.invalid", guard_key="synthetic")
    assert summarize("pods_ready=3", configured) == "pods_ready=3\nAI summary unavailable."
    assert len(calls) == (1 if block_phase == "input" else 3)
