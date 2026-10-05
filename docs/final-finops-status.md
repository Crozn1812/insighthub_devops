# Native local FinOps status

LiteLLM **1.98.0** runs against dedicated PostgreSQL and local Ollama qwen3:4b.
Three native /key/generate virtual keys have max_budget: InsightHub $1,
bot $0.50, coding workflow $1. Values stay outside Git. API generation routes
through the native key/gateway; embeddings remain direct with unchanged identity.

[Budget proof](evidence/upstream/native-budget-runtime.json): three allowed real
model calls, six denied HTTP 429 requests (two concurrent per workload), caps
restored. Denial temporarily set caps to zero. This proves concurrent zero-cap
denial, **not atomic positive-cap exhaustion or zero overshoot** under asynchronous
spend updates. [Workload proof](evidence/upstream/native-workloads-runtime.json)
covers real MCP-backed bot summaries and an isolated tested coding proposal;
the proposal was not applied to production and local capture is not Slack LIVE.

Provider USD = **0** for local Ollama. Planning rates $0.000001/input token and
$0.000002/output token exercise native budgets despite LiteLLM's free-model
bypass. They are accounting rates, not electricity/GPU costs or provider invoices.
Earlier zero-rate calls mean cumulative tokens times current rate do not reconstruct
all-time spend. [Attribution](evidence/upstream/native-attribution.json) exports
aliases, caps, actual usage/response IDs and spend without keys/hashes.
Do not add rolling gateway or judge totals to target scan totals.

Grafana UID insighthub-day6-finops has ten panels backed by a real read-only native
database exporter: workloads, usage, planning spend/caps, provider USD and health.
See [evidence index](evidence/upstream/README.md). The SQLite scoped-identity
adapter and atomic allocation proofs are preserved as historical implementation,
not current native-key proof. Sampled RSS/duration is not exclusive GPU/power use.

AWS: **NOT_EXECUTED_NO_AWS**. MH11 requires Budgets alert *when using AWS*;
no AWS runtime means no triggered budget obligation, and no fabricated AWS output.
See [weekly cost report](day7/cost-report.md) and [implementation](../finops/README.md).
