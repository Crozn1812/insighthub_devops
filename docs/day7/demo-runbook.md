# Day 7 reviewer demo

This is the canonical executable demo sequence, linked by the
[project demo overview](../demo-runbook.md). It targets Docker Desktop Kubernetes and local
Ollama; it does not require or prove AWS execution.

Run from repository root after Docker/Kubernetes recovery. Use an authorized
private kubeconfig selected in the local environment; never display its content.

```powershell
kubectl --context docker-desktop get nodes
kubectl --context docker-desktop -n insighthub-dev get pods
kubectl --context docker-desktop -n monitoring get pods
kubectl --context docker-desktop -n insighthub-dev port-forward service/insighthub-api 18000:8000
```

Keep port-forward in its own terminal. In a second terminal:

```powershell
curl.exe -fsS http://127.0.0.1:18000/healthz
curl.exe -fsS http://127.0.0.1:18000/readyz
kubectl --context docker-desktop -n insighthub-dev exec statefulset/insighthub-postgres -- pg_isready -U insighthub -d insighthub
kubectl --context docker-desktop -n insighthub-dev exec deployment/insighthub-redis -- redis-cli PING
curl.exe -fsS http://127.0.0.1:11434/api/tags
curl.exe -fsS http://127.0.0.1:14002/health/liveliness
curl.exe -fsS -X POST http://127.0.0.1:18000/documents -F file=@sample-docs/so-tay-van-hanh.md
curl.exe -fsS http://127.0.0.1:18000/documents
```

Record the upload's actual document ID and wait for that ID to become ready.
Use the web UI for the factual chat and citation. The native gateway health URL
applies only after its startup is verified; the historical adapter uses 14001.
Neither health endpoint proves authenticated model calls or budget enforcement.

In separate terminals, forward Prometheus and Grafana:

```powershell
kubectl --context docker-desktop -n monitoring port-forward service/kube-prometheus-stack-prometheus 19090:9090
kubectl --context docker-desktop -n monitoring port-forward service/kube-prometheus-stack-grafana 13001:80
```

Open Grafana at localhost:13001. Show nine-plus observability panels, the cost
dashboard and three [RCA evidence](../evidence/upstream/README.md). Authenticate using
the local secret workflow, without exposing passwords in screenshots/video.
Show runtime allowed/blocked guard proof and native budget proof only after their
fresh evidence exists. Show final security totals honestly; the new compliance
run is 69 PASS, 1 benign FAIL, 0 ERROR, HIGH 0, CRITICAL 0. Historical 66/2/2
evidence remains preserved, and formal Day 6 acceptance is still unmet.

Slack LIVE requires the real workspace setup described in
[remaining actions](remaining-manual-actions.md). A local HTTP capture is useful
technical proof but does not satisfy Slack LIVE. Stop only demo port-forwards
afterward; preserve database volumes and evidence.

Native keys stay private: demonstrate allowed/denied requests using the saved
sanitized native proof, not key values or full HTTP Authorization headers.
Use the actual private kubeconfig locally if the default context needs recovery.
No AWS account is needed for this local demo; it does not satisfy AWS LIVE.
