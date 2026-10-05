# Current test and verification matrix

Counts represent distinct executed suites, not full upstream acceptance. Worker
and API security tests are subsets of the API146 and must not be added again.

| Check | Actual result | Scope |
|---|---|---|
| API pytest with real isolated PostgreSQL | 146 PASS +97 subtests; zero skips/failures | Current API/worker/provider/HTTP/guardrail/configuration tests |
| Worker transient retry | 4 PASS included above | Bounded backoff/final failure/permanent no-retry; not duplicate count |
| ChatOps Linux/Redis | 62 PASS | Signature/permissions/approval/dedup, real durable recovery and completed-action redelivery |
| Existing FinOps unittest | 12 PASS | Historical adapter concurrency plus retained artifact validators; native proof separate |
| Fork verifier helper regressions | 69 PASS | Does not mean all official milestone contracts pass |
| Evaluator mechanics Node | 13 PASS | Generic schema/attribution/retry; no security model scan |
| Real-provider fault proxy pytest | 3 PASS | Explicit503, sanitized transport failure, auth-preserving real response forwarding |
| Promtool |16 rules valid; 7 rule scenarios PASS; CRD sync PASS | Full finite1h baseline/10m offset, volume and2m persistence guards |
| Native runtime proof |3 allowed /6 denied;6 guard checks; coding3 isolated tests | Not added to unit total; observed native max_budget and workload scope |
| Full compliance70 |69 PASS /1 benign FAIL /0 ERROR /0 HIGH/CRITICAL | Finite unchanged corpus; predates subsequent UUID/config alias corrections |
| Ruff / mypy | UNAVAILABLE | Not installed solely for submission |

Current unit/mechanics total: **305 PASS**, plus **97 subtests**, zero final
assertion failures (146+62+12+69+13+3). Seven promtool scenarios and earlier isolated
coding tests are reported separately. Intermediate infrastructure/transport
failures and historical99-test closeout remain retained, not silently discarded.

[Official reports](evidence/upstream/official-verifiers.json) preserve exact
upstream PASS/INCOMPLETE status and source/time binding. A partial-runtime PASS
does not waive AWS, Slack LIVE, quizzes, Loom or trainer rubric. Day6 formal
fresh-source/every-case/live-observation acceptance is unmet despite no HIGH.

Current additional native NeMo proof: 4 PASS/1 FAIL (unsafe output override allowed). This is separate from 305 passing unit/mechanics tests and remains a known local control gap.
