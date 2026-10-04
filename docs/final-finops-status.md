# Final FinOps status

Local-only LiteLLM **1.98.0**, Docker image
`docker.litellm.ai/berriai/litellm:v1.98.0`, digest
`sha256:20b5044b619055374061a6d5b7b08754cad75aeabbf82ddf4f69cc0cf80ddaf4`.
Gateway admission và proxy dùng cùng image; underlying model Ollama qwen3:4b
think=false. API nói OpenAI-compatible protocol nhưng không gọi cloud.

| Workload | Evidence lịch sử | Kết quả |
|---|---|---|
| InsightHub | day6-finops-insighthub.json | actual deployed chat, utility/citation PASS |
| Bot | day6-finops-workloads.json | 200/200/429; identity và token usage riêng |
| Coding | day6-finops-workloads.json | first 200; concurrent near-threshold một 200, một 429 |

Ba scoped bearer identities nằm ngoài repo. Đây là equivalent identity/budget
adapter quanh LiteLLM, **không phải native DB-backed LiteLLM virtual-key admin**.
SQLite persistent ledger, `BEGIN IMMEDIATE` admission không overshoot khi
concurrent. Failure vẫn giữ allocation để tránh retry bypass; budget demo đã
consumed, không reset. Chỉ chấp nhận model local đã pin, non-streaming, bounded
request/output. Xem [implementation](../finops/README.md).

**Provider cost** local Ollama = USD 0. **Planning allocation**: 10,000 micro-USD
mỗi admitted request, không phải hóa đơn hay token-based provider pricing.
InsightHub cap 100,000; Bot/Coding mỗi workload 20,000. Sáu successful historical
calls tiêu thụ planning USD 0.06. Ledger export Day 6 có 9 admission events
(6 allowed, 3 denied); Day 7 thêm hai admitted benign calls, không ghi đè snapshot.

Token accounting lấy usage thật/provider IDs; final evaluation cost có đủ 70
records, 39,004 input + 6,805 output tokens, budget config USD 1, actual provider
USD 0. Hai lost-body records dùng actual counter deltas có provenance riêng.
Gateway workload tokens và evaluator-judge tokens không bị nhập chung vào target
evaluation totals. Không tuyên bố cloud billing hoặc electricity free.

Resource accounting là sampled Windows aggregate Ollama RSS và duration;
không exclusive per-request RAM, không GPU memory, không điện năng. Hai missing
scan responses dùng target latency và run-wide sampled peak có nhãn rõ.

Grafana UID `insighthub-day6-finops`, 10 panels: workload requests/tokens,
admission/budget metrics và provider cost riêng. Live dashboard API/Prometheus
scrape được xác nhận Day 6; Day 7 service health 200. Screenshots manual pending.

Evidence: [cost](evidence/day6-cost-final.json),
[workload cost](evidence/day6-finops-cost-workloads.json),
[ledger](evidence/day6-finops-ledger.json),
[monitoring](evidence/day6-monitoring-runtime.json),
[new bounded checks](evidence/day7-runtime.json).
