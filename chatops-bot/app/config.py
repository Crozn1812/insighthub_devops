"""Environment-backed settings for the local Day 5 ChatOps runtime."""
from dataclasses import dataclass
import json
import os


@dataclass(frozen=True)
class Settings:
    slack_signing_secret: str | None
    slack_bot_user_id: str | None
    redis_url: str
    queue_key: str
    dedup_prefix: str
    retry_key: str
    result_key: str
    dedup_ttl_seconds: int
    max_attempts: int
    retry_base_seconds: float
    transport: str
    prometheus_mcp_command: str | None = None
    prometheus_mcp_args: tuple[str, ...] = ()
    kubernetes_mcp_command: str | None = None
    kubernetes_mcp_args: tuple[str, ...] = ()
    mcp_timeout_seconds: float = 15
    approval_prefix: str = "insighthub:chatops:approval"
    approval_ttl_seconds: int = 60
    mutator_kubeconfig: str | None = None
    kubectl_command: str = "kubectl"

    @classmethod
    def from_env(cls) -> "Settings":
        queue_key = os.getenv("CHATOPS_QUEUE_KEY", "insighthub:chatops:events")
        return cls(
            slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
            slack_bot_user_id=os.getenv("SLACK_BOT_USER_ID"),
            redis_url=os.getenv(
                "REDIS_URL",
                os.getenv("CHATOPS_REDIS_URL", "redis://127.0.0.1:16379/0"),
            ),
            queue_key=queue_key,
            dedup_prefix=os.getenv("CHATOPS_DEDUP_PREFIX", "insighthub:chatops:dedup"),
            retry_key=os.getenv("CHATOPS_RETRY_KEY", "insighthub:chatops:retry"),
            result_key=os.getenv("CHATOPS_RESULT_KEY", f"{queue_key}:results"),
            dedup_ttl_seconds=int(os.getenv("CHATOPS_DEDUP_TTL_SECONDS", "86400")),
            max_attempts=int(os.getenv("CHATOPS_MAX_ATTEMPTS", "3")),
            retry_base_seconds=float(os.getenv("CHATOPS_RETRY_BASE_SECONDS", "1")),
            transport=os.getenv("CHATOPS_TRANSPORT", "local"),
            prometheus_mcp_command=os.getenv("PROMETHEUS_MCP_COMMAND"),
            prometheus_mcp_args=_json_args("PROMETHEUS_MCP_ARGS"),
            kubernetes_mcp_command=os.getenv("KUBERNETES_MCP_COMMAND"),
            kubernetes_mcp_args=_json_args("KUBERNETES_MCP_ARGS"),
            mcp_timeout_seconds=float(os.getenv("MCP_TIMEOUT_SECONDS", "15")),
            approval_prefix=os.getenv(
                "CHATOPS_APPROVAL_PREFIX", "insighthub:chatops:approval"
            ),
            approval_ttl_seconds=int(os.getenv("CHATOPS_APPROVAL_TTL_SECONDS", "60")),
            mutator_kubeconfig=os.getenv("CHATOPS_MUTATOR_KUBECONFIG"),
            kubectl_command=os.getenv("KUBECTL_COMMAND", "kubectl"),
        )


def _json_args(name: str) -> tuple[str, ...]:
    value = os.getenv(name, "[]")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must be a JSON string array") from exc
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError(f"{name} must be a JSON string array")
    return tuple(parsed)
