# Native local Day 6 FinOps

Current runtime uses native LiteLLM 1.98.0, dedicated PostgreSQL and three
DB-backed virtual keys with `max_budget`. See [current status](../docs/final-finops-status.md)
and [native proof](../docs/evidence/upstream/native-budget-runtime.json).
The adapter instructions below describe the historical implementation.

Current implementation: `native-compose.yaml`, `native-litellm.yaml`,
`native_keys.py`, `native_verify.py`, `native_exporter.py`, `deploy_native_local.py`
and `verify_workloads.py`; pinned NeMo lives in `security/guardrails/`.
Use private env/key/rollback files outside Git. The provisioning tool refuses
key destinations inside this repository and overwriting existing key files.
After reviewing private credentials and selecting the existing Python runtime:

```powershell
$env:NATIVE_ENV_FILE = $privateEnv
docker compose --env-file $privateEnv -p insighthub-native-finops -f finops/native-compose.yaml up -d --wait
python finops/native_keys.py --env-file $privateEnv --private-keys $privateKeys
python finops/deploy_native_local.py --kubeconfig $privateKubeconfig --private-keys $privateKeys --env-file $privateEnv --rollback-file $privateRollback
python finops/native_verify.py --env-file $privateEnv --private-keys $privateKeys --output $newEvidencePath
```

Do not provision again on a completed runtime or reuse application DB storage.
Deployment `--resume` preserves rollback; `--telemetry-only` repairs genuine
endpoint/scrape wiring without changing keys/restarting workloads. Verification
restores caps in `finally`. Concurrent zero-cap denial is verified; positive-cap
atomic exhaustion is not. Planning token rates are distinct from provider USD 0.
The exporter exposes aliases/usage/spend/caps, never keys/hashes/DSNs/prompts.

## Historical scoped-adapter workflow

Final submission: [evidence index](../docs/evidence/README.md),
[cost/status](../docs/final-finops-status.md). Artifact tests use retained local
originals when available, or the tracked compact package in a clean clone.
Historical snapshots are not live ledger totals; never reset the consumed
demonstration budgets or overwrite historical exports to manufacture results.

Workloads authenticate to a scoped admission adapter on localhost 14001. The
adapter reserves planning credits atomically in SQLite, then calls the pinned
LiteLLM 1.98.0 proxy on the private Docker network. LiteLLM routes only to local
Ollama qwen3:4b with thinking disabled. Provider cost is zero.

Three random bearer keys live only in the existing user-local runtime directory
and the InsightHub Kubernetes Secret. Evidence contains display identities,
never key values. This implementation provides equivalent scoped identities
around LiteLLM; it does not claim native DB-backed LiteLLM virtual-key management.

Budgets are explicit local admission allocations: one admitted model request
reserves 10,000 micro-USD planning credits. They are not provider billing,
electricity cost or measured resource prices. Actual provider tokens and gateway
response/correlation IDs are recorded separately. Failures keep their allocation
to avoid retry bypass. BEGIN IMMEDIATE ensures that concurrent admission cannot
overshoot the configured integer threshold. Persistent state is in the scoped
Docker volume; no reset/delete is performed after tests.

Only non-streaming qwen3:4b requests up to 64 KiB and 1,024 output tokens are
accepted. Public local health and metrics contain no secrets or prompt text.
The dashboard separates allocation credits from the zero provider-cost metric.

## Current runtime / deployment notes

This documents the existing deployment; no rebuild/redeploy was done for
submission. Docker container `insighthub-day6-litellm` runs `--config
/app/config.yaml --port 4000 --num_workers 1` with this `litellm.yaml` mounted
read-only. Gateway container runs `python -m uvicorn finops.gateway:app --host
0.0.0.0 --port 4001` with `finops/` mounted at `/app/finops`, local key file at
`/run/keys.json` and persistent SQLite volume at `/state`.

Both use pinned LiteLLM1.98.0 image, share `insighthub-day6-finops` network;
gateway additionally joins existing Kubernetes `kind` network. Host bindings
are loopback14000(proxy)/14001(gateway); API reaches gateway through the
`insighthub-finops-gateway` Kubernetes Service. `kubernetes.yaml` contains the
observed Docker IP172.22.0.6; it is a local snapshot, not a portable dynamic
discovery manifest. Verify the current IP before any separately authorized apply.

Keys are created only by `create-local-keys.py` in the user runtime directory;
`route-api.py` configures Secret references and the existing API image/provider
route. Do not run these against the healthy deployment for demo/submission.
Review scripts before using them in a new authorized lab; keys never go in env
files/evidence/Git. Host-specific kubeconfig and model/storage setup are covered
by GETTING_STARTED and the demo runbook. The repository does not provide an
automated production deployment for this local bridge.

Safe status checks (no credentials/model requests):

```powershell
docker ps --filter name=insighthub-day6 --format '{{.Names}} {{.Status}}'
Invoke-RestMethod http://127.0.0.1:14001/healthz
```
