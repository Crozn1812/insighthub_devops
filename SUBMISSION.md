# InsightHub DevOps — final submission

PROJECT: InsightHub DevOps

REPOSITORY: https://github.com/Crozn1812/insighthub_devops

BRANCH: day6-security-finops

FINAL COMMIT: Not yet committed at preparation time; resolved after push.

PR: Not yet created at preparation time.

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
