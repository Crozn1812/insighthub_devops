# Day 4 live baseline

- Complete-signal start: `2026-09-30T14:04:42+07:00`
- End: `2026-09-30T15:05:56+07:00`
- Duration: `3674` seconds (`61m14s`)
- Requirement `>= 1h`: PASS
- Prometheus scrape interval: `15s`

Live `query_range` checks over that exact interval returned:

| Signal | Series | Samples |
| --- | ---: | ---: |
| `insighthub:llm_latency_p95_seconds` | 1 | 245 |
| `insighthub:ingestion_queue_depth` | 1 | 245 |
| `insighthub:api_error_ratio5m` | 1 | 245 |
| InsightHub pod memory | 13 | 1720 |
| `pg_up` | 1 | 245 |
| `redis_up` | 1 | 245 |

The workload used the fixture LLM through the real local API. Deployment
rollouts during initial setup caused a small number of honestly logged request
failures before the complete-signal window; they are not hidden or counted as
incident evidence. The interval above begins at the latest required signal's
first continuous sample and therefore contains more than one real hour for
every listed signal.
