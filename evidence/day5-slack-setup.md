# Day 5 live Slack setup

Status: `PENDING_USER_SLACK_APP`

The local ChatOps technical contract is complete. Live Slack validation remains a
manual course-rubric item because this environment does not currently provide a Slack
bot token, Slack signing secret, Slack bot user ID, or an authenticated HTTPS tunnel.

## Minimal Slack app configuration

1. Create or select a user-controlled Slack app and install it in the intended test
   workspace.
2. Grant only these bot token scopes:
   - `app_mentions:read`
   - `chat:write`
3. Enable **Event Subscriptions** and set the Request URL to:
   `https://<temporary-ngrok-host>/slack/events`.
4. Subscribe to the bot event `app_mention`. No broad channel-history scope is needed
   for the implemented mention-driven flow.
5. Supply `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and `SLACK_BOT_USER_ID` to the
   local process environment. Do not write them to repository files, evidence, logs,
   screenshots, or shell history.
6. Expose only `http://127.0.0.1:18005` through an authenticated temporary HTTPS
   tunnel. Do not expose Redis, Prometheus, PostgreSQL, Grafana, or Kubernetes.
7. Use Slack's Event Subscriptions UI to perform the signed Request URL challenge and
   record `Verified` only after Slack confirms it.

## Manual live checks

- `@bot InsightHub có healthy không?`
- `@bot Hôm nay ingest bao nhiêu doc?`
- `@bot Pod nào đang lỗi?`
- Request `scale api to 2`, complete the implementation's exact approval syntax,
  verify replicas become two, then restore to one.
- Request `delete namespace` and verify it is denied without mutation.
- Confirm server-side ACK timing remains below three seconds.

No credential or tunnel URL is recorded in this document.
