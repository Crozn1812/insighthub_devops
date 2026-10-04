# InsightHub DevOps — final submission

PROJECT: InsightHub DevOps

REPOSITORY: https://github.com/Crozn1812/insighthub_devops

BRANCH: day6-security-finops

FINAL COMMIT: current head of [PR #5](https://github.com/Crozn1812/insighthub_devops/pull/5).

Audited source/config/evidence checkpoint:
[`adee283dc040a570f2564a68055638ad4542ed9e`](https://github.com/Crozn1812/insighthub_devops/commit/adee283dc040a570f2564a68055638ad4542ed9e).
This manifest is finalized in a metadata-only follow-up commit; its own commit SHA
cannot be embedded in its content without creating another commit. The PR head
and remote submission branch are authoritative for the final tip. Resolve it with:

```powershell
git rev-parse HEAD
git ls-remote --heads origin day6-security-finops
gh pr view 5 --repo Crozn1812/insighthub_devops --json headRefOid
```

PR: https://github.com/Crozn1812/insighthub_devops/pull/5 — OPEN; base main. No automatic merge.

STATUS: COMPLETE_WITH_LIMITATIONS

RUNTIME: LOCAL VERIFIED / USABLE; final bounded smoke7/7 groups PASS.

TESTS: Final existing offline Python suites99/99 PASS; evaluator mechanical
tests13/13 PASS. No full security evaluation rerun; ruff/mypy unavailable.

SECURITY: COMPLETED_WITH_LIMITATIONS; Day6 acceptance/verifier FAIL,
runtime_verified=false. Official eval-aPL-2026-10-04T01:13:14:70executed,
66PASS/2FAIL/2ERROR. HIGH attack-009/016 unresolved; ERROR attack-002/004;
CRITICAL0. No adjudication/severity/verdict edits.

FINOPS: LOCAL TECHNICAL EXECUTION COMPLETE. Three scoped workload identities,
actual traffic/tokens, budget allow/deny/concurrency and Grafana evidence.
Equivalent scoped adapter, not native LiteLLM key admin. ProviderUSD0 local
Ollama; planning credits/resource measurements distinct from billing.

AWS: NOT_EXECUTED_NO_AWS; cloud/IaC STATIC_VALIDATION_ONLY.

DEMO: [Runbook](docs/demo-runbook.md)

EVIDENCE: [Tracked sanitized index](docs/evidence/README.md)

LIMITATIONS: [Risk register](docs/project-limitations.md)

Days1–7: COMPLETE_WITH_LIMITATIONS each. Historical partial verifier PASS for
Days1–5 does not mean full original rubric completion. Security FAIL remains.

Manual follow-up: screenshots/quiz/screencast, Slack integration, HIGH/error
review, trainer acceptance and review of packaged vs retained raw evidence.
This PR is for submission/review, not automatic merge or production acceptance.

Submission checkpoint pushed normally; GitHub README render and required docs/
source/package paths verified. Two workflows on the implementation checkpoint
passed (Starter baseline; Day3 IaC validation). Checks on subsequent PR/metadata
heads are independent and must be reviewed in GitHub; no blanket CI/security
acceptance claim. Local tree clean after the implementation commit, except
intentionally ignored local evidence/diagnostics/runtime files.
