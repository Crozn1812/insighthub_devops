# InsightHub

InsightHub là RAG notebook cho bài thực hành AI-Native DevOps DO2603: upload
tài liệu `.txt/.md/.pdf`, xử lý ingestion qua queue và hỏi đáp với sources.
Dự án dùng starter0.2.3/specification3.3 và đã phát triển qua Days1–6.
Day7 tổng hợp tài liệu/evidence, không mở lại security remediation.

**Final state:** local runtime usable; technical implementation complete with
limitations. **Day6 acceptance FAIL / COMPLETED_WITH_LIMITATIONS**: official
scan70 cases có66PASS/2FAIL/2ERROR, unresolved HIGH attack-009/016, ERROR
attack-002/004; CRITICAL0. Official verifier `runtime_verified=false`.
Day7 fresh runtime checks7/7 và offline unit/artifact tests99/99 PASS không thay
đổi kết quả security này. Trainer acceptance và manual evidence còn pending.

## Architecture / technologies

```text
User → Next.js Web → FastAPI API → Redis/ARQ → Ingestion worker
                                                ↓
                                     PostgreSQL16 + pgvector
Chat → API → embed/retrieve → sanitize context → scoped budget gateway
     → LiteLLM1.98.0 → local Ollama qwen3:4b → output guardrails → citations
App/worker/exporters/gateway → Prometheus → Grafana / Alertmanager
```

Upload trả202 sau enqueue; worker lưu chunks/embedding và chuyển document ready.
Embedding dùng mxbai-embed-large với identity nhất quán; không trộn fixture/real
index. Current runtime là Docker Desktop Kubernetes (`insighthub-dev`,
`monitoring`) cộng Ollama host và local FinOps containers; **không AWS production**.
Terraform/cloud claims chỉ STATIC_VALIDATION_ONLY; AWS NOT_EXECUTED_NO_AWS.

## Setup / operation

Đọc [GETTING_STARTED](GETTING_STARTED.md) để setup từ đầu, provider/config/storage
và troubleshooting. Compose là môi trường local riêng; không chạy Compose
redeploy lên current Kubernetes hoặc overwrite `.env` đang dùng. Giữ secrets,
kubeconfig và keys ngoài repo; không in `docker compose config` đầy đủ.
Không tải model/cài package/tạo cloud resources trong closeout.

Current API được forward tại localhost18000; `/readyz` kiểm tra DB/mode.
Web và dashboards là ClusterIP Services, dùng port-forward theo
[demo runbook](docs/demo-runbook.md). Node access hiện qua temporary recovery
relay; không reset cluster khi transport lỗi. Evidence ghi thời điểm quan sát,
không hứa services còn hoạt động sau host restart.

## Security, observability, ChatOps, FinOps

- [Security status](docs/final-security-status.md): request/context/output
  controls, citation hardening, unresolved findings và judge limitations.
- [Architecture](docs/final-architecture.md): actual local topology và
  Prometheus/Grafana/Alertmanager. Historical local alert incidents PASS;
  external Slack delivery/manual screenshots chưa hoàn tất.
- ChatOps: signed event HMAC/replay checks, Redis durable queue/dedup,
  approval binding và constrained Kubernetes actions; historical local tests
  PASS. Live Slack chưa verified; Day7 không gửi Slack hoặc mutate cluster.
- [FinOps](docs/final-finops-status.md): three scoped workload identities,
  atomic persistent budget admission, actual tokens. Provider Ollama costUSD0
  tách khỏi planning credits và sampled RSS/duration; không cloud billing,
  GPU/electricity accounting hoặc native LiteLLM key-admin claim.

## Review / evidence navigation

CI/CD gồm GitHub Actions baseline và local-first IaC workflow: Terraform static
validation/policy, Helm lint/render và local deployment evidence. Không có AWS
apply hoặc cloud-runtime claim. Xem `.github/workflows/` và `infra/`.

Repository structure: `web/` UI; `api/` backend/security/providers;
`ingestion-worker/` ARQ worker; `chatops-bot/` signed ChatOps;
`infra/` Terraform/Helm/schema/policies; `observability/` rules/dashboards;
`security/` immutable dataset và frozen evaluator tooling; `finops/` gateway/
budgets/tests; `docs/` reviewer docs; `docs/evidence/` compact tracked package;
`tests/` milestone/verifier regression; `ai-prompts/` decision logs.

| Tài liệu | Nội dung |
|---|---|
| [Final architecture](docs/final-architecture.md) | Service topology, trust boundaries, image/runtime |
| [End-to-end flow](docs/end-to-end-flow.md) | Upload→worker→RAG→metrics, evidence scope |
| [Final test matrix](docs/final-test-matrix.md) | Historical Days1–6 và fresh Day7 results riêng |
| [Limitations / risks](docs/project-limitations.md) | Remaining risks, manual/cloud/tool gaps |
| [Demo runbook](docs/demo-runbook.md) | Commands/UI, expected results và fallback |
| [Evidence index](docs/evidence/README.md) | Tracked sanitized artifacts Days1–7 |
| [Day7 closeout](docs/evidence/day7-final.md) | Historical completion state và final checks |
| [Submission manifest](SUBMISSION.md) | Branch, commit/PR checkpoint và submission instructions |
| [Project specification](Running-Project-Specification-Student.md) | Rubric/acceptance gốc |
| [Verification contract](scripts/VERIFICATION_CONTRACT.md) | Official verifier scope |
| [Lab guides](docs/lab-guides/README.md) | Teaching workflow Days1–7 |

Most `evidence/*` is gitignored, với một số exceptions. `docs/evidence/` là
sanitized tracked package với source hashes và explicit projections; large raw
Promptfoo/intermediate logs giữ local. Historical failed/invalid runs được giữ,
không xóa hoặc relabel PASS. Xem provenance/limitations trước khi đọc derivatives.

Human review còn: screenshots/quiz/screencast, Slack integration, trainer
acceptance, security HIGH/errors, evidence packaging và review toàn bộ diff.
Day7 đã dừng trước Git writes; final-submission workflow riêng được user cho phép
commit/push và mở PR. Technical readiness không thay acceptance; không tuyên bố
production-ready hoặc full-rubric PASS. Xem [SUBMISSION.md](SUBMISSION.md).
