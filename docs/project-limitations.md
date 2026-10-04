# Limitations / risk register

Mọi future action dưới đây là đề xuất cho review sau, chưa được thực thi Day 7.

| Risk / gap | Trạng thái, ảnh hưởng | Future action / owner |
|---|---|---|
| attack-009 / attack-016 | Unresolved automated HIGH; Day 6 acceptance FAIL | Human security review, remediation riêng nếu được phép |
| attack-002 / attack-004 | Evaluator ERROR; không có verdict; missing target bodies | Cải thiện telemetry và judge reliability trong task riêng |
| Semantic judge | Calibration 11/12, unsafe invalid judgment | Benchmark independent/human review; không tuyên bố reliable tuyệt đối |
| Injection heuristics | Có false positive/negative, obfuscation bypass | Mở rộng adversarial regression có scope |
| RAG sanitizer | Mixed-content preservation không chứng minh mọi bypass được chặn | Review retrieval trust boundary / adversarial corpus |
| Local model | qwen3:4b nondeterminism, latency, utility limits | Ghi seed/config/latency; đánh giá chất lượng độc lập |
| Async enqueue gap | Crash sau DB commit trước enqueue chưa có outbox/reconciler | Thiết kế recovery riêng; không pending vô hạn trong production |
| Docker Desktop K8s | Single node, không HA, host/storage dependent | Production design/backup/restore validation riêng |
| Recovery relay | Temporary localhost16443; Docker health unhealthy dù kubectl hoạt động | Điều tra native API transport, không reset trong closeout |
| Container endpoint | FinOps Service trỏ Docker network IP local | Discovery/recovery tự động nếu chuyển production |
| Restart history | Worker 40, web 22 tại inventory; hiện ready | Review nguyên nhân historical restarts và stability window |
| AWS runtime | NOT_EXECUTED_NO_AWS | Chỉ triển khai cloud với authorization/budget riêng |
| Terraform | STATIC_VALIDATION_ONLY; không cloud plan/apply | Không coi static PASS là deployed cloud |
| FinOps pricing | Provider USD0 local; planning allocations không billing | Pricing model riêng nếu provider thay đổi |
| Resource measurement | RSS sampled/shared; không GPU/electricity | Đo energy/GPU/cost khi có phương pháp và scope |
| LiteLLM identity | Adapter equivalent, không native virtual-key admin | Đánh giá native administration sau |
| Demo budgets | Bot/Coding consumed; không reset | Show existing denial evidence, không replenish để tạo PASS |
| Current quality tools | ruff/mypy unavailable; không install | Human chạy trong environment đã chuẩn bị; historical targeted checks không toàn repo |
| WSL dependencies | Day 7 pytest collection thiếu prometheus_client/httpx | Existing Linux image used offline; không cài package |
| Screenshots / quiz | Day 2 inspector/quiz, Day 4 dashboard/quiz, Day 5 screencast, Day 6 FinOps screenshot pending | Learner thu manual evidence |
| Slack integration | Day 4 delivery / Day 5 live Slack chưa xác nhận | User-controlled app/secret setup; không ghi secret |
| Trainer acceptance | Pending; verifier partial contract không thay rubric | Trainer + learner review |
| Evidence shipping | evidence/* phần lớn gitignored, local links không đủ cho reviewer remote | Human quyết định packaging/sanitized export; không đổi .gitignore ở đây |
| Historical source binding | Day wrappers bind historical source; current docs không tái attestation | Không sửa timestamp/hash để giả fresh PASS |

Final local runtime usable không đồng nghĩa production-ready/security accepted.
Day 7 technical finalization không thay đổi Day 6 verdict.
