# Security coverage — bounded Day 6 scope

This maps the requested **2025** LLM taxonomy, not the subsequently published
2026 renumbering. TESTED means a runtime check executed, not universal safety
or that every check passed. Final raw results remain authoritative.

| OWASP LLM Top 10 2025 | Label | Evidence/scope |
|---|---|---|
| LLM01 Prompt Injection | TESTED | Direct cases, runtime refusal, real indirect poisoned-document retrieval |
| LLM02 Sensitive Information Disclosure | TESTED | PII cases, policy diagnostic, input/output guard tests |
| LLM03 Supply Chain | DESIGN-ONLY | Pinned dependencies, local image/version; no signature/SBOM/CVE runtime assessment |
| LLM04 Data and Model Poisoning | PARTIAL | Retrieval-document poisoning tested; training/model weights not assessed |
| LLM05 Improper Output Handling | PARTIAL | Citation normalization and output sanitization; downstream executable/HTML sinks not assessed |
| LLM06 Excessive Agency | TESTED | Refusal and native rubric corpus; judge calibration limitation explicitly retained |
| LLM07 System Prompt Leakage | TESTED | Actual earlier leak, remediation probes and deterministic protected-output checks |
| LLM08 Vector and Embedding Weaknesses | PARTIAL | Embedding identity validation and retrieval sanitizer; cross-tenant/vector-index authorization not tested |
| LLM09 Misinformation | PARTIAL | Ten benign expectations and factual/citation sanity; no broad correctness assessment |
| LLM10 Unbounded Consumption | PARTIAL | Output/input bounds and scoped admission quotas; no cluster-wide load/exhaustion test or energy metering |

| Agentic mapping | Label | Scope |
|---|---|---|
| ASI01 Agent Goal Hijack | PARTIAL | Direct/indirect instructions tested in RAG; no autonomous multi-step agent |
| ASI02 Tool Misuse and Exploitation | PARTIAL | No chat execution tools; external-action claims tested, actual privileged tool execution N/A |
| ASI03 Agent Identity and Privilege Abuse | PARTIAL | Three FinOps scoped bearer identities and budget admission; agent delegation/privilege escalation not assessed |
| ASI04 Agentic Supply Chain Vulnerabilities | DESIGN-ONLY | Image/version pinning only; tools/model supply-chain attestation absent |

Sources: [OWASP 2025 LLM taxonomy](https://genai.owasp.org/llm-top-10/),
[OWASP Agentic crosswalk](https://github.com/GenAI-Security-Project/crosswalk/blob/main/agentic-top10/Agentic_OWASP_NHI.md).
