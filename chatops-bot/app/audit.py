"""
InsightHub ChatOps Bot — Audit log (SKELETON)

Mọi tool call của bot PHẢI được ghi audit. Đây là yêu cầu bảo mật cốt lõi:
khi AI agent có quyền chạm vào hạ tầng, phải có dấu vết kiểm toán.

TODO Day 5: hoàn thiện theo gợi ý dưới.
"""
import json
import logging
import os
from pathlib import Path
import threading
import uuid
from datetime import datetime, timezone

logger = logging.getLogger("chatops-bot.audit")
_write_lock = threading.Lock()


def record_action_decision(
    event_id: str,
    action: str,
    decision: str,
    user: str,
    *,
    arguments_summary: dict | None = None,
    tool: str | None = None,
    result_summary: str | None = None,
    approval_id: str | None = None,
    attempt: int = 0,
    transport: str = "local",
) -> dict:
    """Create a verifier-compatible audit event and optionally persist it."""
    run_id = (os.getenv("INSIGHTHUB_VERIFY_RUN_ID")
              or os.getenv("CHATOPS_TEST_RUN_ID") or "local-runtime")
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_id": event_id[:200],
        "action": action[:100],
        "decision": decision,
        "user": user[:200],
        "test_run_id": run_id,
        "intent": action[:100],
        "arguments_summary": arguments_summary or {},
        "attempt": attempt,
        "transport": transport,
    }
    if tool:
        record["tool"] = tool[:100]
    if result_summary:
        record["result_summary"] = result_summary[:500]
    if approval_id:
        record["approval_id"] = approval_id[:64]
    logger.info("ACTION_AUDIT %s", json.dumps(record, ensure_ascii=False))
    destination = (os.getenv("INSIGHTHUB_VERIFY_OBSERVATIONS")
                   or os.getenv("CHATOPS_AUDIT_PATH"))
    if destination:
        _append_observation(Path(destination), run_id, record)
    return record


def _append_observation(path: Path, run_id: str, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock:
        data = {"run_id": run_id, "events": []}
        if path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if loaded.get("run_id") == run_id and isinstance(loaded.get("events"), list):
                    data = loaded
            except (OSError, UnicodeError, json.JSONDecodeError):
                pass
        data["events"].append(record)
        temporary = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        os.replace(temporary, path)


def log_mcp_call(event_id: str, intent: str, backend: str, tool: str,
                 result_summary: str, success: bool) -> None:
    """Emit bounded structured metadata; never include raw MCP responses."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_id": event_id[:200],
        "intent": intent[:50],
        "mcp_backend": backend[:50],
        "tool": tool[:100],
        "result_summary": result_summary[:500],
        "success": success,
    }
    logger.info("MCP_AUDIT %s", json.dumps(record, ensure_ascii=False))


def log_tool_call(
    user: str,
    tool: str,
    args: dict,
    result_summary: str,
    approved: bool = True,
) -> None:
    """
    Ghi 1 dòng audit cho mỗi tool call.

    TODO Day 5:
    - Ghi ra file hoặc stdout dạng structured JSON (mỗi dòng 1 record).
    - Trong production thật: đẩy sang log aggregator (Loki...).
    - Trường tối thiểu: timestamp, user, tool, args, kết quả, approved.

    Ví dụ record:
      {"ts": "...", "user": "U123", "tool": "kubectl_get_pods",
       "args": {...}, "result": "5 pods Running", "approved": true}
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "tool": tool,
        "args": args,
        "result": result_summary,
        "approved": approved,
    }
    # TODO: thay bằng ghi file / gửi log aggregator
    logger.info("AUDIT %s", json.dumps(record, ensure_ascii=False))
