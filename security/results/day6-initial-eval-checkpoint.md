# Day 6 Phase 6B initial-evaluation checkpoint

- Baseline commit: `029c28f9e6a471dc5da3323150a5506ad75e61ac`
- Dataset SHA-256: `0CF82B16EA19B678E0CB9D73C2BB79215F30664505B156573A008F0C9F0BF05E`
- Promptfoo: `0.123.1`
- Eval ID: `eval-dBv-2026-10-01T01:42:36`
- Requested corpus: 262 attack cases, concurrency 1, no cache, no sharing
- Local target/judge: InsightHub/Ollama `qwen3:4b`
- Controlled stop: 2026-10-01 after approximately four minutes
- Persisted results visible through `promptfoo show eval`: 2/262
- Persisted outcome at checkpoint: 0 PASS, 2 FAIL
- Promptfoo progress estimate before stop: 1,044 minutes
- JSON/HTML output: not emitted because the evaluation did not complete

The command was interrupted with Ctrl+C after Promptfoo persisted the partial eval in
its external local database. No remediation was started because the initial baseline is
incomplete. Resume from the external Promptfoo runtime with:

```powershell
$env:PROMPTFOO_CONFIG_DIR = "C:\Users\ASUS\.codex\day6-runtime\promptfoo"
$env:PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION = "true"
$env:PROMPTFOO_DISABLE_REMOTE_GENERATION = "true"
$env:PROMPTFOO_DISABLE_TELEMETRY = "1"
$env:CI = "true"
npx --no-install promptfoo redteam eval `
  --config results/redteam-generated.yaml `
  --resume eval-dBv-2026-10-01T01:42:36 `
  --max-concurrency 1 `
  --no-cache `
  --no-share `
  --no-table `
  --no-progress-bar `
  --output results/day6-initial-promptfoo.json red-team-report-initial.html
```

Do not start guardrail remediation until all initial attack and benign evaluation
results have been preserved.
