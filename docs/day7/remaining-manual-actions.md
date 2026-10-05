# Remaining manual and external actions

All items affect full upstream acceptance/submission; none is waived by local verifier PASS. Roadmap MLOps was explicitly selected on 2026-10-05. Inspector and Grafana screenshots are already real evidence, not pending manual items.

## MANUAL_REQUIRED

| Upstream requirement | Why / next user action | Required evidence |
|---|---|---|
| Day2 MH10 quiz | Complete trainer's actual form | Actual score ≥7/10 |
| Day4 MH11 quiz | Complete trainer's actual form; preserve exact score | ≥4/5 MH; acceptance checklist asks 5/5 |
| Day5 MH11 / Day7 artifact8 Loom | Record the actual 180-second demo using the prepared script | Real accessible Loom URL and classroom submission |
| Day7 self-evaluation / roadmap form | Submit own answers and MLOps choice | Actual form confirmation; draft is not submission |
| Section4 daily submissions / trainer rubric | Supply actual classroom URLs and obtain review | Real timestamps/feedback; no retroactive fabrication |

## BLOCKED_EXTERNAL

| Upstream requirement | Why / next user action | Required evidence |
|---|---|---|
| Day3 MH3/4/5/6/9/10/11/14 | No AWS account/credits; configure authorized OIDC/backend/environment and reviewed workflow | Actual AWS plan/cost/deploy, managed services/IRSA/cloud smoke/tags; local/static is insufficient |
| Day4 MH6 Slack alert | Workspace webhook/channel authorization absent | Actual #alerts delivery |
| Day5 MH4/5/6 Slack LIVE | Public event URL, real Slack app/workspace credentials absent | Signed real mentions for three intents, replies, permission/approval audit |
| Day7 artifact10 LIVE | No reviewer-accessible endpoint supplied | Reachable URL and actual HTTP200; local health alone is insufficient |

## Local acceptance gaps retained

Day6 pristine verifier remains INCOMPLETE: stale/current-source initial and all-pass final/live observations are unmet; benign-001 is FAIL. Latest native NeMo output-override probe is FAIL (4/5 pass), semantic checks disabled. These are technical gaps, not external waivers. No new full security scan or remediation loop is authorized by this checklist. Optional ruff/mypy remain unavailable. PR5 stays open/unmerged for review.

See [matrix](../upstream-compliance-matrix.md), [demo](demo-runbook.md), [script](screencast-script-3min.md), [evidence](../evidence/upstream/README.md). Never paste credentials into tracked artifacts.
