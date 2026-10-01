# Day 6 evaluation dataset selection

The immutable-style generated corpus retains all 262 Promptfoo-native attacks and
the 10 explicit benign cases. The primary execution dataset is a bounded,
reproducible evaluation of 60 attacks plus all 10 benign cases; it does not claim
that the remaining corpus was executed.

Selection happens before remediation results are known. Within each group, cases
are ordered by their original zero-based position in `redteam-generated.yaml` and
the first required entries are selected:

- Direct injection: 20 `jailbreak-templates` cases, four from each of the five
  configured plugins.
- PII: 30 `basic` cases: eight each from `pii:api-db` and `pii:direct`, and seven
  each from `pii:session` and `pii:social`.
- Excessive agency: the first 10 `basic` `excessive-agency` cases.
- Benign: all 10 explicit regression cases.

Every selected case retains its original `corpus_case_id`, plugin, strategy, and
prompt. The remaining generated cases stay available for extended or nightly
scans in `day6-generated-corpus.json`.

Indirect/RAG poisoning is not represented as a supported native local Promptfoo
plugin. It remains a separate mandatory application-level test using
`scripts/rag-poisoning-eval.py` through real upload, ingestion, retrieval, and
Ollama generation.
