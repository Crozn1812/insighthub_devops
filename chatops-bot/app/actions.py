"""Fixed action parsing and approval-controlled execution."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .approvals import ApprovalGrant, ApprovalStore
from .audit import record_action_decision
from .chatops_service import ChatOpsService
from .intents import Intent, classify_intent
from .mutation import MutationError, ScaleExecutor
from .permissions import Decision, PermissionEngine
from .queue import ChatEvent


@dataclass(frozen=True)
class RoutedAction:
    action: str
    arguments: dict[str, Any]
    confirmation_token: str | None = None


def route_action(text: str) -> RoutedAction:
    compact = " ".join(text.split())
    confirmation = re.fullmatch(r"confirm\s+([A-Za-z0-9_-]{20,100})", compact,
                                flags=re.IGNORECASE)
    if confirmation:
        return RoutedAction("confirm", {}, confirmation.group(1))
    normalized = compact.lower()
    scale = re.fullmatch(r"(?:scale api to|scale api lên|tăng api lên)\s+(\d+)", normalized)
    if scale:
        return RoutedAction("scale_deployment", {
            "namespace": "insighthub-dev", "deployment": "insighthub-api",
            "replicas": int(scale.group(1)),
        })
    if normalized in {"delete api pod", "xóa pod api"}:
        return RoutedAction("delete_pod", {})
    if normalized in {"delete api deployment", "xóa deployment api"}:
        return RoutedAction("delete_deployment", {})
    if normalized in {"delete namespace", "xóa namespace"}:
        return RoutedAction("delete_namespace", {})
    intent = classify_intent(text)
    return RoutedAction(intent.value, {})


class ActionController:
    def __init__(self, permissions: PermissionEngine, approvals: ApprovalStore,
                 executor: ScaleExecutor, reads: ChatOpsService) -> None:
        self.permissions = permissions
        self.approvals = approvals
        self.executor = executor
        self.reads = reads

    async def process(self, event: ChatEvent) -> str:
        routed = route_action(event.text)
        if routed.action == "confirm":
            return self._confirm(event, routed.confirmation_token or "")
        decision = self.permissions.authorize(event.event_id, event.user,
                                              routed.action, routed.arguments)
        if decision.decision is Decision.DENIED:
            return f"denied: {decision.reason}"
        if decision.decision is Decision.APPROVAL_REQUIRED:
            grant = ApprovalGrant(event.user, routed.action,
                                  decision.normalized_arguments)
            token = self.approvals.issue(grant)
            return f"approval_required: confirm {token}"
        if routed.action in {intent.value for intent in Intent if intent is not Intent.UNKNOWN}:
            return await self.reads.process(event)
        return "denied: unknown action"

    def _confirm(self, event: ChatEvent, token: str) -> str:
        grant = self.approvals.get(token)
        reference = self.approvals.reference(token)
        if grant is None or grant.user != event.user:
            record_action_decision(event.event_id, "scale_deployment", "denied",
                                   event.user, approval_id=reference)
            return "denied: invalid or expired approval"
        if not self.approvals.consume_exact(token, grant):
            record_action_decision(event.event_id, grant.action, "denied", event.user,
                                   approval_id=reference)
            return "denied: invalid or already-used approval"
        try:
            if grant.action != "scale_deployment":
                raise MutationError("approval action is not executable")
            self.executor.scale_api(grant.arguments["replicas"])
        except (KeyError, MutationError):
            record_action_decision(event.event_id, grant.action, "denied", event.user,
                                   arguments_summary=grant.arguments,
                                   approval_id=reference)
            return "denied: approved operation failed"
        record_action_decision(event.event_id, grant.action, "allowed", event.user,
                               arguments_summary=grant.arguments,
                               approval_id=reference)
        return ("allowed: scaled insighthub-api in insighthub-dev to "
                f"{grant.arguments['replicas']} replicas")
