# Three-minute screencast script

This is a recording plan, not a recording or a Loom URL. Use actual final results
from [the compliance matrix](../upstream-compliance-matrix.md). Record only after
runtime recovery and final checks; do not narrate historical health as current.
Hide terminals containing credentials, private kubeconfig, tokens or policy text.

| Time | On screen | Narration/action |
|---|---|---|
| 0:00–0:20 | README and architecture diagram | InsightHub uploads documents and answers with cited retrieved facts. API admits jobs; Redis/ARQ dispatches a separate ingestion worker. |
| 0:20–0:40 | AGENTS.md headings, real prompt log and Day 1 PR | Show six context sections and explain one accepted/rejected engineering decision. |
| 0:40–1:15 | Web upload and document state, then chat | Upload the prepared sample, observe the same ID pending→ready, ask a factual question, open the cited source. Show measured upload/ready timings only if captured. |
| 1:15–1:35 | GitHub Actions and IaC files | Show latest actual workflow run. Explain static checks versus AWS plan/apply; AWS remains not executed unless real evidence changes. |
| 1:35–1:55 | Grafana and one RCA report | Show RED/queue/resource panels and a cited incident metric/timestamp. Do not fabricate a currently firing alert. |
| 1:55–2:20 | Slack workspace if authorized | Ask health, ingest count, failing pods. If Slack LIVE is blocked, state that explicitly and show technical tests as a separate result. |
| 2:20–2:45 | Final security report, native guard/key metadata and cost dashboard | State exact PASS/FAIL/ERROR and HIGH/CRITICAL totals. Demonstrate safe metadata only, never virtual-key values. Explain provider USD 0 versus resource/planning costs. |
| 2:45–3:00 | Compliance matrix and remaining actions | State unresolved requirements, chosen roadmap only if learner has chosen, and show real submission links. |

Before recording: keep prepared browser tabs open, rehearse to 180 seconds,
verify health, avoid long model loading during capture, disable notifications
that could reveal private messages. After recording: inspect video for secrets,
upload through the learner's Loom account, verify reviewer access, and place the
real URL in the checklist. A local demo cannot replace a live Slack requirement.
