"""Fail-closed action policy for Day 5 ChatOps."""
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .audit import record_action_decision


class Decision(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    APPROVAL_REQUIRED = "approval_required"


READ_ACTIONS = {"health", "ingest_today", "failing_pods"}
DESTRUCTIVE_ACTIONS = {"delete_pod", "delete_deployment", "delete_namespace"}
SCALE_ACTION = "scale_deployment"


@dataclass(frozen=True)
class PermissionDecision:
    action: str
    decision: Decision
    reason: str
    normalized_arguments: dict[str, Any]


def decide(action: str, arguments: dict[str, Any] | None = None) -> PermissionDecision:
    arguments = arguments or {}
    if action in READ_ACTIONS:
        return PermissionDecision(action, Decision.ALLOWED, "read-only action", {})
    if action in DESTRUCTIVE_ACTIONS:
        return PermissionDecision(action, Decision.DENIED,
                                  "destructive actions are not permitted", {})
    if action == SCALE_ACTION:
        replicas = arguments.get("replicas")
        expected = {
            "namespace": "insighthub-dev",
            "deployment": "insighthub-api",
            "replicas": replicas,
        }
        valid = (
            type(replicas) is int
            and 1 <= replicas <= 5
            and arguments.get("namespace") == "insighthub-dev"
            and arguments.get("deployment") == "insighthub-api"
            and set(arguments) == {"namespace", "deployment", "replicas"}
        )
        if valid:
            return PermissionDecision(action, Decision.APPROVAL_REQUIRED,
                                      "write action requires exact approval", expected)
        return PermissionDecision(action, Decision.DENIED,
                                  "scale target or replica count is outside policy", {})
    return PermissionDecision(action, Decision.DENIED, "unknown action", {})


class PermissionEngine:
    def authorize(self, event_id: str, user: str, action: str,
                  arguments: dict[str, Any] | None = None) -> PermissionDecision:
        result = decide(action, arguments)
        record_action_decision(event_id, action, result.decision.value, user,
                               arguments_summary=result.normalized_arguments)
        return result
