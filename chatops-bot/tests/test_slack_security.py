import hashlib
import hmac

import pytest

from app.slack_security import SlackAuthenticationError, verify_slack_request


def signature(body: bytes, timestamp: int, secret: str) -> str:
    base = b"v0:" + str(timestamp).encode() + b":" + body
    return "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()


def test_valid_raw_body_signature(secret: str) -> None:
    body = b'{"type":"event_callback","text":"exact bytes"}'
    verify_slack_request(body, "1000", signature(body, 1000, secret), secret, now=1001)


@pytest.mark.parametrize("timestamp,now", [(699, 1000), (1031, 1000)])
def test_replay_window_rejects_expired_and_future(timestamp: int, now: int, secret: str) -> None:
    body = b"{}"
    with pytest.raises(SlackAuthenticationError):
        verify_slack_request(body, str(timestamp), signature(body, timestamp, secret), secret, now=now)


@pytest.mark.parametrize("timestamp,signature_value,configured", [
    ("bad", "v0=" + "0" * 64, "secret"),
    ("1000", "not-a-signature", "secret"),
    ("1000", "v0=" + "0" * 64, "secret"),
    ("1000", "v0=" + "0" * 64, None),
])
def test_invalid_auth_is_rejected(timestamp: str, signature_value: str,
                                  configured: str | None) -> None:
    with pytest.raises(SlackAuthenticationError, match="request authentication failed"):
        verify_slack_request(b"{}", timestamp, signature_value, configured, now=1000)


def test_changed_body_invalidates_signature(secret: str) -> None:
    original = b'{"a":1}'
    with pytest.raises(SlackAuthenticationError):
        verify_slack_request(b'{"a":2}', "1000", signature(original, 1000, secret), secret, now=1000)
