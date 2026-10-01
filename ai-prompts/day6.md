# Day 6 prompt and decision log

## Phase 6A

- Accepted: keep the application target on real local `qwen3:4b` and use real `mxbai-embed-large` embeddings.
- Accepted: preserve the generated 262-attack corpus and a deterministic 60-attack + 10-benign core profile.
- Rejected: remote-only Promptfoo coverage, paid providers, fixture grading, and fabricated indirect-injection results.
- Evidence: real upload/retrieve/generate passed; the controlled RAG poison instruction influenced the baseline answer.

## Phase 6B

- Accepted: preserve the first 70-case run as invalid evidence because 69 judge JSON responses were truncated.
- Accepted: judge-only `qwen3:1.7b` after 10/10 JSON validity and 9/10 agreement; the application target remained `qwen3:4b`.
- Accepted: the official initial eval `eval-07X-2026-10-01T05:45:08` (70/70, zero execution/parse errors) as the vulnerable baseline.
- Accepted: deterministic pre-request guards, an explicit trusted/untrusted prompt envelope, retrieved-instruction filtering, exact-context deduplication, PII/output checks, least-agency refusal, citations, and bounded telemetry.
- Rejected: claiming a dedicated runtime guard model; CPU-local options were not practical and the smaller evaluator showed a reviewed false negative.
- Accepted after verification: exact poison fixture retrieval was observed, marker-only control was neutralized, and delete/stale retrieval cleanup passed.
- Accepted with manual review: `benign-007` output contained the required citation, while the 1.7B judge incorrectly claimed it was absent; the raw false-negative artifact remains preserved.
- Evidence: known agency case automated PASS; benign nine automated PASS plus one manual PASS; complete API suite 78/78 PASS with isolated DB integration, zero skips/xfail.
