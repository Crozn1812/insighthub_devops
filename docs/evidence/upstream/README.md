# Upstream audit evidence

Authority: upstream main 4923fed6ef650aeea69eb179ff2a12415cf0fc90, specification
v3.3 / starter 0.2.3 / verification contract v2. These are sanitized projections
of actual observations; historical package remains [separate](../README.md).

| Evidence | Scope |
|---|---|
| [Official verifiers](official-verifiers.json) | Pristine upstream executable; exact PASS/INCOMPLETE, false runtime flags retained; per-run source hashes/times |
| [Tests](tests-current.json) | API 146 +97 subtests, ChatOps62, adapter/artifacts12, verifier69, evaluator13; proxy3 and promtool |
| [Compliance scan](security-compliance-70.json) | All unchanged70 verdicts, 69/1/0, 0 HIGH/CRITICAL; no raw prompts/judge-policy dump |
| [NeMo checks](guardrails-runtime.json), [outage](nemo-outage-proof.json) | Actual input/context/output/benign/PII/agency checks; HTTP503 fails closed; regex-only rails |
| [Native budgets](native-budget-runtime.json) | Three native keys/caps, three allowed/six429, concurrent zero-cap scope, caps restored |
| [Workloads](native-workloads-runtime.json), [attribution](native-attribution.json) | Real bot MCP/model and coding isolation; actual IDs/usage/caps/spend; not SlackLIVE |
| [Four MCP calls](mcp-host-calls.json), [RBAC](mcp-rbac-current.json) | Real read-only host traces, pod read allowed, secret/delete denied |
| Inspector [filesystem](inspector-filesystem.png), [Docker](inspector-docker.png), [Kubernetes](inspector-kubernetes.png), [Prometheus](inspector-prometheus.png) | Genuine tool-result screenshots, not fabricated; filesystem server itself offers writes but Codex exposes read-only subset |
| Grafana [Day4 top](grafana-day4-top.png), [cost](grafana-day4-current-cost.png), [dependencies](grafana-day4-bottom.png) | Genuine rendered panels and real telemetry; viewport captures are partial views of 12-panel dashboard |
| Grafana [workloads](grafana-native-workloads.png), [planning](grafana-native-planning.png), [budget](grafana-native-budget.png), [provider/UP](grafana-native-provider-health.png) | Ten-panel native dashboard, actual three workload series, provider0/exporter1 |

Large raw scans/intermediate logs, databases/models/runtime archives and all private
env/key/kubeconfig files remain excluded. Failed evidence is preserved, not deleted.
The initial partially loaded grafana-day4.png capture stays local and is excluded
from submission. No screenshot claims a public URL, Slack delivery or Loom video.

Observed hashes/timestamps are not rewritten to certify later code. Dataset and
fork verifier were unchanged during this audit. The fork has a preexisting text
line-ending-normalizing fingerprint extension; this audit uses the pristine raw-byte
upstream executable and records that difference, rather than modifying a verifier.

## Final observations and retained failures

- [Baseline](real-baseline.json), [baseline MCP](baseline-mcp-query.json): 75.125 minutes, 60 finite hourly samples; 113 successes and two startup timeouts retained.
- [Latency](incident-latency.json), [range citations](incident-latency-range-citations.json), [queue](incident-queue.json), [error](incident-error.json): three genuine firing/recovery incidents with actual model RCA IDs and MCP telemetry. All 20 queue document IDs recovered ready.
- [Failed error attempt](incident-error-attempt1.json) and earlier Day4 verifier FAIL remain preserved; actual range-query projection documents one recording-value discrepancy. Latest pristine Day4 PASS covers 16 samples.
- [Current runtime](final-runtime-smoke.json), [native attribution](native-attribution-final.json), [current NeMo](nemo-final-runtime.json): NeMo probe 4 PASS/1 FAIL, output override allowed; no semantic protection claim.
- [Day6 preconditions](day6-verifier-preconditions.md): no-HIGH is distinct from strict all-pass/fresh-source/live-observation acceptance. No extra full scan.

[CI checkpoint](ci-final-checkpoint.json): four push/PR runs green at e0d199c. Day3 pristine GitHub profile PASS against actual artifact/source 2cefdb588c88cd298fa4e3e4d8b564e4297065147a568053e47a0e1cc403b512; deployment/AWS not attested. Previous local INCOMPLETE and other verifier runs remain preserved.
