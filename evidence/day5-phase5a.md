# Day 5 Phase 5A — ChatOps foundation evidence

Date: 2026-09-30 (Asia/Saigon)

## Scope and isolation

- Track: local-only / no-cost.
- Branch: `day5-chatops`, created from Day 4 SHA
  `7a6fb331cc7a7e354cba144dcad2f18b82372c53`.
- Python: 3.12.0 in `C:\Users\ASUS\.codex\day5-runtime\venv`.
- Redis port-forward: `127.0.0.1:16379` to the `insighthub-redis` Service.
- Bot: `http://127.0.0.1:18005`; worker runs as a separate process.
- E2E data used the isolated `insighthub:chatops:e2e:20260930:*` namespace.
- No AWS, paid cloud, MCP tool, live Slack API, or infrastructure mutation was used.

## Security and queue contract

- Verification order: raw body → timestamp/signature verification → JSON parsing.
- Signature: Slack v0 HMAC-SHA256 with constant-time comparison.
- Replay rule: reject requests older than 300 seconds or more than 30 seconds in the
  future.
- URL challenge is returned only after authentication.
- `bot_message`, `bot_id`, and configured bot-user events ACK without enqueue.
- Redis Lua performs `SET NX EX` and `RPUSH` atomically by `event_id`.
- Dedup TTL: 86,400 seconds; max processing attempts: 3.
- Retry metadata remains in a Redis sorted set until due; backoff is exponential.
- Queue payload contains only event ID, user, channel, text, event timestamp, and attempt.

## Verification

- Redis PING: PASS.
- Health: HTTP 200 with `ready=true`, `redis=ok`, `queue=ready`, `transport=local`.
- Tests: 19 passed, 0 failed, 0 skipped.
- Python compile check: PASS.
- Redis integration covers dedup/state across a new queue object and durable retry
  promotion using isolated test keys.
- Local E2E: 20 unique signed events accepted, 20 captured results, duplicate ACKed,
  duplicate reprocessed = false.

ACK timing for 20 real loopback HTTP requests:

- minimum: 7.492 ms
- average: 23.575 ms
- p95: 32.049 ms
- maximum: 80.345 ms
- all samples below 3 seconds: PASS

## Regression and secret handling

- InsightHub API health: HTTP 200.
- Prometheus readiness: HTTP 200.
- `insighthub-dev` and `monitoring` workloads: Ready/Running.
- Actual Slack credentials, Kubernetes tokens, database secrets, private keys, and
  tunnel credentials written by this phase: none.
- The E2E signing value was a disposable local fixture supplied only to the process
  environment and is not recorded here or in repository configuration.
