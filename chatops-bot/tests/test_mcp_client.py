import asyncio
import sys

import pytest

from app.mcp_client import MCPClient, MCPError, MCPServer, shape_mcp_result


def test_timeout_is_bounded() -> None:
    client = MCPClient(MCPServer(sys.executable, ("-c", "import time; time.sleep(2)"), 0.1))
    with pytest.raises(MCPError, match="timed out"):
        asyncio.run(client.list_tools())


def test_malformed_protocol_is_sanitized() -> None:
    client = MCPClient(MCPServer(sys.executable, ("-c", "print('not-json')"), 1))
    with pytest.raises(MCPError, match="malformed"):
        asyncio.run(client.list_tools())


def test_backend_unavailable_is_sanitized() -> None:
    client = MCPClient(MCPServer("definitely-missing-day5-command", (), 1))
    with pytest.raises(MCPError, match="unavailable"):
        asyncio.run(client.list_tools())


def test_sensitive_fields_and_size_are_removed() -> None:
    shaped = shape_mcp_result({
        "name": "pod", "token": "do-not-leak", "environment": {"A": "secret"},
        "nested": {"authorization": "Bearer hidden", "safe": "x" * 30000},
    })
    rendered = repr(shaped)
    assert "do-not-leak" not in rendered
    assert "Bearer hidden" not in rendered
    assert len(shaped["nested"]["safe"]) == 20000
