# Day 3 Local Kubernetes Evidence

- Observed at: `2026-09-30T07:57:57+07:00`
- Environment: **LOCAL Docker Desktop Kubernetes — NOT EKS**
- Context: `docker-desktop`
- Namespace: `insighthub-dev`
- Helm release: `insighthub` (`deployed`)
- Workloads: web, API, ingestion-worker, PostgreSQL, and Redis all `1/1 Ready`
- Services: web, API, PostgreSQL, and Redis are `ClusterIP`
- PVCs: `data-insighthub-postgres-0` and `insighthub-payloads` are `Bound`
- Database: `vector` extension present; tables `embedding_index`, `documents`, and `chunks` present
- Redis: `PING` returned `PONG`
- API `/healthz`: HTTP 200
- API `/readyz`: HTTP 200
- Web `/api/health`: HTTP 200
- Official local smoke: PASS; upload returned HTTP 202 and the asynchronous document reached `ready`; chat and metrics checks passed

No password, Secret data, token, or kubeconfig is included in this evidence.
