# ChatOps — Day 5

Phase 5A cung cấp nền tảng local-only: Slack HTTP request được xác thực trên raw body
bằng HMAC-SHA256 trước khi parse JSON; timestamp chỉ hợp lệ trong cửa sổ 5 phút
(cho phép lệch tương lai tối đa 30 giây). Event hợp lệ được deduplicate và enqueue
nguyên tử vào Redis, vì vậy HTTP handler ACK nhanh còn worker xử lý riêng.

Chạy local với Python 3.12, Redis tại `redis://127.0.0.1:16379/0`, sau đó:

```text
python -m uvicorn app.main:app --host 127.0.0.1 --port 18005
python -m app.worker
```

`SLACK_SIGNING_SECRET` không có giá trị mặc định; thiếu secret thì endpoint event fail
closed. `CHATOPS_TRANSPORT=local` ghi kết quả đã rút gọn vào Redis capture list và không
gửi Slack message.

Phase 5B thêm official Python MCP SDK qua stdio cho ba intent read-only:

- health: Prometheus `query` và Kubernetes `pods_list_in_namespace`;
- ingest today: `insighthub_documents_created_today` từ PostgreSQL, tính từ 00:00
  `Asia/Ho_Chi_Minh`, được đọc qua Prometheus MCP;
- failing pods: trạng thái hiện tại từ Kubernetes MCP, không kết luận lỗi chỉ vì restart
  count lịch sử.

Các biến `PROMETHEUS_MCP_COMMAND`, `PROMETHEUS_MCP_ARGS`,
`KUBERNETES_MCP_COMMAND`, `KUBERNETES_MCP_ARGS` và `MCP_TIMEOUT_SECONDS` cấu hình
runtime. Hai biến `*_ARGS` là JSON string array; repository không đặt default đường dẫn
phụ thuộc máy.

Phase 5C áp dụng ba quyết định cố định: read `allowed`, scale API
`approval_required`, destructive/unknown `denied`. Approval nằm trong Redis 60 giây,
gắn với user + action + normalized arguments và được consume nguyên tử một lần. Executor
chỉ patch scale subresource của `insighthub-api` trong `insighthub-dev`, dùng kubeconfig
mutator riêng từ `CHATOPS_MUTATOR_KUBECONFIG`; không dựng shell command từ message.
Live Slack vẫn thuộc phase sau.

Transport double chỉ phục vụ test; không thay Slack App kết nối thật. Xem thêm
[Spec mục 9](../Running-Project-Specification-Student.md).
