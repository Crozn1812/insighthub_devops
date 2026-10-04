# Demo / operation runbook

Demo chuẩn bị cho human review; không chạy lại Day6 security cases, reset budget,
scale cluster, redeploy hoặc delete data. Các bước upload dưới đây dành cho demo
future do người học thực hiện, **không được chạy trong Day7 verification**.
Không hiển thị env/Secret/kubeconfig, bearer key hoặc protected prompt.

PowerShell, root repo; kubeconfig đã có ngoài repo:

```powershell
$demoKube = Join-Path $env:USERPROFILE '.codex/day6-runtime/kubeconfig-recovery-20261003.yaml'
kubectl --kubeconfig $demoKube get nodes
kubectl --kubeconfig $demoKube -n insighthub-dev get pods,services
kubectl --kubeconfig $demoKube -n monitoring get pods
```

| Bước / command hoặc UI | Mục đích / expected | Evidence / fallback |
|---|---|---|
| 1. Lệnh inventory trên | Node Ready, pods Running/ready | day7-inventory.json nếu API transport unavailable; không reset |
| 2. `Invoke-RestMethod http://127.0.0.1:18000/readyz` | API ready, db=true, mode=real | day7-runtime.json; không đổi mode sang fixture |
| 2a. `kubectl --kubeconfig $demoKube -n insighthub-dev exec insighthub-postgres-0 -- pg_isready` | PostgreSQL accepting connections | Final runtime smoke; không in DB credentials |
| 2b. `kubectl --kubeconfig $demoKube -n insighthub-dev exec deployment/insighthub-redis -- redis-cli ping` | Redis PONG | Final runtime smoke |
| 2c. `Invoke-RestMethod http://127.0.0.1:11434/api/tags`; `Invoke-RestMethod http://127.0.0.1:14001/healthz` | Ollama local models; gateway ready/LiteLLM200 | Model generation đã ghi trong final-smoke.json; không replay security scan |
| 3. Nếu chưa có web forward: `kubectl --kubeconfig $demoKube -n insighthub-dev port-forward service/insighthub-web 13000:3000`; mở localhost13000 | UI upload/chat visible | Nếu không mở browser được, show source/HTTP200 inventory; ghi UI chưa xác minh |
| 4. Upload file `.txt` mới, nội dung benign duy nhất, <10MB qua UI | 202 + ID; poll GET /documents đúng ID đến ready | day1 runtime/replay historical nếu demo unavailable; không nhận document cũ làm fresh proof |
| 5. Hỏi câu chỉ nằm trong tài liệu mới | Answer có sources/citation đúng file | D7 benign recorded check; model error không fallback âm thầm |
| 6. Mở citation/source trong response | Citation normalization, provenance | day7-runtime.json có citation=true; citation không chứng minh answer correctness |
| 7. `kubectl --kubeconfig $demoKube -n monitoring port-forward service/kube-prometheus-stack-prometheus 19090:9090`; mở /targets, query up | Active scrape targets up | day4-targets.md/day6-monitoring-runtime.json; không sửa scrape để tạo PASS |
| 8. Forward Grafana Service 13001:80; mở localhost13001, dùng credentials local trong UI | Dashboard app/FinOps, UID insighthub-day6-finops | Monitoring evidence; không in password; screenshot do human |
| 9. Show saved refusal/sanity evidence | Explain request/output security controls | day6-final-sanity.json; không rerun attack002/004/009/016 |
| 10. Show RAG mixed-content saved result | Safe facts/citation retained, malicious instruction removed | day6-final-rag-poisoning.json; không tái poisoning corpus |
| 11. `docker ps --filter name=insighthub-day6 --format '{{.Names}} {{.Status}}'`; show safe traffic/token evidence | LiteLLM running, 3 attributed workloads | day6 ledger + day7 runtime; không expose keys |
| 12. Show historical Bot200/200/429 and Coding concurrent200/429 | Persistent budget denial, no overshoot | day6-finops-workloads.json; consumed demo budget không reset |
| 13. Show raw status/counts và official verifier failure | Honest66/2/2; HIGH009/016; ERROR002/004 | final-security-status.md + reconciliation; không sửa findings |
| 14. Review matrix/risk/evidence index | Distinguish runtime/static/manual | Final docs; acceptance trainer pending |

Existing API forward localhost18000 cần được kiểm tra trước, không spawn trùng.
Nếu port-forward chết, mở một session forward mới đến Service hiện có (không
redeploy) và ghi rõ thời điểm. Nếu relay không dùng được, dừng live demo và dùng
historical evidence với nhãn rõ; không tự reset Kubernetes. Đóng riêng session
port-forward mình mở sau demo, không dừng unrelated processes.

Live ChatOps mutation và Slack messaging không nằm trong demo closeout này.
Show signed-event/approval/audit historical thay cho thực thi action mới.
Human review: screenshot, quiz/screencast, trainer acceptance, evidence packaging,
review diff trước bất kỳ staging/commit/push nào.
