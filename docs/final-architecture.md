# Actual local architecture

User → Next.js web → FastAPI API → Redis/ARQ → separate ingestion worker
→ PostgreSQL 16 + pgvector.

Chat → embed/retrieve → context sanitization → native LiteLLM 1.98.0 virtual key
→ local Ollama qwen3:4b → structured answer/citation/output protection.
NeMo 0.24.1 checks input, retrieved context and output; outage fails closed.
Embeddings use Ollama mxbai with the existing dimension/revision identity.

App/worker/dependency exporters → Prometheus → Grafana/Alertmanager.
Native FinOps PostgreSQL → read-only accounting exporter → Prometheus/Grafana.

Five base services are web/api/postgres/redis/ingestion-worker. Docker Desktop
Kubernetes hosts namespaces insighthub-dev and monitoring. Native LiteLLM, NeMo,
accounting DB/exporter run locally in Docker with genuine Kubernetes endpoints;
Ollama runs on the host. EndpointSlice and legacy Endpoints share real container
IPs; installed Prometheus discovery currently uses legacy Endpoints.

Upload returns 202 after successful enqueue; payload survives the request and
worker persists chunks consistently before ready. Retry is transient-only,
bounded and idempotent. DB schema and embedding identity remain unchanged.

ChatOps validates Slack HMAC/replay, uses durable Redis processing/lease/recovery,
reads Kubernetes/Prometheus MCP facts, and adds optional guarded model advice.
Facts and permission checks remain authoritative. Scale requires bound, expiring,
single-use approval. Slack delivery can be at least once after a crash;
exactly-once delivery and Slack LIVE are not claimed.

Terraform describes EKS/RDS/ElastiCache/IAM and OIDC workflows, but only static
and local checks ran. Cloud resources are not deployed; local health is not HA
or public reviewer access. Private runtime files/Kubernetes Secrets retain keys.
