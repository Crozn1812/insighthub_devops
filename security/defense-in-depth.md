# Day 6 defense in depth

1. Pydantic request bounds reject empty, oversized, unknown-field, and invalid `top_k` requests.
2. Normalized deterministic signals block direct prompt override and prompt-extraction attempts before provider generation.
3. The generation envelope names trusted system policy, untrusted retrieved documents, and the trusted user question explicitly.
4. Retrieved chunks containing override/forced-output instructions are excluded from generation; only a safe filtered placeholder is exposed for audit. Exact duplicate factual chunks are collapsed before generation.
5. A dedicated runtime guard model was investigated but not added: concurrent CPU-local model grading materially harms latency, and the smaller model showed one clear-case false negative. Deterministic layers fail closed for explicit attacks.
6. Input PII is blocked and output email, phone, credential, token, prompt-leak, and model reasoning content are redacted, removed, or refused. A bounded 1024-token response budget prevents the real target's final answer from being truncated.
7. RAG chat blocks external-action requests and has no bridge to Day 5 ChatOps mutation authority.
8. `insighthub_guardrail_decisions_total{stage,decision,category}` records only bounded labels; it never labels prompts, users, filenames, request IDs, or PII.

These controls reduce risk; they do not claim perfect detection.
