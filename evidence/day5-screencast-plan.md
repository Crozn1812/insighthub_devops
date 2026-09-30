# Day 5 screencast plan

Status: `PENDING_MANUAL`

Target duration: approximately three minutes.

- **0:00–0:20** — Show the architecture: Slack → authenticated HTTP ACK → Redis
  queue → worker → Prometheus/Kubernetes MCP → response.
- **0:20–0:55** — Run the health intent and briefly identify both MCP backends.
- **0:55–1:25** — Run the ingest-today intent and explain the
  `Asia/Ho_Chi_Minh` midnight/PostgreSQL metric semantics.
- **1:25–1:55** — Run the failing-pods intent and show the truthful current result.
- **1:55–2:30** — Demonstrate approval-required, scale API from 1→2, then restore 2→1.
- **2:30–2:45** — Send a destructive request and show the policy denial.
- **2:45–3:00** — Summarize structured audit, least-privilege identities, replay
  protection, deduplication, bounded retry, and the no-secret evidence policy.

Recording guidance: hide tokens, request bodies, kubeconfigs, approval tokens, tunnel
credentials, database credentials, and unrelated desktop notifications. Do not mark
this item complete until an actual user-recorded screencast exists.
