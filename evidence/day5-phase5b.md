# Day 5 Phase 5B — MCP and three intents evidence

Timestamp: 2026-09-30T17:17:00+07:00

## Runtime and security boundary

- Mode: local-only / no-cost.
- MCP transport: real stdio through official Python MCP SDK 2.2.0.
- Prometheus MCP: `prometheus/prometheus-mcp` 0.18.0, targeting loopback port 19090.
- Kubernetes MCP: `kubernetes-mcp-server` 0.0.67, context `docker-desktop`.
- Kubernetes identity: dedicated `mcp-readonly` ServiceAccount with a refreshed
  short-lived token stored only in the external kubeconfig.
- Kubernetes namespace: `insighthub-dev`.
- RBAC verification: pod/deployment get/list YES; Secret get NO; pod delete NO;
  deployment patch NO.
- MCP Secret access test: DENIED. No Secret content was returned or recorded.
- Kubernetes mutation tool catalog: none exposed.
- Prometheus `quit`, `reload`, `snapshot`, `delete_series`, and `clean_tombstones`:
  none exposed; TSDB admin tools disabled.

## Real MCP smoke

- Prometheus `healthy`: PASS.
- Prometheus `ready`: PASS.
- Prometheus `list_targets`: returned the live Day 4 InsightHub API target.
- Prometheus `query(up)`: returned live cluster series.
- Prometheus `query(insighthub_http_requests_total)`: returned real API request data.
- Kubernetes `pods_list_in_namespace(insighthub-dev)`: returned seven real pods.
- Kubernetes `resources_list(apps/v1, Deployment, insighthub-dev)`: PASS.

## Ingest-today metric

- Metric: `insighthub_documents_created_today`.
- Source: PostgreSQL `documents.created_at` using a parameterized `COUNT(*)` query.
- Semantics: documents created since local-day midnight in `Asia/Ho_Chi_Minh`;
  it does not claim successful/ready ingestion.
- Labels: none (low cardinality).
- Live Prometheus MCP result: 7.
- Independent PostgreSQL count: 7.

## Local signed-event E2E

All three requests were authenticated, ACKed, queued, consumed by the separate worker,
and answered through local CaptureTransport:

1. Health → `HEALTHY`; API target UP, seven workloads observed, zero unhealthy pods.
2. Ingest today → seven documents created since local midnight.
3. Failing pods → no unhealthy pods in `insighthub-dev`.

The worker path used MCP stdio. Direct Prometheus HTTP, kubectl, and PostgreSQL were used
only afterward as cross-checks; they agreed with the bot results.

## Verification

- ChatOps tests: 37 passed, 0 failed, 0 skipped, 0 xfail.
- Phase 5A tests remain included and passing (19 original tests).
- API image unit tests: 9 passed.
- Complete backend suite with DB lab: 67 passed.
- No live Slack message, AWS call, paid API, mutation action, official Day 5 verifier,
  commit, push, or PR was performed.
- Evidence contains no token, kubeconfig path, credential, raw Secret, or raw MCP frame.
