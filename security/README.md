# Security / Governance / FinOps

Current compliance scan on the unchanged70 dataset: **69 PASS, 1 benign FAIL,
0 ERROR, 0 HIGH, 0 CRITICAL**. MH5's no-HIGH condition is met for this observed
run; formal Day6 acceptance remains unmet. [Current status](../docs/final-security-status.md),
[per-case evidence](../docs/evidence/upstream/security-compliance-70.json), and
[matrix](../docs/upstream-compliance-matrix.md) govern current claims.
Historical66/2/2 and initial reports remain preserved in the [historical index](../docs/evidence/README.md).

Promptfoo is pinned0.123.1 with valid local plugins/strategies. The foundation
promptfooconfig.yaml and generated corpus are historical initial-generation inputs;
its qwen3:1.7b judge is rejected for acceptance. The evaluated70 cases use the
frozen final config/profile and qwen3:4b, not that rejected foundation judge.
Do not rerun casually, change expectations, special-case IDs or adjudicate manually.
Real RAG poisoning must use ingestion/retrieval, not only a /chat attack string.

Native NeMo0.24.1 input/context/output rails and native LiteLLM virtual keys are
actual local runtime additions. Regex rails are not semantic guarantees.
See [guardrails](guardrails/README.md), [threat model](threat-model.md),
[coverage](security-coverage.md), [FinOps](../docs/final-finops-status.md).
