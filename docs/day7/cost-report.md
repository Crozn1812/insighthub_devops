# Weekly practice cost report

Scope: retained local practice snapshots, not an AWS/cloud invoice or a claim
that electricity/hardware are free. Avoid adding duplicate snapshots or judge
usage to target usage. Provider Ollama API USD is **0** in the observed local runs.

| Category | Observation | Scope/evidence |
|---|---|---|
| AWS | NOT_EXECUTED_NO_AWS | No queried cloud invoice or executed plan/cost estimate |
| Historical target 70 | 39,004 input / 6,805 output tokens | [Historical cost](../evidence/day6-cost-final.json); separate from judges |
| Historical allocation | $0.06, six allowed calls | [Adapter cost](../evidence/day6-finops-cost-workloads.json); not provider billing |
| New compliance target 70 | 25,986 input / 3,555 output measured across 46 requests; 24 usage unavailable/null | [Per-request proof](../evidence/upstream/security-compliance-70.json); no invented tokens |
| Native caps | InsightHub $1 / bot $0.50 / coding $1 | DB-backed native max_budget; restored after denial tests |
| Native planning rate | $0.000001/input + $0.000002/output token | Budget accounting only; zero-cost-model bypass requires explicit planning rate |
| Native spend snapshot | InsightHub $0.034816 / bot $0.000949 / coding $0.000385 | [Snapshot at its own timestamp](../evidence/upstream/native-attribution.json); later baseline calls not retroactively included |
| Native enforcement | Three allowed, six concurrent zero-cap 429 denials | [Actual proof](../evidence/upstream/native-budget-runtime.json); positive-cap hard atomicity not tested |
| Resources | Actual sampled aggregate Ollama RSS and target durations | Not exclusive per-request RAM or GPU/electricity |
| Power/hardware/labor | Unmeasured | No fabricated dollar estimate |

Native rolling DB totals include earlier zero-rate calls; total tokens times the
new rate do not reconstruct all-time spend. Current dashboards distinguish
provider zero, positive planning spend/caps and workload attribution. Historical
adapter caps ($0.10/$0.02/$0.02) and atomic allocation are a separate implementation.
This report summarizes available practice evidence, not an exhaustive weekly
provider/judge/machine ledger or the required Infracost estimate on a live AWS plan.
