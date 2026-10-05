# InsightHub DevOps — upstream compliance submission

Repository: https://github.com/Crozn1812/insighthub_devops

Branch: day6-security-finops. Final commit is the actual current head of
[PR #5](https://github.com/Crozn1812/insighthub_devops/pull/5), kept open/unmerged.
Resolve the tip using git rev-parse HEAD, git ls-remote --heads origin
day6-security-finops, and gh pr view 5 --json headRefOid; no recursive self-SHA.

Authority: congdinh2008/insighthub main at 4923fed6ef650aeea69eb179ff2a12415cf0fc90,
specification v3.3 / starter 0.2.3 / verification contract v2.
**Full upstream compliance is not achieved.** Use individual PASS/FAIL/
BLOCKED_EXTERNAL/MANUAL_REQUIRED rows, not completion labels, for acceptance.

Local runtime: real usable Kubernetes/API/PostgreSQL/Redis/Ollama/native
LiteLLM/NeMo/Prometheus/Grafana. AWS: NOT_EXECUTED_NO_AWS/static only.
Security: compliance scan 70 executed, 69 PASS, 1 benign FAIL, 0 ERROR,
0 HIGH/CRITICAL; MH5 scoped no-HIGH met, formal Day 6 acceptance unmet.
Historical 66/2/2 and official FAIL preserved. FinOps: native keys/max_budget,
three workloads, real usage, allowed/denied proof and honest planning/provider split.

- [Exact compliance matrix](docs/upstream-compliance-matrix.md)
- [Tests](docs/final-test-matrix.md)
- [Evidence](docs/evidence/upstream/README.md), [historical index](docs/evidence/README.md)
- [Demo](docs/day7/demo-runbook.md), [Loom script](docs/day7/screencast-script-3min.md)
- [Limitations](docs/project-limitations.md), [manual actions](docs/day7/remaining-manual-actions.md)

Do not claim AWS LIVE, Slack LIVE, a real Loom URL, all security tests passing,
full rubric acceptance or production readiness. Submit for transparent partial
review only until remaining upstream requirements are fulfilled/trainer accepted.
