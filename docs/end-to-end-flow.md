# End-to-end request and data flow

1. Web/API accepts supported, nonempty uploads within 10 MB.
2. API validates, stores recoverable payload/document, enqueues ARQ, returns 202.
   Enqueue failure is an error, not a successful indefinitely pending job.
3. Separate worker chunks, embeds and stores consistent vectors/metadata, then
   marks ready and emits a structured completion event. Bounded transient retry
   and idempotent replay preserve data; permanent failures become failed.
4. Chat checks request/NeMo input rails, embeds question, retrieves pgvector
   chunks, sanitizes retrieved instructions and checks context rails.
5. Native InsightHub key routes generation via LiteLLM to local Ollama qwen3:4b.
   Structured output, citations and output rails precede the response.
6. Real Prometheus metrics feed Grafana. Provider USD 0 and planning spend are
   separate series. No cloud invoice or power measurement is implied.
7. Signed ChatOps events read MCP facts; guarded advice cannot authorize actions.
   Permission/approval/dedup/lease/audit govern scale and durable delivery.

No embedding identity change or fixture mixing. Slack LIVE needs user workspace
authorization. See [architecture](final-architecture.md),
[security](final-security-status.md), [FinOps](final-finops-status.md), and
[matrix](upstream-compliance-matrix.md).
