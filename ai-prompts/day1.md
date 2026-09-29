# Day 1 prompt log

## Prompt 1 — Hoàn thiện toàn bộ 7/7 yêu cầu Day 1 trên branch day1-refactor

> Hoàn thiện toàn bộ 7/7 yêu cầu Day 1 trên branch `day1-refactor`, dựa trên phương án Redis/ARQ giữ job, volume chung giữ payload và ingestion-worker tái sử dụng `process_document()`. Giữ schema DB, fixture và dependencies pin/hash; thêm worker Dockerfile/entry point, retry failed-only, xử lý timeout enqueue, log JSON, Compose năm service, test, CRLF wrapper và evidence. Không sửa Day 2--7, frontend, verifier, volume/dữ liệu; không gọi provider mất phí, commit hay push. Kiểm tra runtime upload 202 dưới một giây, ready dưới 30 giây và chat vẫn hoạt động.

- **Vì sao dùng prompt:** chuyển starter ingestion đồng bộ thành pipeline Day 1 có API admission và worker riêng nhưng không mở rộng kiến trúc ngoài rubric.
- **Phản hồi/thay đổi chính:** thêm Redis, ARQ queue, payload volume, worker non-root và route upload 202; worker gọi chung `process_document()`, không có implementation ingestion thứ hai. Thêm retry thủ công cho `failed` và event `ingestion_completed` có ID/timestamp/status.
- **Review/quyết định:** chấp nhận job chỉ chứa document ID và payload `<id>.payload`; chấp nhận giữ payload khi enqueue timeout. Bác bỏ biến pipeline thành `async def` đơn thuần vì không tách worker process, và không thêm automatic retry Day 1.
- **File ảnh hưởng:** Compose, API config/router/error/queue/payload/worker, `ingestion-worker/`, lock dependency và test integration/queue.
- **Test/bằng chứng:** runtime hiện tại có năm service healthy; upload fixture 202, worker ready, chat source và JSON completion event được verifier kiểm tra.
- **Giới hạn còn lại:** fixture không đánh giá chất lượng semantic retrieval; không có outbox/reconciler cho crash sau DB commit trước enqueue.

## Prompt 2 — Thực hiện final review Day 1 trước commit

> Thực hiện final review Day 1 trước commit. Review toàn bộ diff như reviewer độc lập: correctness, race condition, payload lifecycle, retry semantics, worker Dockerfile/entry point thực sự được Compose dùng, một implementation ingestion, log không lộ payload/secret. Kiểm tra retry failed-only, status pending/ready, missing ID, payload missing/hash/pipeline mismatch, enqueue failure/timeout và replay. Thêm test lỗi tạm thời lần đầu rồi retry cùng ID đạt ready không trùng chunks. Chạy backend, regression, pytest/verifier nếu dependency có; không commit/push hay sửa Day 2--7.

- **Vì sao dùng prompt:** xác minh các quyết định async trước submission thay vì chỉ dựa vào smoke cũ.
- **Phản hồi/thay đổi chính:** healthcheck Compose đổi sang packaged worker entry point; retry đọc payload có giới hạn; bổ sung test pipeline mismatch và test provider lỗi lần đầu, retry cùng document ID đạt `ready` với một chunk.
- **Review/quyết định:** xác nhận `FOR UPDATE SKIP LOCKED` marker không ghi đè `ready`, ARQ `keep_result=0` giải phóng stable job ID cho retry, và whitespace runtime vẫn failed là invalid input, không phải recovery thành công.
- **File ảnh hưởng:** `docker-compose.yml`, `payloads.py`, integration tests, milestone contract test, review evidence và tài liệu Day 1.
- **Test/bằng chứng:** `make test-backend` hiện tại 67/67 PASS; milestone có retry provider-failure-to-ready và assertions chống duplicate chunk.
- **Giới hạn còn lại:** Ruff và Mypy chưa chạy theo quyết định của người thực hiện.

## Prompt 3 — Verifier Day 1 hiện chạy được nhưng báo INCOMPLETE vì thiếu đúng bốn milestone scenarios

> Verifier Day 1 hiện chạy được nhưng báo INCOMPLETE vì thiếu đúng bốn milestone scenarios: `test_duplicate_or_invalid`, `test_empty_input`, `test_refactor_regression`, `test_worker_ingests`. Đọc verifier, verification contract và tests milestone; bổ sung đúng tên, assertion thực, dùng biến môi trường verifier lúc chạy, không skip/xfail hay sửa verifier. Kiểm tra zero-byte upload, poll document ID mới đến ready, invalid/replay contract, health/readiness và chat/retrieval sau refactor; giữ các test async upload/retry hiện có.

- **Vì sao dùng prompt:** hoàn tất contract test mà verifier yêu cầu thay vì tạo tên test hình thức.
- **Phản hồi/thay đổi chính:** thêm bốn scenario, chuyển URL sang helper runtime thay vì đọc `os.environ[...]` lúc import, và làm nội dung retrieval duy nhất bằng UUID sau khi test phát hiện collision giữa các fixture giống nhau.
- **Review/quyết định:** chấp nhận invalid extension là bằng chứng hợp lệ cho `duplicate_or_invalid`; không giả định hai upload giống nhau phải cùng ID. Giữ poll bounded cho đúng ID và source/context đúng document mới.
- **File ảnh hưởng:** `tests/milestones/day1/test_async_contract.py`; evidence Day 1 được tạo lại với fingerprint/timestamp runtime hiện tại.
- **Test/bằng chứng thực tế:** backend **67/67 PASS**; milestone **6/6 PASS**; verifier Day 1 **PASS**, `runtime_verified=true`. Verifier smoke ghi nhận pipeline runtime, upload document mới và event worker tương quan.
- **Giới hạn còn lại:** fixture không đánh giá chất lượng semantic retrieval. Ruff: chưa chạy theo quyết định của người thực hiện. Mypy: chưa chạy theo quyết định của người thực hiện.
