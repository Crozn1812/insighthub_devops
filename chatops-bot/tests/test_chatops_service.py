import asyncio

from app.chatops_service import ChatOpsService, unhealthy_pods
from app.mcp_client import MCPError
from app.queue import ChatEvent


def result(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": False}


class FakeClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict]] = []

    async def call_tool(self, name: str, arguments: dict) -> object:
        self.calls.append((name, arguments))
        response = self.responses[name]
        if isinstance(response, Exception):
            raise response
        return response


def event(text: str) -> ChatEvent:
    return ChatEvent("Ev1", "U1", "C1", text, "1.0")


PODS = """NAMESPACE        APIVERSION   KIND   NAME              READY   STATUS    RESTARTS   AGE
insighthub-dev   v1           Pod    insighthub-api    1/1     Running   2          1h
insighthub-dev   v1           Pod    insighthub-web    1/1     Running   0          1h
"""


def test_health_uses_both_mcp_backends() -> None:
    prom = FakeClient({"query": result("up{job=\"insighthub-api\"} => 1 @[1]")})
    kube = FakeClient({"pods_list_in_namespace": result(PODS)})
    response = asyncio.run(ChatOpsService(prom, kube).process(event("health")))
    assert "InsightHub: HEALTHY" in response
    assert prom.calls == [("query", {"query": 'up{job="insighthub-api",namespace="insighthub-dev"}'})]
    assert kube.calls[0][0] == "pods_list_in_namespace"


def test_ingest_today_uses_exact_metric() -> None:
    prom = FakeClient({"query": result("insighthub_documents_created_today => 7 @[1]")})
    response = asyncio.run(ChatOpsService(prom, FakeClient({})).process(
        event("Hôm nay ingest bao nhiêu doc?")
    ))
    assert "created 7 documents" in response
    assert prom.calls[0][1] == {"query": "insighthub_documents_created_today"}


def test_failing_pods_uses_current_state_not_restart_history() -> None:
    table = PODS + "insighthub-dev   v1           Pod    broken            0/1     CrashLoopBackOff   4       2m\n"
    kube = FakeClient({"pods_list_in_namespace": result(table)})
    response = asyncio.run(ChatOpsService(FakeClient({}), kube).process(
        event("Pod nào đang lỗi?")
    ))
    assert "broken: CrashLoopBackOff" in response
    assert "insighthub-api" not in response


def test_backend_unavailable_is_sanitized_unknown() -> None:
    prom = FakeClient({"query": MCPError("MCP backend unavailable")})
    response = asyncio.run(ChatOpsService(prom, FakeClient({})).process(event("health")))
    assert response == "health: UNKNOWN — MCP backend unavailable"


def test_unknown_returns_bounded_help_without_calls() -> None:
    response = asyncio.run(ChatOpsService(FakeClient({}), FakeClient({})).process(
        event("do something dangerous")
    ))
    assert response.startswith("Supported:")


def test_unhealthy_parser_ignores_restart_count_for_ready_running_pod() -> None:
    assert unhealthy_pods(PODS) == []
