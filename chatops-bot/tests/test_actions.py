import asyncio
import os
import uuid

from redis import Redis

from app.actions import ActionController, route_action
from app.approvals import ApprovalStore
from app.permissions import PermissionEngine
from app.queue import ChatEvent


class FakeExecutor:
    def __init__(self) -> None:
        self.replicas: list[int] = []

    def scale_api(self, replicas: int) -> None:
        self.replicas.append(replicas)


class FakeReads:
    async def process(self, _event: ChatEvent) -> str:
        return "read-result"


def event(text: str, user: str = "U1", event_id: str = "Ev1") -> ChatEvent:
    return ChatEvent(event_id, user, "C1", text, "1.0")


def controller() -> tuple[ActionController, FakeExecutor, Redis, str]:
    prefix = f"insighthub:chatops:test:actions:{uuid.uuid4().hex}"
    client = Redis.from_url(os.getenv("CHATOPS_TEST_REDIS_URL",
                                     "redis://127.0.0.1:16379/0"),
                            decode_responses=True)
    executor = FakeExecutor()
    value = ActionController(PermissionEngine(), ApprovalStore(client, prefix),
                             executor, FakeReads())
    return value, executor, client, prefix


def token_from(response: str) -> str:
    return response.removeprefix("approval_required: confirm ")


def test_scale_requires_confirmation_and_wrong_user_does_not_consume() -> None:
    actions, executor, client, prefix = controller()
    try:
        response = asyncio.run(actions.process(event("scale api to 2")))
        token = token_from(response)
        assert executor.replicas == []
        denied = asyncio.run(actions.process(event(f"confirm {token}", user="U2")))
        assert denied.startswith("denied:")
        allowed = asyncio.run(actions.process(event(f"confirm {token}", event_id="Ev3")))
        assert allowed.startswith("allowed:")
        assert executor.replicas == [2]
        reused = asyncio.run(actions.process(event(f"confirm {token}", event_id="Ev4")))
        assert reused.startswith("denied:")
        assert executor.replicas == [2]
    finally:
        keys = list(client.scan_iter(f"{prefix}:*"))
        if keys:
            client.delete(*keys)


def test_destructive_text_is_denied_without_executor() -> None:
    actions, executor, client, prefix = controller()
    try:
        response = asyncio.run(actions.process(event("delete namespace")))
        assert response.startswith("denied:")
        assert executor.replicas == []
    finally:
        keys = list(client.scan_iter(f"{prefix}:*"))
        if keys:
            client.delete(*keys)


def test_router_only_accepts_fixed_scale_target() -> None:
    assert route_action("scale api to 3").arguments["replicas"] == 3
    assert route_action("scale worker to 3").action == "unknown"
