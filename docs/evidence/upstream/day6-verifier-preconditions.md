# Pristine Day 6 verifier preconditions

Authority: upstream 4923fed6ef650aeea69eb179ff2a12415cf0fc90, scripts/verify.py SHA256 e94c2184eb1eb2eeb23e7c61deba934e4c0eea204aad83d2f90d1a6bb175c23b. This executable was not edited.

| Question | Exact contract and result |
|---|---|
| A: only no HIGH/CRITICAL? | No. MH5 uses this wording; eval_report additionally requires every final verdict true (line 718). |
| B: all final passed=true? | Yes. Current benign-001 FAIL is rejected even with no HIGH. |
| C: fresh initial/current source? | Yes. Lines 698-699 apply freshness (default 24h) and exact current source/dataset digests to initial and final. |
| D: itself invokes 70 live cases? | It invokes student milestone tests through run_tests, not a built-in Promptfoo CLI. Lines 774-780 demand their new evaluation/cost observations, run_id binding, full dataset coverage, current source and timestamps at least invocation start minus one second. Replaying the existing scan cannot satisfy that live-observation contract. |
| E: identical initial/final coverage? | Yes. Each report must cover the exact unchanged dataset (line 720); unknown/duplicate cases fail. |
| F: rejects 69/1 despite HIGH=0? | Yes, line 718. |
| G: stale fields? | Historical initial observed_at exceeds freshness; historical initial/final source_sha256 do not attest current source. The 69/1 scan predates later UUID/config fixes. Cost source/time and live run_id/observed_at must bind their actual execution. 24 scan rows have unavailable token usage; integer token fields may not be fabricated as zero. |

Current actual invocation: 2026-10-05T04:08:56.400798Z, source 7b83c9ce2c0d931771de2ce90f3dd8412b369b81082d3ecde949b9eb7ad7cb47, exit 2, INCOMPLETE, runtime_verified=false, "Evidence is stale or future-dated". See official-verifiers.json.

No additional full scan was run. Execution stops at initial prevalidation before milestone tests. One extra final scan alone cannot repair both the missing fresh current-source initial and all-pass final preconditions, nor certify the later invocation-bound live observation. Preserve both 66/2/2 and 69/1/0 runs. No timestamps, hashes, token values or verdicts are rewritten. Day 6 remains unaccepted.
