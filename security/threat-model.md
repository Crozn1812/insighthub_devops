# Day 6 local threat model

Trust boundaries: user input and uploaded/retrieved documents are untrusted.
The API owns retrieval and output controls; only real local Ollama generates
answers. Chat exposes no infrastructure execution tools. The FinOps admission
adapter authenticates each workload before LiteLLM routes to local Ollama.
Model output and judge output are both untrusted. Credentials stay user-local
or in Kubernetes Secrets and are excluded from evidence.

| ID | Threat and boundary | Mitigation | Evidence and remaining limit |
|---|---|---|---|
| T1 | Direct injection changes assistant behavior | Request guard, trusted/untrusted prompt separation, protected-output inspection | Frozen 70-case corpus plus direct-refusal sanity; semantic judge remains limited |
| T2 | Indirect injection crosses retrieval boundary | Bounded mixed-content sanitizer, fail-closed invalid content, preserve safe facts | Real uploaded/retrieved poisoning document 23; finite payload/language scope |
| T3 | RAG/data poisoning changes factual answer | Sanitize malicious instructions, deduplicate contexts, preserve citations | r2 poisoning security and utility PASS, deletion/no stale retrieval; training-data poisoning not exercised |
| T4 | PII/secret disclosure through requests or answers | Input/output detection and controlled redaction | PII corpus and guardrail tests; regexes do not prove complete PII coverage or tenant isolation |
| T5 | Excessive agency claims privileged external actions | Input guard; no action tools; semantic evaluation | Runtime agency refusal and corpus; qwen3:1.7b rejected, frozen qwen3:4b still has invalid judgments |
| T6 | System-policy extraction through generation | Structured final-answer generation and bounded protected-text detector | Policy sanity and deterministic output inspection; paraphrased/encoded disclosure may evade exact overlap |
| T7 | Resource/cost abuse exhausts local runtime | Bounded inputs/output; scoped persistent atomic admission allocations | FinOps runtime results recorded separately; planning credits are not electricity metering; direct Ollama access outside gateway is not governed |
| T8 | Model/provider/dependency supply-chain compromise | Pinned packages/image, local-only allowlist, no cloud fallback | LiteLLM 1.98.0 image digest recorded; signature verification, SBOM/CVE attestation and model training provenance are not completed |

Initial baseline, remediation and final run are separate artifacts. A FAIL is
never rewritten to PASS. Invalid transport runs do not establish a security
finding. Successful scoped tests do not certify security beyond the tested
local workload, model, documents and bounded dataset.
