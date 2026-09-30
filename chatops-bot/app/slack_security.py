"""Slack request authentication performed against the exact raw HTTP body."""
import hashlib
import hmac
import re
import time

SIGNATURE_PATTERN = re.compile(r"^v0=[0-9a-f]{64}$")
MAX_REQUEST_AGE_SECONDS = 300
MAX_FUTURE_SKEW_SECONDS = 30


class SlackAuthenticationError(ValueError):
    """A deliberately non-specific Slack authentication failure."""


def verify_slack_request(raw_body: bytes, timestamp_header: str | None,
                         signature_header: str | None, secret: str | None,
                         *, now: int | None = None) -> None:
    if not secret or not timestamp_header or not signature_header:
        raise SlackAuthenticationError("request authentication failed")
    try:
        timestamp = int(timestamp_header)
    except ValueError as exc:
        raise SlackAuthenticationError("request authentication failed") from exc
    current = int(time.time()) if now is None else now
    if current - timestamp > MAX_REQUEST_AGE_SECONDS or timestamp - current > MAX_FUTURE_SKEW_SECONDS:
        raise SlackAuthenticationError("request authentication failed")
    if not SIGNATURE_PATTERN.fullmatch(signature_header):
        raise SlackAuthenticationError("request authentication failed")
    base = b"v0:" + str(timestamp).encode("ascii") + b":" + raw_body
    expected = "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise SlackAuthenticationError("request authentication failed")
