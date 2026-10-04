# Day 6 residual risks

- qwen3:1.7b is REJECTED_FOR_SECURITY_JUDGE: calibration demonstrated both false
  PASS and false FAIL. The one bounded qwen3:4b attempt matched 11/12 canaries;
  one unsafe mixed refusal/action response exhausted two invalid judgments.
  qwen3:4b is frozen as the more defensible local fallback, with
  EVALUATOR_LIMITATION=TRUE, not promoted as a fully validated judge.
- Native rubric expectations and all 70 dataset cases remain unchanged. Final
  failed verdicts/errors are retained without human adjudication or replacement.
- Protected overlap checks cover substantial literal/normalized disclosure,
  not arbitrary semantic paraphrase, encoded leakage or every language.
- Local embeddings/retrieval are not a multi-tenant isolation proof. RAG
  poisoning document 23 was cleaned up; that finite fixture is not exhaustive.
- FinOps identities are scoped bearer keys enforced by a local adapter around
  LiteLLM, not LiteLLM's native DB-backed virtual-key admin system. Local
  admission allocations are planning credits, not provider/electricity bills.
  Direct access to local Ollama outside that adapter is outside budget scope.
- Baseline token counts are recoverable from all 70 raw API responses, although
  the earlier normalized report omitted them. HTTP/provider transport IDs and
  an execution-time source fingerprint were not recorded. Derived evidence
  identifies actual Promptfoo record UUIDs explicitly as evaluation identifiers,
  never provider IDs. Review-workspace binding is separate from historical
  execution provenance. Missing provenance is never invented.
- Sampled host Ollama RSS excludes GPU memory and is aggregate, not exclusive
  per-request memory or cloud billing. Dashboard screenshots remain manual.
- AWS runtime is NOT_EXECUTED_NO_AWS; Terraform/cloud checks are
  STATIC_VALIDATION_ONLY. No paid provider or AWS resource was used.
- Image/model supply-chain signatures and full ruff/mypy validation are not
  attested by this local execution task.
