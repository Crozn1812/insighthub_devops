# Acceptance blockers and limitations

Upstream requirements govern acceptance; partial verifier PASS is not full rubric.

- No authorized AWS account/credits: EKS, managed DB/cache, IRSA, plan/apply,
  cloud smoke/tags remain NOT_EXECUTED_NO_AWS. Static CI is not cloud deployment.
- Actual learner/trainer must complete quiz, self-evaluation and classroom
  review/submissions. Upstream author's personal trainer exemptions are not ours.
  Roadmap MLOps was chosen by the learner; its trainer-form entry is still pending.
- Slack webhook/app/workspace, public event URL, channel alerts and three live
  Slack intents remain unverified. Local tests/capture do not establish LIVE.
- Mandatory Loom URL/video is absent. Script preparation is not a recording.
- Health is local HTTP 200; public reviewer accessibility is not established.
- Day 6 has no HIGH/CRITICAL in the compliance run but benign-001 FAIL; fresh
  source-bound initial/all-passing final reports and fresh verifier full observation
  contract remain unmet. Verifier INCOMPLETE/runtime_verified=false.
- Native LiteLLM 1.98.0 responds 200 at `/health/liveliness`; its `/healthz`
  responds 404. Deployment health is verified, but the exact Day 6 example
  acceptance endpoint is a documented compatibility deviation.
- NeMo uses regex rails, not semantic safety guarantees. Corpus/model judge
  nondeterminism, encoded attacks and PII/tenant isolation retain residual risk.
- Native budget proof is concurrent zero-cap denial. Positive-cap atomic
  exhaustion/overshoot is unverified with asynchronous native spend updates.
- USD 0 provider excludes hardware/power/GPU/labor; planning rates and historical
  allocation credits are not invoices. RSS/duration is sampled, not exclusive.
- Single local node, port-forwards/relay/private credentials need reboot recovery.
  WSL limitations and transient readiness failures are retained, not hidden.
- Ruff/mypy are not installed solely for submission; actual availability is reported.

See [matrix](upstream-compliance-matrix.md) and [manual actions](day7/remaining-manual-actions.md).

## Final native NeMo probe (2026-10-05)

[Current native proof](evidence/upstream/nemo-final-runtime.json): **4 PASS / 1 FAIL**. Benign input allowed, direct injection and poisoned context blocked; real native HTTP identity failure produces API503 in an isolated current handler. The output rail allowed a behavior-override sentence that the probe expected to block. Output regexes currently cover PII/key markers, not general output injection; semantic checks are disabled. This is a documented native guardrail gap, not a unit-test failure or a substituted custom-guard PASS. No further remediation loop was performed. Literal MH6 remains enabled/configured with actual allowed/blocked proof; complete protection and Day 6 acceptance are not claimed.
