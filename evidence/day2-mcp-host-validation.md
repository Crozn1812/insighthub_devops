# Day 2 MCP Host Validation

## Environment

- Host: ChatGPT-Codex
- Platform: Windows native
- Repository: InsightHub
- Branch: `day2-mcp`

## Backend Summary

| Backend | Server ID | Pinned Version | Transport | Host Validation |
|---|---|---|---|---|
| Filesystem | `filesystem-day2` | 2026.8.31 | stdio | PASS |
| Docker | `docker-day2` | 2.2.6 | stdio | PASS |
| Kubernetes | `kubernetes-day2` | 0.0.67 | stdio | PASS |
| Prometheus | `prometheus-day2` | 0.18.0 | stdio | PASS |

## Filesystem

- Project allow-list: `G:/Download/insighthub_devops` only.
- Codex exposed a read-only tool subset.
- Positive read and listing calls succeeded.
- Outside-project reads and traversal were denied.
- No filesystem write tool was invoked.

## Docker

- Verified host calls: `container_list`, `container_logs`, and `container_stats`.
- The host tool surface was read-only.
- Mutation and destructive tools exposed: none.

## Kubernetes

- ServiceAccount: `mcp-readonly`; namespace: `insighthub`; context: `docker-desktop-mcp-readonly`.
- RBAC checks: get pods = yes; delete pods = no; get secrets = no.
- Verified MCP calls: `pods_list_in_namespace`, `namespaces_list`, and `resources_list`.
- Secret negative test: DENIED.
- Course `get_pods` maps to upstream v0.0.67 `pods_list_in_namespace`; no literal `get_pods` tool was claimed.

## Prometheus

- Backend version: 3.13.3; targets `prometheus` and `node-exporter` were up.
- Verified MCP calls: `list_targets`, `query("up")`, `metric_metadata`, `healthy`, `ready`, and `build_info`.
- Prometheus MCP version: 0.18.0.
- Forbidden tools absent: `quit`, `reload`, `snapshot`, `delete_series`, and `clean_tombstones`.

## Security Summary

- No `@latest`; all integrations were version-pinned and used local stdio.
- Filesystem was project-bounded; Docker was read-only; Kubernetes used a dedicated read-only ServiceAccount.
- Prometheus destructive/admin tools were absent; secrets remain local.

## Deferred Evidence

- Inspector screenshots: **DEFERRED / PENDING**
- Quiz: **DEFERRED / PENDING**
- Day 2 is not yet fully complete.
