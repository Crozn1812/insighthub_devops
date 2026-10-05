# Day 2 MCP Debug Session

## 1. Incident Summary

- Date: 2026-09-29
- Investigation window: 2026-09-29T13:30:41.989Z to 2026-09-29T13:31:35.357Z
- Environment: Windows native with Docker Desktop
- Container: `day2-crash-fixture`
- Image: `prom/prometheus:v3.13.3`
- Initial observed state: `Exited`
- Initial exit code: `2`
- Purpose: controlled Day 2 MCP diagnostic exercise

## 2. Investigation Constraints

- Docker MCP was the sole source of Docker diagnostic evidence.
- MCP server: `docker-day2`
- The Docker MCP tool surface was read-only.
- No container mutation occurred during the investigation.
- Docker CLI was not used for RCA evidence.
- Credentials and secrets were not recorded.

## 3. MCP Investigation Trace

| Time UTC | MCP Server | Tool | Input | Result Summary |
|---|---|---|---|---|
| 2026-09-29T13:31:00.389Z | `docker-day2` | `container_list` | `{"all":true,"sparse":true}` | Located `day2-crash-fixture`; image `prom/prometheus:v3.13.3`; state `exited`; status reported exit code 2. |
| 2026-09-29T13:31:11.427Z | `docker-day2` | `container_inspect` | `{"id_or_name":"day2-crash-fixture"}` | `/bin/prometheus` received `--config.file=/day2/fixture/missing-prometheus.yml`; state was exited with code 2; restart policy was `no`. |
| 2026-09-29T13:31:24.375Z | `docker-day2` | `container_logs` | `{"id_or_name":"day2-crash-fixture","tail":100,"stdout":true,"stderr":true,"timestamps":true,"follow":false}` | Bounded logs reported a configuration load failure because the specified file did not exist. |

`container_diff` was not used because the first three read-only calls provided sufficient evidence for the RCA.

## 4. Observed Evidence

The following are observed facts, not interpretation:

- The container image was `prom/prometheus:v3.13.3`.
- The container state was `exited`, it was not running, and its exit code was `2`.
- The startup process was `/bin/prometheus`.
- The process argument was `--config.file=/day2/fixture/missing-prometheus.yml`.
- The Docker state error field was empty.
- The restart policy was `no`.
- The bounded log error was: `open /day2/fixture/missing-prometheus.yml: no such file or directory`.

## 5. Root Cause Analysis

**Root cause:** The container was configured to start Prometheus with a configuration path that did not exist inside the container.

**Immediate failure mechanism:** `/bin/prometheus` attempted to load `/day2/fixture/missing-prometheus.yml`, received a file-not-found error, and terminated during startup with exit code 2.

The evidence supports this conclusion because `container_inspect` identifies the exact process and configuration argument, while `container_logs` independently reports that the same path could not be opened. `container_list` confirms the resulting exited state and exit indication. Exit code 2 is consistent with the observed startup/configuration error.

## 6. Remediation

Supply a valid Prometheus configuration file at the path passed through `--config.file`, either by correcting the argument to an existing in-image path or by mounting a validated configuration file at the intended path. Then create a separate validation container and confirm that it remains running and reports successful readiness.

No remediation was applied during RCA. The failed fixture remains preserved as evidence.

## 7. Impact and Isolation

- Impact was limited to the controlled `day2-crash-fixture` container.
- The InsightHub application was not modified.
- `prometheus-day2` was unaffected.
- `node-exporter-day2` was unaffected.

## 8. Debugging Outcome

- InvestigationStartUTC: `2026-09-29T13:30:41.989Z`
- InvestigationEndUTC: `2026-09-29T13:31:35.357Z`
- MCP-assisted investigation duration: `53.368 seconds`
- Result: **RCA CONFIRMED**

No non-MCP debugging-time comparison was made.

## 9. Security Notes

- Docker MCP remained read-only.
- No mutation or destructive tools were exposed.
- Docker TCP port 2375 was not enabled or used.
- No credentials, tokens, authorization headers, or private keys are present in this document.
- Log retrieval was bounded to the latest 100 lines.

## 10. Learning Notes

In this case, Codex acted as the MCP Host and client, while `docker-day2` acted as the MCP Server that exposed a constrained diagnostic tool surface. `container_inspect` supplied structured runtime configuration and state, whereas `container_logs` supplied the application's own failure message; together they connected the invalid startup argument to the observed termination. A read-only MCP is appropriate for diagnosis because it permits evidence collection while preventing accidental lifecycle or configuration changes during an incident investigation.
