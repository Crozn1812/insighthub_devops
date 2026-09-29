# Day 2 MCP Inspector CLI Evidence

## Runtime

- Inspector: `@modelcontextprotocol/inspector@2.8.0`
- Node.js: `v24.19.0`
- Mode: CLI with read-only `--config` session

## Filesystem

- Initialize and `tools/list`: PASS
- `list_allowed_directories`: PASS; allow-list was `G:/Download/insighthub_devops` only.
- Outside-project read and traversal: DENIED.

Direct Inspector connects to the official upstream filesystem server and sees its full catalog, including write-capable tools. Those tools were not invoked. Codex Host separately filters filesystem exposure to a read-only `enabled_tools` subset.

## Docker

- Initialize, `tools/list`, and `container_list`: PASS
- Mutation tools exposed: none

## Kubernetes

- Initialize, `tools/list`, and `pods_list_in_namespace` for `insighthub`: PASS
- Empty pod list: valid; mutation tools exposed: none
- Course `get_pods` maps to upstream v0.0.67 `pods_list_in_namespace`.

## Prometheus

- Initialize, `tools/list`, and `query("up")`: PASS
- `prometheus` = 1; `node-exporter` = 1
- Destructive/management mutation tools exposed: none

## Result

- Inspector CLI: **4/4 PASS**
- Screenshot evidence: **DEFERRED / PENDING**
- Invalid earlier screenshots are not represented as passing evidence.
