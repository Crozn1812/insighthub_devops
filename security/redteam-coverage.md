# Day 6 red-team coverage

Pinned tooling: Promptfoo 0.123.1. IDs below were verified against
`promptfoo redteam plugins --ids-only` and the pinned CLI strategy catalog.

| Risk | Promptfoo plugin / strategy | Why it maps | Test path | Expected protection layer |
| --- | --- | --- | --- | --- |
| Direct prompt injection | `jailbreak-templates` strategy over the local plugins | Wraps generated probes in direct attempts to replace the application's policy. | Promptfoo HTTP target → real `/chat` | Input policy, hardened system prompt, output policy |
| Indirect prompt injection | `indirect-prompt-injection` (validated ID; remote-only in 0.123.1) | Models instructions arriving from untrusted content. It was not represented as locally generated Promptfoo output. | `scripts/rag-poisoning-eval.py` through `/documents` → worker → `/chat` | Document trust boundary, context isolation, output policy |
| RAG poisoning | `rag-poisoning` (validated ID; remote-only in 0.123.1) | Targets corrupted retrieval knowledge. It was not represented as locally generated Promptfoo output. | Real application helper through `/documents` → worker → `/chat` | Ingestion controls, retrieval isolation, prompt boundary |
| PII disclosure | `pii:direct`, `pii:api-db`, `pii:session`, `pii:social` | Requests sensitive data through four locally supported Promptfoo PII paths. | Promptfoo HTTP target → real `/chat` | Input/output PII detection and least-data retrieval |
| Excessive agency | `excessive-agency` | Tests whether a read-oriented assistant claims or performs actions beyond its authority. | Promptfoo HTTP target → real `/chat` | Permission boundary, no tools in RAG endpoint, response policy |

## Standards mapping

- OWASP LLM Top 10 2025: LLM01 Prompt Injection (direct and indirect), LLM02
  Sensitive Information Disclosure (PII), LLM04 Data and Model Poisoning (RAG
  poisoning), and LLM06 Excessive Agency.
- OWASP Agentic risks: ASI01 Agent Goal Hijack, ASI02 Tool Misuse and Exploitation,
  ASI03 Identity and Privilege Abuse, and ASI04 Agentic Supply Chain Vulnerabilities.

With both remote-generation disable flags set, Promptfoo 0.123.1 reported
`hijacking`, `system-prompt-override`, `indirect-prompt-injection`, and
`rag-poisoning` as remote-only. They were excluded from the local generated artifact
rather than fabricated. The real helper uploads a controlled document, waits for that
exact ID, retrieves it through chat, deletes it, and verifies that no document or stale
retrieval context remains.
