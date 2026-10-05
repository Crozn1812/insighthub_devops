# InsightHub DevOps

InsightHub is a local RAG notebook: upload .txt/.md/.pdf, ingest asynchronously,
ask questions and review citations. This fork implements the DO2603 seven-day
project against authoritative upstream [congdinh2008/insighthub](https://github.com/congdinh2008/insighthub)
at 4923fed6ef650aeea69eb179ff2a12415cf0fc90, specification v3.3, starter 0.2.3.

**Full upstream compliance is not achieved.** Local runtime is usable/verified;
AWS runtime is **NOT_EXECUTED_NO_AWS**. Current 70-case compliance scan is
**69 PASS / 1 FAIL / 0 ERROR / 0 HIGH / 0 CRITICAL**. MH5 no-HIGH is met for that
run, but Day 6 official acceptance remains unmet: verifier INCOMPLETE and
runtime_verified=false. Historical 66/2/2 results and HIGH findings are preserved.
Quizzes, Slack LIVE, mandatory Loom, public access and trainer review remain.

## Architecture and stack

User → Next.js web → FastAPI → Redis/ARQ → separate ingestion worker
→ PostgreSQL 16 + pgvector. Upload returns HTTP 202 after enqueue; worker does
chunk/embed/store with bounded transient retry and idempotent replay.
Chat embeds/retrieves/sanitizes, routes through native LiteLLM 1.98.0 to local
Ollama qwen3:4b, validates structured output/citations and applies output controls.
Embeddings remain mxbai with consistent identity. Native NeMo 0.24.1 protects
input/context/output using pinned regex rails; outage fails closed. The latest
native probe has **4 PASS / 1 FAIL**: an output behavior-override sentence was
allowed. Semantic checks are disabled; see [security status](docs/final-security-status.md).

Docker Desktop Kubernetes runs application/monitoring namespaces; Ollama runs on
the host and native LiteLLM/NeMo/accounting services run in local Docker.
Prometheus gathers app/worker/exporter metrics; Grafana shows observability and
native FinOps. Alertmanager Slack delivery requires workspace authorization.
ChatOps provides signed events, MCP facts, approval/RBAC, durable Redis queue,
audit and guarded advisory summaries; local tests do not prove Slack LIVE.

## DevOps, security and FinOps

Terraform/Helm, version pins, policies, Checkov and GitHub Actions support the
local/static path and opt-in protected OIDC AWS jobs. No cloud apply occurred.
MCP uses four actual pinned backends with read-only host subsets, project-only
filesystem and Kubernetes read-only ServiceAccount. Inspector evidence is real.
Security includes input/context/output guards, poisoning/prompt-leak work,
Promptfoo coverage and immutable dataset/verifier. See [security status](docs/final-security-status.md).

Three **native LiteLLM virtual keys with max_budget** identify InsightHub, bot
and coding workflow. Real allowed calls, six concurrent zero-cap denials,
attribution and restored budgets are documented. Local Ollama provider USD 0 is
separate from token-based planning spend; positive-cap atomic exhaustion is not
claimed. See [FinOps status](docs/final-finops-status.md).

## Run, test and demo

Start with [GETTING_STARTED](GETTING_STARTED.md); use private environment/key
files outside Git. The [demo runbook](docs/day7/demo-runbook.md) covers Kubernetes,
readiness, PostgreSQL, Redis, Ollama, LiteLLM, upload/ready/chat/citations,
Prometheus/Grafana, guardrails/budgets and known findings. AWS is not required.
Do not replace existing DB volumes or embedding identity when restarting.
Use [test matrix](docs/final-test-matrix.md) for actual commands/counts and scope;
the expensive full scan is retained rather than casually repeated.

## Repository and review

web/ UI; api/ backend; ingestion-worker/ ARQ entrypoint; chatops-bot/ signed bot;
infra/ Terraform/Helm/schema/policies; observability/ metrics/rules/dashboards;
security/ frozen evaluation/guardrails/threat model; finops/ native local gateway
and historical adapter; tests/ milestone/verifier regression; ai-prompts/ real
decision logs; docs/evidence/ compact sanitized evidence, not raw runtime dumps.

- [Exact 70-Must-have matrix](docs/upstream-compliance-matrix.md)
- [Architecture](docs/final-architecture.md) and [request flow](docs/end-to-end-flow.md)
- [Evidence index](docs/evidence/README.md) and [current audit evidence](docs/evidence/upstream/README.md)
- [Limitations](docs/project-limitations.md), [Day 7 checklist](docs/day7/submission-checklist.md)
- [Submission convention audit](docs/submission-convention-audit.md), [submission](SUBMISSION.md)

Historical failed evidence is preserved. No claim of all security tests passing,
AWS deployment, full rubric acceptance or production readiness is made.
