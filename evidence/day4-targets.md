# Day 4 Prometheus targets

Observed from the live local Prometheus target API on 2026-09-30 (Asia/Saigon).

| Component | Scrape/metric source | Status |
| --- | --- | --- |
| API | `insighthub-api` ServiceMonitor, native `/metrics` | UP |
| web | kubelet/cAdvisor and kube-state-metrics | UP |
| ingestion-worker | kubelet/cAdvisor, kube-state-metrics, and API queue gauge | UP |
| PostgreSQL | `insighthub-postgres-exporter` ServiceMonitor | UP |
| Redis | `insighthub-redis-exporter` ServiceMonitor | UP |

The three custom scrape targets (`insighthub-api`, PostgreSQL exporter, Redis
exporter) were all `up`. Web and worker intentionally do not claim native
Prometheus endpoints; their real pod/container and deployment signals come
from the monitoring stack's Kubernetes targets.
