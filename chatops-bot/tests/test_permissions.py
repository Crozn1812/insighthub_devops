import pytest

from app.permissions import Decision, decide


@pytest.mark.parametrize("action", ["health", "ingest_today", "failing_pods"])
def test_read_actions_are_allowed(action: str) -> None:
    assert decide(action).decision is Decision.ALLOWED


def test_only_exact_scale_target_requires_approval() -> None:
    arguments = {"namespace": "insighthub-dev", "deployment": "insighthub-api",
                 "replicas": 2}
    result = decide("scale_deployment", arguments)
    assert result.decision is Decision.APPROVAL_REQUIRED
    assert result.normalized_arguments == arguments


@pytest.mark.parametrize("arguments", [
    {"namespace": "insighthub-dev", "deployment": "insighthub-api", "replicas": 0},
    {"namespace": "insighthub-dev", "deployment": "insighthub-api", "replicas": 6},
    {"namespace": "other", "deployment": "insighthub-api", "replicas": 2},
    {"namespace": "insighthub-dev", "deployment": "insighthub-web", "replicas": 2},
])
def test_scale_outside_policy_is_denied(arguments: dict) -> None:
    assert decide("scale_deployment", arguments).decision is Decision.DENIED


@pytest.mark.parametrize("action", [
    "delete_pod", "delete_deployment", "delete_namespace", "arbitrary_shell",
])
def test_destructive_and_unknown_actions_are_denied(action: str) -> None:
    assert decide(action).decision is Decision.DENIED
