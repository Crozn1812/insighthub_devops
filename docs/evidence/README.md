# Submission evidence index

Compact tracked package for Days1–7; original historical evidence remains local
and unchanged. [Provenance](provenance.json) records source SHA-256 and package
SHA-256. Compact projections omit prompts, answer bodies, judge rendered prompts,
stack traces and unnecessary private machine paths. No FAIL/severity/error edits.
The >1MB final raw Promptfoo file and hundreds of intermediate/debug artifacts
are deliberately excluded, not deleted. Full originals are not available from
this package alone; hashes permit comparison with the retained local originals.

| Day | Evidence | What it proves / scope |
|---|---|---|
| 1 | [Final log-derived result](day1-final-result.json), [review](day1-status.md), [runtime](day1-runtime.json), [replay](day1-replay.json) | Final verifier PASS reported by prompt log; fixture202/ready/source/replay. Earlier failed retry row retained, not called successful. |
| 2 | [Status](day2-status.md), [host validation](day2-host-validation.md); tracked original MCP/RBAC under ../../evidence | Four MCP backends, Inspector4/4, read-only RBAC; partial contract PASS; screenshots/quiz pending. |
| 3 | [Status](day3-status.md), [local K8s](day3-local-k8s.md), [CI binding](day3-ci-binding.json) | Static Terraform/policy/Helm plus local deploy and historical CI; AWS NOT_EXECUTED_NO_AWS. |
| 4 | [Status](day4-status.md), [baseline](day4-baseline.md) | Local telemetry/dashboard/alerts and61m14s baseline; Slack delivery/screenshots/quiz pending. |
| 5 | [Status](day5-status.md), [audit](day5-audit.json); tracked phase5a/phase5b originals under ../../evidence | Signature/queue/approval/RBAC/controlled scale+restore; live Slack and screencast pending. |
| 6 security | [All70 records](day6-final-results.json), [verifier](day6-verifier.json), [reconciliation](day6-acceptance-reconciliation.md) | eval-aPL:66PASS/2FAIL/2ERROR; HIGH009/016, ERROR002/004, CRITICAL0; acceptance FAIL/runtime_verified=false. |
| 6 RAG/output | [Poisoning](day6-rag-poisoning.json), [sanity](day6-output-sanity.json), [integrity](day6-prompt-leak-integrity.json) | Real r2 poisoning PASS/cleanup; output checks/protected-policy remediation provenance, no policy text. Only68 retained final bodies inspected. |
| 6 FinOps | [Workloads](day6-finops-workloads.json), [app](day6-finops-insighthub.json), [ledger](day6-finops-ledger.json) | Three attributed real workloads, allow/deny, atomic concurrent threshold; historical snapshots not live totals. |
| 6 cost | [Evaluation cost](day6-cost-final.json), [workload cost](day6-finops-cost-workloads.json), [recovered tokens](day6-recovered-tokens.json) | Actual target usage70records, USD0 local provider, positive configured budget, sampled RSS/duration; not cloud/GPU/electricity billing. |
| 6 dashboard | [Monitoring](day6-monitoring-runtime.json) | Historical Grafana UID10panels/Prometheus scrape up; screenshot pending. |
| 7 | [Inventory](day7-inventory.json), [runtime](day7-runtime.json), [tests](day7-tests.json), [review](day7-review.json), [closeout](day7-final.md) | Historical Day7 fresh7runtime groups/99tests, documentation/integrity and limitations. |
| Final submission | [Fresh smoke](final-smoke.json), [final checks](final-checks.json) | New bounded health+2benign model requests; offline99Python+13evaluator mechanical tests. No security scan rerun. |

The Day7 closeout/reconciliation copies preserve their historical interpretation.
Their no-commit/ready-for-commit-NO wording describes that prior task; current
Git submission authorization/status is in [SUBMISSION](../../SUBMISSION.md).
The HTML raw-result table used FAIL labels for ERROR002/004; this package uses
the correct separate ERROR status and retains boolean passed=false.

Reviewer entry points: [test matrix](../final-test-matrix.md),
[security](../final-security-status.md), [FinOps](../final-finops-status.md),
[limitations](../project-limitations.md), [demo](../demo-runbook.md).
