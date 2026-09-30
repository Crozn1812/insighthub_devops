"""Read-only MCP-backed implementations of the Day 5 ChatOps intents."""
from __future__ import annotations

import logging
import re
from typing import Any, Protocol

from .audit import log_mcp_call
from .config import Settings
from .intents import HELP_TEXT, Intent, classify_intent
from .mcp_client import MCPClient, MCPError, MCPServer, content_values
from .queue import ChatEvent

logger = logging.getLogger("chatops-bot.service")


class ToolClient(Protocol):
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...


def clients_from_settings(settings: Settings) -> tuple[MCPClient, MCPClient]:
    if not settings.prometheus_mcp_command or not settings.kubernetes_mcp_command:
        raise MCPError("MCP runtime is not configured")
    prometheus = MCPClient(MCPServer(settings.prometheus_mcp_command,
                                     settings.prometheus_mcp_args,
                                     settings.mcp_timeout_seconds))
    kubernetes = MCPClient(MCPServer(settings.kubernetes_mcp_command,
                                     settings.kubernetes_mcp_args,
                                     settings.mcp_timeout_seconds))
    return prometheus, kubernetes


def _text(result: Any) -> str:
    pieces: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            pieces.append(value)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for value in content_values(result):
        walk(value)
    return "\n".join(pieces)[:20000]


def unhealthy_pods(table: str) -> list[tuple[str, str]]:
    unhealthy: list[tuple[str, str]] = []
    for line in table.splitlines():
        if not line.strip() or line.lstrip().startswith("NAMESPACE"):
            continue
        columns = re.split(r"\s{2,}", line.strip())
        if len(columns) < 6 or columns[2] != "Pod":
            continue
        name, ready, status = columns[3], columns[4], columns[5]
        try:
            ready_count, total_count = (int(value) for value in ready.split("/", 1))
        except (ValueError, TypeError):
            ready_count, total_count = 0, 1
        if status not in {"Running", "Succeeded"} or ready_count != total_count:
            unhealthy.append((name[:253], status[:100]))
    return unhealthy


class ChatOpsService:
    def __init__(self, prometheus: ToolClient, kubernetes: ToolClient) -> None:
        self.prometheus = prometheus
        self.kubernetes = kubernetes

    async def process(self, event: ChatEvent) -> str:
        intent = classify_intent(event.text)
        if intent is Intent.UNKNOWN:
            return HELP_TEXT
        try:
            if intent is Intent.HEALTH:
                return await self._health(event)
            if intent is Intent.INGEST_TODAY:
                return await self._ingest_today(event)
            return await self._failing_pods(event)
        except MCPError as exc:
            log_mcp_call(event.event_id, intent.value, "mcp", "unavailable",
                         "backend unavailable", False)
            return f"{intent.value}: UNKNOWN — {exc}"

    async def _health(self, event: ChatEvent) -> str:
        query = 'up{job="insighthub-api",namespace="insighthub-dev"}'
        prometheus_result = await self.prometheus.call_tool("query", {"query": query})
        pods_result = await self.kubernetes.call_tool(
            "pods_list_in_namespace", {"namespace": "insighthub-dev"}
        )
        prom_text, pods_text = _text(prometheus_result), _text(pods_result)
        api_up = bool(re.search(r"=>\s*1(?:\.0+)?(?:\s|@|$)", prom_text))
        pod_rows = [line for line in pods_text.splitlines()
                    if line.strip() and not line.lstrip().startswith("NAMESPACE")]
        unhealthy = unhealthy_pods(pods_text)
        healthy = api_up and not unhealthy and bool(pod_rows)
        summary = f"api_up={api_up}, workloads={len(pod_rows)}, unhealthy={len(unhealthy)}"
        log_mcp_call(event.event_id, Intent.HEALTH.value, "prometheus", "query", summary, True)
        log_mcp_call(event.event_id, Intent.HEALTH.value, "kubernetes",
                     "pods_list_in_namespace", summary, True)
        state = "HEALTHY" if healthy else "DEGRADED"
        return (f"InsightHub: {state}\n- API metrics target: {'UP' if api_up else 'DOWN/UNKNOWN'}\n"
                f"- workloads observed: {len(pod_rows)}\n- unhealthy pods: {len(unhealthy)}")

    async def _ingest_today(self, event: ChatEvent) -> str:
        result = await self.prometheus.call_tool(
            "query", {"query": "insighthub_documents_created_today"}
        )
        text = _text(result)
        match = re.search(r"=>\s*(-?\d+(?:\.\d+)?)", text)
        if match is None:
            raise MCPError("ingest-today metric unavailable")
        value = int(float(match.group(1)))
        log_mcp_call(event.event_id, Intent.INGEST_TODAY.value, "prometheus", "query",
                     f"documents_created_today={value}", True)
        return (f"Today (Asia/Ho_Chi_Minh), InsightHub has created {value} "
                "documents since local midnight.")

    async def _failing_pods(self, event: ChatEvent) -> str:
        result = await self.kubernetes.call_tool(
            "pods_list_in_namespace", {"namespace": "insighthub-dev"}
        )
        unhealthy = unhealthy_pods(_text(result))
        log_mcp_call(event.event_id, Intent.FAILING_PODS.value, "kubernetes",
                     "pods_list_in_namespace", f"unhealthy={len(unhealthy)}", True)
        if not unhealthy:
            return "No unhealthy pods in insighthub-dev."
        lines = [f"- {name}: {status}" for name, status in unhealthy[:20]]
        return "Unhealthy pods:\n" + "\n".join(lines)
