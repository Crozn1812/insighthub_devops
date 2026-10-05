"""Day 5 verifier contract tests using real application security logic."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import sys
import time
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from redis import Redis

REPO = Path(os.environ["INSIGHTHUB_REPO_ROOT"])
sys.path.insert(0, str(REPO / "chatops-bot"))

from app.approvals import ApprovalGrant, ApprovalStore  # noqa: E402
from app.config import Settings  # noqa: E402
from app.main import app  # noqa: E402
from app.permissions import Decision, PermissionEngine  # noqa: E402
from app.queue import ChatEvent, EventQueue  # noqa: E402


def redis_client() -> Redis:
    return Redis.from_url(os.getenv("CHATOPS_TEST_REDIS_URL",
                                    "redis://127.0.0.1:16379/0"),
                          decode_responses=True)


def scale_arguments(replicas: int = 2) -> dict:
    return {"namespace": "insighthub-dev", "deployment": "insighthub-api",
            "replicas": replicas}


def test_permission_denied() -> None:
    executor_calls: list[str] = []
    result = PermissionEngine().authorize("verify-denied", "U_VERIFY",
                                          "delete_namespace", {})
    if result.decision is Decision.ALLOWED:
        executor_calls.append("unexpected")
    assert result.decision is Decision.DENIED
    assert executor_calls == []


def test_approval_required() -> None:
    executor_calls: list[str] = []
    result = PermissionEngine().authorize("verify-approval", "U_VERIFY",
                                          "scale_deployment", scale_arguments())
    if result.decision is Decision.ALLOWED:
        executor_calls.append("unexpected")
    assert result.decision is Decision.APPROVAL_REQUIRED
    assert executor_calls == []


def test_approval_bound_to_action() -> None:
    client = redis_client()
    prefix = f"insighthub:chatops:verify:approval:{uuid.uuid4().hex}"
    approvals = ApprovalStore(client, prefix, ttl_seconds=60)
    exact = ApprovalGrant("U_VERIFY", "scale_deployment", scale_arguments())
    token = approvals.issue(exact)
    try:
        assert not approvals.consume_exact(
            token, ApprovalGrant("U_OTHER", "scale_deployment", scale_arguments())
        )
        assert not approvals.consume_exact(
            token, ApprovalGrant("U_VERIFY", "scale_deployment", scale_arguments(3))
        )
        assert not approvals.consume_exact(
            token, ApprovalGrant("U_VERIFY", "delete_deployment", scale_arguments())
        )
        assert approvals.consume_exact(token, exact)
        assert not approvals.consume_exact(token, exact)
    finally:
        keys = list(client.scan_iter(f"{prefix}:*"))
        if keys:
            client.delete(*keys)


def test_duplicate_event() -> None:
    client = redis_client()
    root = f"insighthub:chatops:verify:queue:{uuid.uuid4().hex}"
    settings = Settings(
        "verify-only", None, "redis://127.0.0.1:16379/0",
        f"{root}:events", f"{root}:dedup", f"{root}:retry", f"{root}:results",
        60, 3, 0.01, "local",
    )
    queue = EventQueue(client, settings)
    event = ChatEvent("verify-duplicate", "U_VERIFY", "C_VERIFY", "health", "1.0")
    try:
        assert queue.enqueue_once(event)
        assert not queue.enqueue_once(event)
        assert queue.dequeue(timeout=1) == event
        assert queue.dequeue(timeout=1) is None
    finally:
        keys = list(client.scan_iter(f"{root}:*"))
        if keys:
            client.delete(*keys)


def test_invalid_signature() -> None:
    secret = "verifier-local-only-secret"
    body = json.dumps({"type": "event_callback", "event_id": "verify-signature",
                       "event": {"user": "U_VERIFY", "channel": "C_VERIFY",
                                 "text": "health", "event_ts": "1.0"}},
                      separators=(",", ":")).encode()
    timestamp = str(int(time.time()))
    wrong = "v0=" + hmac.new(secret.encode(),
                              b"v0:" + timestamp.encode() + b":" + body + b"changed",
                              hashlib.sha256).hexdigest()
    with patch("app.main.get_redis", side_effect=AssertionError("must not enqueue")):
        with patch.dict(os.environ, {"SLACK_SIGNING_SECRET": secret}):
            response = TestClient(app).post(
                "/slack/events", content=body,
                headers={"X-Slack-Request-Timestamp": timestamp,
                         "X-Slack-Signature": wrong,
                         "Content-Type": "application/json"},
            )
    assert response.status_code == 401
    assert secret not in response.text
