# Day 5 prompt log

## Mốc 1 — Transport, security và durable queue

- Yêu cầu: xây nền tảng local-only gồm Slack raw-body HMAC, replay protection, Redis
  queue/dedup/retry, worker riêng và local capture transport.
- Quyết định chấp nhận: verify signature trước JSON, atomic Lua `SET NX EX` + enqueue,
  retry có giới hạn ba lần và process bot/worker tách riêng.
- Quyết định bác bỏ: không dùng Slack SDK/live token, không gọi MCP trong HTTP handler,
  không xóa queue mặc định để test; E2E dùng namespace Redis cô lập.
- Bằng chứng: 19 test Phase 5A pass; 20 signed request có ACK p95 32.049 ms và duplicate
  không được xử lý lại.

## Mốc 2 — MCP và ba read intent

- Yêu cầu: dùng MCP stdio thật với Prometheus 0.18.0 và Kubernetes 0.0.67 cho health,
  ingest-today và failing-pods.
- Quyết định chấp nhận: official Python MCP SDK 2.2.0, fixed tool/argument mapping,
  timeout và result shaping. Thêm metric không label từ PostgreSQL `created_at`, định
  nghĩa theo 00:00 Asia/Ho_Chi_Minh.
- Quyết định bác bỏ: không dùng kubectl hoặc Prometheus HTTP làm bot backend; chúng chỉ
  dùng cross-check. Không diễn giải tổng document hiện tại thành số tạo hôm nay.
- Bằng chứng: ba signed E2E event dùng MCP thật; kết quả khớp Prometheus, kubectl và
  PostgreSQL; 37 ChatOps test và 67 backend test pass.

## Mốc 3 — Permission, approval, audit và verifier

- Yêu cầu: ba permission tier, approval 60 giây single-use, mutator identity tối thiểu,
  controlled scale, structured audit và official Day 5 verifier.
- Quyết định chấp nhận: fail-closed action IDs, Redis token được hash trong key và bind
  exact user/action/arguments, Lua compare-and-delete, executor argv cố định không shell,
  namespaced Role chỉ get/patch exact API deployment/scale.
- Quyết định bác bỏ: không arbitrary kubectl, wildcard RBAC, Secret access, pod delete,
  namespace mutation, live Slack hoặc approval token trong audit.
- Bằng chứng: wrong-user/reuse bị deny; scale 1→2 quan sát được và restore 2→1; saved
  audit có allowed/denied/approval_required; milestone tests sinh fresh observations.

## Mốc 4 — Live Slack gate và finalization

- Yêu cầu: kiểm kê credential theo presence-only, chỉ chạy live Slack khi đủ credential
  và tunnel đã xác thực; nếu thiếu phải giữ blocker thủ công nhưng vẫn hoàn tất evidence,
  regression, Git và PR.
- Quyết định chấp nhận: giữ `PENDING_USER_SLACK_APP` vì bốn biến Slack đều không có và
  `ngrok` không khả dụng; thêm hướng dẫn setup tối thiểu cùng kế hoạch screencast không
  chứa secret. Unignore từng artifact Day 5 bằng negation hẹp, không mở rộng cả thư mục
  evidence.
- Quyết định bác bỏ: không tạo HMAC local rồi gọi là Slack live, không cài tunnel hoặc
  yêu cầu scope rộng, không giả lập screenshot/screencast, không ghi credential vào repo.
- Bằng chứng: source fingerprint vẫn là
  `e20a53b2b1f92521191d7465767bbe63d44842f1c8369d0292ea505c1d31dd39`;
  54 ChatOps test và 5 milestone test pass; Redis, Kubernetes workloads, monitoring và
  hai MCP backend được kiểm tra lại thành công.
