# Submission convention audit

Authority: upstream specification v3.3, section 4, at
`4923fed6ef650aeea69eb179ff2a12415cf0fc90`.
Audit checkpoint: fork `daf3f8bd67594f3bc5f287a00f03ef91324be9bc`.
This review does not establish classroom submission or trainer approval.

| Day | Actual branch | PR evidence | Convention gap |
|---|---|---|---|
| 1 | day1-refactor | [PR 1](https://github.com/Crozn1812/insighthub_devops/pull/1), exact required title | No naming gap |
| 2 | day2-mcp | No dedicated PR found in all-state GitHub listing | Required daily PR evidence missing; changes retained cumulatively |
| 3 | day3-terraform | [PR 2](https://github.com/Crozn1812/insighthub_devops/pull/2) | Local CI does not establish full AWS pipeline acceptance |
| 4 | day4-aiops | [PR 3](https://github.com/Crozn1812/insighthub_devops/pull/3) | Topic differs from recommended day4-observability example |
| 5 | day5-chatops | [PR 4](https://github.com/Crozn1812/insighthub_devops/pull/4) | Topic differs from recommended day5-chatops-bot example |
| 6 | day6-security-finops | [PR 5](https://github.com/Crozn1812/insighthub_devops/pull/5) | Current final-submission title lacks `[Day 6]` prefix; do not imply acceptance |
| 7 | Included in day6-security-finops | PR 5 cumulative closeout | No separate day7-showcase branch/PR |

Section 4 requires `day{N}-<topic>`; the alternate Day 4/5 topics still fit
that syntax. Preserve published history rather than rename branches or fabricate
historical per-day submissions. A new present-day Day 2 PR may establish review,
but cannot retroactively demonstrate the classroom deadline.

Recent commits use Conventional Commit prefixes (`feat`, `fix`, `test`, `docs`,
`chore`). Prompt logs exist at `ai-prompts/day1.md` through `day7.md`.
Days 1–5 contain at least three actual prompt summaries with decisions and
recorded evidence; Day 6 contains multiple dated real milestones. These logs
remain historical records, not fresh verifier evidence. Day 7's two prior user
requests plus the current master audit are distinct actual requests; adding this
milestone must not invent model/version metadata unavailable in the session.

Manual requirements still need real URLs: daily Slack submissions/deadlines,
official quiz forms, Day 7 self-evaluation form, Loom URL, trainer rubric/feedback.
Repository URLs and local HTTP URLs cannot replace those external records.

GitHub CI observed at the audit checkpoint: Starter baseline and Day 3 IaC
validation both completed successfully for `daf3f8b`. This predates new audit
edits and proves only the jobs actually executed. AWS plan/cost/apply were absent
from that run and therefore cannot be described as green cloud execution.
