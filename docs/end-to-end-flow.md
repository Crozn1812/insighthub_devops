# Luồng end-to-end và phạm vi đã kiểm chứng

1. Web gửi `.txt/.md/.pdf` đến `POST /documents`. API kiểm tra filename,
   loại file, rỗng và giới hạn 10 MB; lưu payload có giới hạn vào shared storage.
2. API lưu metadata `pending` rồi enqueue ARQ job qua Redis. Trả **202** khi
   enqueue thành công; lỗi enqueue không được trả thành công giả.
3. Ingestion worker riêng nhận document ID, lấy payload, chunk văn bản,
   tạo embedding đúng count/dimension/identity và ghi chunks/metadata nhất quán
   vào PostgreSQL + pgvector. Thành công chuyển `ready`; lỗi kiểm soát chuyển
   `failed`, không thêm trạng thái schema mới.
4. Worker phát JSON `ingestion_completed` với document ID, timestamp và ready.
   Replay phải không tạo chunk trùng. Retry user khác retry worker tự động;
   payload/hash/pipeline identity phải hợp lệ.
5. Client poll `GET /documents` theo ID vừa upload; không dùng document ready cũ.
6. Với chat, API kiểm tra request security; nếu từ chối sẽ không gọi generation.
7. API embed question bằng embedding identity hiện có, retrieve top-k chunks
   trong pgvector, lọc/sanitize mixed-content và metadata nguồn. Safe facts có
   thể được giữ trong khi bỏ instruction độc hại; context sạch rỗng sẽ refusal.
8. API gửi context qua scoped gateway. Gateway xác thực identity, atomic reserve
   planning credits trong SQLite, rồi gọi LiteLLM → Ollama qwen3:4b local.
9. Model trả structured answer. API kiểm tra protected-policy/PII output,
   chuẩn hóa citation theo nguồn đã retrieve, rồi trả answer, sources, contexts,
   latency và usage thật. Citation không chứng nhận tính đúng tuyệt đối của answer.
10. API/worker/exporters phát metrics; Prometheus scrape, Grafana hiển thị,
    Prometheus rules/Alertmanager dùng cho alerting local. Gateway ledger ghi
    workload, correlation ID, provider response ID, tokens và admission decision.

| Đoạn luồng | Evidence | Giới hạn |
|---|---|---|
| Upload → worker → ready → citation | [Day 1 runtime](evidence/day1-runtime.json), [implementation](day1-async-ingestion.md) | fixture lịch sử; Day 7 không upload mới |
| ARQ replay | [replay](evidence/day1-replay.json) | document 5; 2 replay; không tương đương crash recovery toàn hệ thống |
| Real local ingestion/retrieval | [Day 3 local](evidence/day3-local-k8s.md), [RAG poisoning](evidence/day6-rag-poisoning.json) | workload local cụ thể; không cloud |
| Mixed-content controls | [security summary](../security/final-security-summary.md) | Day 6 r2 document 23; không rerun Day 7 |
| Current RAG → gateway → model → citation | [Day 7 runtime](evidence/day7-runtime.json) | 1 benign RAG mới, 560 input / 48 output tokens; 42.656s, không phải latency SLA |
| Direct LiteLLM model request | [Day 7 runtime](evidence/day7-runtime.json) | 1 benign request, 25 input / 10 output tokens; không security retest |
| FinOps attribution/budget/concurrency | [Day 6 ledger](evidence/day6-finops-ledger.json), [workloads](evidence/day6-finops-workloads.json) | snapshot lịch sử; ledger live tiếp tục tăng, không reset |
| Observability | [Day 4 status](evidence/day4-status.md), [Day 6 monitoring](evidence/day6-monitoring-runtime.json) | dashboard/alerts lịch sử; Day 7 health mới |

Day 7 kiểm tra PostgreSQL accepting connections, Redis PONG, API db=true và
pod ready. Điều đó không thay thế lần chạy upload/worker end-to-end mới.
Day 6 security acceptance vẫn FAIL; không suy từ benign success thành secure PASS.
