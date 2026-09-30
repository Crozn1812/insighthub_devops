import hashlib
import hmac
import json
import time

import pytest


@pytest.fixture
def secret() -> str:
    return "unit-test-signing-secret"


def signed_request(payload: dict, secret: str, *, timestamp: int | None = None) -> tuple[bytes, dict[str, str]]:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    ts = int(time.time()) if timestamp is None else timestamp
    base = b"v0:" + str(ts).encode() + b":" + raw
    signature = "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()
    return raw, {"x-slack-request-timestamp": str(ts), "x-slack-signature": signature,
                 "content-type": "application/json"}
