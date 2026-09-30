# Observability

Day 4 uses a local-only monitoring stack on Docker Desktop Kubernetes. No
Grafana Cloud or AWS resources are used.

## Pinned stack

- Helm chart: `prometheus-community/kube-prometheus-stack`
- Chart version: `91.8.2`
- Prometheus Operator app version: `v0.94.1`
- Namespace: `monitoring`
- Prometheus retention: `15d`
- Services: local `ClusterIP` only
- Custom scrape interval: `15s`

The values in `kube-prometheus-stack-values.yaml` allow `ServiceMonitor` and
`PrometheusRule` discovery across namespaces. Grafana dashboards are
provisioned from labeled ConfigMaps rather than manual UI edits.

## Five-component telemetry mapping

| InsightHub component | Real metric source |
| --- | --- |
| API | Native `/metrics` endpoint through `ServiceMonitor` |
| web | kubelet/cAdvisor container metrics and kube-state-metrics |
| ingestion-worker | kubelet/cAdvisor, kube-state-metrics, and the API's real Redis queue-depth gauge |
| PostgreSQL | Pinned `postgres_exporter` connected through the local runtime Secret |
| Redis | Pinned `redis_exporter` connected to `insighthub-redis` |

Web and worker do not claim native Prometheus endpoints. Runtime credentials
remain in Kubernetes Secrets and are never rendered into this directory.

## Application signals and controlled incidents

- `insighthub_ingestion_queue_depth` reads the real configured ARQ sorted-set
  size from Redis at scrape time.
- `insighthub_llm_estimated_cost_usd_total` records usage-derived estimated
  cost. The local fixture provider initializes this to zero because it makes no
  billable provider call.
- `DAY4_CHAOS_LLM_DELAY_SECONDS` and `DAY4_CHAOS_FORCE_ERROR` are disabled by
  default, bounded by application validation, and changed only through an
  explicit local Helm upgrade during a controlled incident.

`prometheus-rules.yaml` is the canonical promtool input. The runtime
`prometheus-rule-crd.yaml` contains the same groups, and
`scripts/day4/check-rule-sync.py` fails if they diverge.

## Alert delivery

Alertmanager always has a valid local null receiver. Slack routing is enabled
only when a real runtime webhook Secret is supplied. No webhook is committed;
without that Secret, Slack delivery remains `PENDING_USER_SECRET`.
