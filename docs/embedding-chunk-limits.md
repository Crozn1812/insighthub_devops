# Bounded local embedding chunks

Ollama model metadata reports mxbai-embed-large context 512 and dimension 1024.
CHUNK_SIZE remains the logical target. For this provider/model only, the effective
document budget is min(CHUNK_SIZE, 400), measured conservatively as UTF-8 bytes
after NFKC normalization. This is an estimator, not an exact tokenizer guarantee;
112 context positions provide additional margin. No tokenizer/model dependency
is downloaded. Other providers retain existing chunk behavior.

Chunks preserve normalized text order, prefer word boundaries, split unusually
long words at Unicode character boundaries and remain nonempty. Overlap uses the
same estimator: min(CHUNK_OVERLAP, effective budget / 4), normally 100. Formatting
normalization remains the existing whitespace-joining behavior. No truncation,
model, dimension, embedding identity or database schema changes.

The bounded pipeline has a distinct version. Supported retry can upgrade failed
records from the exact legacy pipeline with identical settings/embedding identity
only after retained payload hash/size verification. Ready records are not changed;
unrelated pipeline or modified/missing payload is still rejected. Successful retry
uses the same document ID and transactionally replaces chunks.

Ollama still receives truncate=false and rejects any unsupported input rather
than silently losing text. Provider error bodies and uploaded contents are never
logged by this fix. Tests use synthetic English, Vietnamese, Unicode and dense
text; TXT/MD/PDF share the chunking stage after extraction.

## Verified locally

- Linux API unit suite: 130 passed, with 97 passing subtests.
- Only API and ingestion-worker images were rebuilt and rolled out; both Ready.
- Supported retry of existing failed documents 45, 46 and 47 completed: each
  ready, 124 chunks, no error_code, stored vector dimension 1024. Retained payload
  hashes were unchanged; maximum chunk estimator value was 400.
- Harmless public-format RAG query returned HTTP 200, real mode and a citation
  from the retried document. Private document contents were not printed.
- Synthetic 6,195-byte Markdown upload returned HTTP 202, became ready with
  21 chunks in 9.1 seconds, and returned the correct fact with its citation.
- API readyz HTTP 200, real mode/db=true; Redis PONG; actual Ollama generation
  and embedding HTTP 200 with 1024-dimensional finite vectors, truncate=false.
- Two worker restarts during verification were caused by existing ARQ health
  probes timing out on Redis connections. The worker subsequently remained Ready
  and completed ingestion. Probe settings and other services were not changed.

The conservative estimator trades larger chunk counts for input safety. It is
not the exact model tokenizer; pathological input can still be rejected by the
provider, and provider rejection remains explicit rather than silently truncated.