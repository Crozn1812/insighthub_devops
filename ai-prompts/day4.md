# Day 4 AI Prompt Log

Host: ChatGPT-Codex
Date: 2026-09-30
Track: local-only / no-cost

## Entry 1 — Monitoring architecture and inventory

- Time: 2026-09-30 morning
- Context: Day 3 source and Docker Desktop Kubernetes runtime were frozen before Day 4 work.
- Prompt summary: Inventory existing metrics and install a pinned local kube-prometheus-stack without AWS or paid services.
- Why it worked: The telemetry plan mapped every component to an honest source before deploying exporters.
- Reviewed/changed: Installed chart `91.8.2`, enabled local Prometheus/Grafana/Alertmanager, retained Day 2 monitoring, and kept all services loopback or ClusterIP.

## Entry 2 — Instrumentation, rules, and dashboard

- Time: 2026-09-30 afternoon
- Context: Existing application metrics lacked real Redis queue depth, cost provenance, and deterministic local chaos controls.
- Prompt summary: Add minimal safe instrumentation, 1-hour anomaly rules, tested alerts, and at least nine real Grafana queries.
- Why it worked: Chaos defaults remain disabled, queue depth comes from Redis, fixture cost is explicitly zero, and canonical/runtime rule synchronization is executable.
- Reviewed/changed: Added unit coverage, three ServiceMonitors, pinned exporters, 14 promtool-validated rules, and a 12-panel provisioned dashboard. A duplicate metric registration discovered during rollout was fixed and regression-tested.

## Entry 3 — Baseline, incidents, RCA, and verifier

- Time: 2026-09-30 afternoon
- Context: The official verifier requires three distinct incident reports whose exact samples remain queryable in live Prometheus.
- Prompt summary: Collect at least 60 minutes of real baseline telemetry, inject three bounded local incidents, restore health, build evidence-first RCAs, and run the official verifier.
- Why it worked: Incident work is gated on the actual baseline clock and citations are validated against the live query-range API.
- Reviewed/changed: Collected a 61m14s complete-signal baseline; produced three real incidents whose dedicated alerts reached `firing`; restored delay, worker replicas, error mode, queue, and API health; and validated every RCA citation against live query-range data. Manual Slack, screenshot, and quiz gaps remain explicit.
