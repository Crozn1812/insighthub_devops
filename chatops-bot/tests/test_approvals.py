import os
import time
import uuid

from redis import Redis

from app.approvals import ApprovalGrant, ApprovalStore


def store(ttl: int = 60) -> tuple[ApprovalStore, Redis, str]:
    prefix = f"insighthub:chatops:test:approval:{uuid.uuid4().hex}"
    client = Redis.from_url(os.getenv("CHATOPS_TEST_REDIS_URL",
                                     "redis://127.0.0.1:16379/0"),
                            decode_responses=True)
    return ApprovalStore(client, prefix, ttl), client, prefix


def grant(user: str = "U1", replicas: int = 2) -> ApprovalGrant:
    return ApprovalGrant(user, "scale_deployment", {
        "namespace": "insighthub-dev", "deployment": "insighthub-api",
        "replicas": replicas,
    })


def cleanup(client: Redis, prefix: str) -> None:
    keys = list(client.scan_iter(f"{prefix}:*"))
    if keys:
        client.delete(*keys)


def test_approval_is_bound_and_single_use() -> None:
    approvals, client, prefix = store()
    try:
        token = approvals.issue(grant())
        assert approvals.consume_exact(token, grant("U2")) is False
        assert approvals.consume_exact(token, grant(replicas=3)) is False
        assert approvals.consume_exact(token, grant()) is True
        assert approvals.consume_exact(token, grant()) is False
    finally:
        cleanup(client, prefix)


def test_approval_expires() -> None:
    approvals, client, prefix = store(ttl=1)
    try:
        token = approvals.issue(grant())
        time.sleep(1.1)
        assert approvals.get(token) is None
        assert approvals.consume_exact(token, grant()) is False
    finally:
        cleanup(client, prefix)
