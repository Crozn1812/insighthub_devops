# Day 6 bounded local evaluation profile

This pre-remediation profile keeps the complete 262-attack generated corpus while
executing a deterministic 60-attack core plus all 10 benign cases. Both initial and
final evaluations use the same real InsightHub target: `qwen3:4b`, real retrieval,
`OLLAMA_THINK=false`, and a 128-token target answer budget. The evaluator uses a
separate calibrated grading budget so Promptfoo's structured rubric response is not
truncated.

## Performance evidence

- The initial 256-token target benchmark measured 85.378, 47.144, and 35.816
  seconds (median 47.144), and every response reached 256 output tokens.
- The bounded 128-token benchmark measured 26.065, 16.577, and 17.582 seconds
  (median 17.582). All responses were real Ollama responses with three retrieved
  sources and provider-reported input/output usage.
- The `qwen3:4b`, `think=false` judge agreed with four clear expected decisions
  (direct injection, PII, excessive agency, and benign) in 5.046–7.946 seconds.
  It was acceptable, so no additional smaller model was downloaded.
- The actual Promptfoo five-case path completed in 269.684 seconds at concurrency
  one: 53.937 seconds/case and a linear 70-case projection of 62.93 minutes.
  That first benchmark exposed truncated judge JSON at a 128-token judge budget; its
  security outcomes are invalid and retained only as performance evidence. A corrected
  non-truncating judge benchmark is required before the official baseline.
- The judge-only `qwen3:1.7b` candidate produced 10/10 valid JSON, 9/10 exact
  pass/fail agreement, and 9/10 severity agreement against `qwen3:4b` on the
  deterministic clear-case set. Its one disagreement was a reviewed false negative
  on `direct-1`; the reference and expected label were unsafe/high. This meets the
  stated 9/10 preferred agreement gate without changing the application target.
- Promptfoo 0.123.1's Ollama provider passes `format: json` to `/api/chat`; the
  judge-only profile uses that structured-output mode with `think=false` and a
  128-token JSON budget to avoid both malformed truncation and verbose grading.
- The healthy-target structured Promptfoo benchmark completed 5/5 in 172.732
  seconds (34.546 seconds/case), with zero execution or grading-parse errors. The
  linear 70-case projection is 40.30 minutes at concurrency one.

The target and embedding models were resident during measurement. Concurrency remains
one because the measured projection is below 90 minutes and avoids local RAM pressure.
