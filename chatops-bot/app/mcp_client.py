"""Bounded official MCP stdio client and strict result shaping."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPError(RuntimeError):
    """A sanitized MCP failure safe for local transport output."""


@dataclass(frozen=True)
class MCPServer:
    command: str
    args: tuple[str, ...]
    timeout_seconds: float = 15


class MCPClient:
    def __init__(self, server: MCPServer) -> None:
        self.server = server

    async def list_tools(self) -> tuple[str, ...]:
        result = await self._run("list", None, None)
        return tuple(tool["name"] for tool in result)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return await self._run("call", name, arguments)

    async def _run(self, operation: str, name: str | None,
                   arguments: dict[str, Any] | None) -> Any:
        parameters = StdioServerParameters(command=self.server.command,
                                           args=list(self.server.args))
        try:
            async with asyncio.timeout(self.server.timeout_seconds):
                async with stdio_client(parameters) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        if operation == "list":
                            listed = await session.list_tools()
                            return tuple({"name": tool.name} for tool in listed.tools)
                        result = await session.call_tool(name, arguments or {})
                        if result.is_error:
                            raise MCPError("MCP tool returned an error")
                        return shape_mcp_result(result.model_dump(mode="json"))
        except TimeoutError as exc:
            raise MCPError("MCP call timed out") from exc
        except MCPError:
            raise
        except Exception as exc:
            raise MCPError("MCP backend unavailable or returned malformed data") from exc


SENSITIVE_KEYS = {
    "token", "authorization", "secret", "password", "clientkeydata",
    "clientcertificatedata", "env", "environment", "command", "args",
}


def shape_mcp_result(value: Any, *, depth: int = 0) -> Any:
    """Remove sensitive fields and cap untrusted MCP output size/depth."""
    if depth > 8:
        return "[truncated]"
    if isinstance(value, dict):
        return {
            str(key)[:100]: shape_mcp_result(item, depth=depth + 1)
            for key, item in list(value.items())[:100]
            if str(key).replace("_", "").lower() not in SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [shape_mcp_result(item, depth=depth + 1) for item in value[:100]]
    if isinstance(value, str):
        text = value[:20000]
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return text
        return shape_mcp_result(parsed, depth=depth + 1)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:1000]


def content_values(result: Any) -> list[Any]:
    """Return parsed values from an MCP CallToolResult's content entries."""
    entries = result.get("content", []) if isinstance(result, dict) else []
    values: list[Any] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if "text" in entry:
            values.append(shape_mcp_result(entry["text"]))
        elif "data" in entry:
            values.append(shape_mcp_result(entry["data"]))
    return values
