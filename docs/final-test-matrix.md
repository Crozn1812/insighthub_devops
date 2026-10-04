# Final test / verification matrix

PASS dưới đây chỉ áp dụng scope có evidence; không thay full rubric. H = historical,
D7 = kiểm tra mới Day 7, static = không chứng minh deployment/runtime.

| Capability | Status | Evidence / kiểm tra | Scope / limitation |
|---|---|---|---|
| API | PASS | D7 readyz + unit HTTP; day7-runtime.json | Local real db=true; không API exhaustive |
| Web | PASS | D7 pod ready, HTTP200 qua Service | Backend-visible page; browser UI manual pending |
| Async ingestion | PASS | H day1 runtime/replay; ai-prompts/day1.md final 6 milestone PASS | Fixture historical; no fresh D7 upload |
| PostgreSQL/pgvector | PASS | D7 pg_isready, API RAG; H stored vectors | Retrieval mới; không backup/restore test |
| Redis | PASS | D7 PONG; H ingestion/ChatOps queue | Không durability disaster test D7 |
| RAG | PASS | D7 real benign, utility/citation; H poisoning | Một benign request không semantic benchmark |
| Docker | PASS | D7 running containers/images; offline Linux unit tests | Relay health unhealthy được ghi riêng |
| Kubernetes | PASS | D7 Ready node/pods; H day3 local-k8s | Single local node, không HA |
| Helm | PASS | H day3-status lint/render/local deploy | Không upgrade/rollback D7 |
| Terraform | PASS | H day3-status; Checkov20/0, targeted suppression1, policy2/2 | STATIC_VALIDATION_ONLY; AWS NOT RUN |
| GitHub Actions | PASS | H day3-status PR run36657449428 + ci-binding | Không trigger/new remote run D7 |
| MCP read-only | PASS | H day2-status, inspector4/4; RBAC Secret/delete denied | Host screenshots/quiz deferred |
| Prometheus | PASS | D7 ready200; H day4 targets/metrics, day6 monitoring | Không one-hour re-baseline D7 |
| Grafana | PASS | D7 health200; H day4 12panels, day6 FinOps10panels | Screenshots pending |
| Alerts | PARTIAL | H day4 3 incidents firing/restored, promtool PASS | Local Alertmanager PASS; Slack delivery pending |
| ChatOps signature/replay | PASS | H day5-phase5a/status | Local signed event, không live Slack |
| ChatOps durable queue | PASS | H day5-phase5a/status | Redis worker tests historical |
| ChatOps deduplication/retry | PASS | H day5-status | Bounded retry/dedup tests historical |
| ChatOps approval | PASS | H day5-status/audit | Binding/expiry/single-use; không new approvals D7 |
| ChatOps Kubernetes action | PASS | H day5-status/audit controlled scale/exact restore | Constrained identity; no mutation D7 |
| ChatOps live Slack | NOT RUN | H day5-status PENDING_USER_SLACK_APP | Human-controlled external integration |
| Prompt injection | PARTIAL | H final corpus + guardrail unit tests | Two injection-category HIGH FAIL; no fresh attack tests |
| Benign utility | PASS | H final10/10 benign; D7 one benign RAG | Model nondeterminism/limited coverage |
| RAG poisoning | PASS | H day6-final-rag-poisoning.json | r2 doc23; no rerun D7 |
| PII protection | PARTIAL | H retained bodies scan + unit checks | Zero deterministic matches in68; HIGH native judge findings unresolved |
| Excessive agency | PARTIAL | H final raw; agency mechanical tests | Two evaluator ERROR, no valid final verdict |
| Protected prompt leakage | PARTIAL | H safeguards/sanity +68 retained inspections | Two bodies unavailable; no full policy exported |
| Final70 evaluation | FAIL | H raw eval-aPL:66PASS/2FAIL/2ERROR | Day6 verifier FAIL/runtime_verified=false; unchanged |
| LiteLLM routing | PASS | H day6-insighthub; D7 two benign model requests | Local Ollama only; new config not security rescanned |
| Workload attribution | PASS | H three identity traffic + ledger | Equivalent adapter, not native key management |
| Token accounting | PASS | H evaluation/cost70 + D7 actual provider usage | Recovered tokens use counter windows; not body reconstruction |
| Budget enforcement | PASS | H Bot200/200/429 + denial ledger | Planning credits, not actual provider billing |
| Concurrent threshold | PASS | H Coding one200/one429 | Atomic local SQLite; no cloud load test |
| Cost evidence | PASS | H cost USD0, positive budgetUSD1 | RSS/duration measured; GPU/electricity NOT RUN |
| AWS runtime | NOT RUN | H day3-status | NOT_EXECUTED_NO_AWS |

## Historical milestone results

Day1 prompt log records final backend67/67, milestone6/6, official verifier PASS
and runtime_verified=true. Earlier docs contain backend62/62 and regression66/68
with CRLF failures; these are earlier observations, not overwritten by final
milestone success. day1-async-runtime.json also retains failed-to-failed retry
observation; independent final review and later milestone log cover successful
retry. Do not present the earlier row as successful retry evidence.

Days2/3/4/5 official partial-runtime contracts PASS, runtime_verified=true;
manual/cloud/Slack gaps prevent a full rubric completion claim. Day6 official
FAIL, runtime_verified=false. Historical evidence/source hashes are retained;
the current documentation tree is not a reattestation of those runs.

## Fresh Day 7 tests

99 existing offline unit/artifact tests PASS, 0 assertion failures: guardrails48,
HTTP15, providers24, FinOps12. Executed using existing Linux API image Python,
network none, read-only repo, tmpfs test storage; no packages installed.
Seven runtime check groups PASS/0FAIL, including current RAG and LiteLLM traffic.

Initial WSL pytest collection failed with 3 missing-dependency collection errors
(prometheus_client/httpx). First container invocation omitted test-support import
path: 48 executed PASS plus 2 module import errors. Corrected invocation through
WSL then failed to launch with Wsl/Service/0x8007274c. Final direct Docker invocation
added api/tests to PYTHONPATH and passed99/99. These infrastructure/setup attempts
are recorded, not counted as security verdicts or hidden as PASS. Ruff/mypy
unavailable; no installs. Day6 historical117 includes helper/evaluator/live checks
not rerun here; do not sum it with Day7 totals as unique coverage.

See [evidence index](evidence/README.md), [runtime](evidence/day7-runtime.json),
[Day7 closeout](evidence/day7-final.md).
