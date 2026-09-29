# Day 2 AI Prompt Log

## Prompt 1 - Four-backend MCP integration and security validation

**Host**: ChatGPT-Codex

**Host / model details**: Codex agent based on GPT-5 on Windows native; no account or subscription identifiers recorded.

**Time**: 2026-09-29. Exact per-call timestamps remain in phase evidence where available.

**Context / Evidence**:

- Servers: `filesystem-day2`, `docker-day2`, `kubernetes-day2`, and `prometheus-day2`.
- Results: `evidence/day2-mcp-host-validation.md`.
- Sanitized configuration: `evidence/day2-mcp-config-sanitized.toml`.

**Prompt summary (condensed from the actual prompt used)**:

Validate four pinned MCP backends through Codex Host with real read-only calls. Confirm filesystem containment, Docker's non-mutating surface, Kubernetes read-only identity and negative permissions, and Prometheus query health with destructive tools absent. Do not alter runtime configuration or expose credentials.

**Why it worked**:

- Per-backend expected results were explicit.
- Positive calls and negative security checks were both required.
- Tool catalogs were checked before invocation.

**What I reviewed / changed**:

- Reviewed tool surfaces and pinned versions.
- Verified real backend responses without mutation.
- Kept credentials outside repository evidence.

## Prompt 2 - Independent MCP Inspector CLI validation

**Host**: ChatGPT-Codex

**Host / model details**: Codex agent based on GPT-5 on Windows native; no account or subscription identifiers recorded.

**Time**: 2026-09-29 during the Day 2 Inspector validation session.

**Context / Evidence**:

- Inspector: `@modelcontextprotocol/inspector@2.8.0`.
- Node.js: `v24.19.0`.
- Results: `evidence/day2-inspector-cli.md`.

**Prompt summary (condensed from the actual prompt used)**:

Use pinned Inspector CLI with an external read-only session config. Initialize every server, list tools, and invoke one real read-only tool. Treat the upstream filesystem catalog and Codex Host filtering as separate security layers.

**Why it worked**:

- Inspector validated servers independently of Codex Host.
- Exact upstream tool names were used instead of aliases.
- Filesystem containment had positive and negative tests.

**What I reviewed / changed**:

- Confirmed Inspector CLI 4/4 PASS.
- Corrected interpretation of upstream filesystem write-capable tools.
- Kept screenshot evidence explicitly pending after invalid captures.

## Prompt 3 - Docker MCP controlled crash RCA

**Host**: ChatGPT-Codex

**Host / model details**: Codex agent based on GPT-5 on Windows native; no account or subscription identifiers recorded.

**Time**: 2026-09-29T13:30:41.989Z to 2026-09-29T13:31:35.357Z.

**Context / Evidence**:

- Controlled fixture `day2-crash-fixture` was created separately before investigation.
- `docker-day2` was read-only.
- RCA artifact: `debug-session-day2.md`.

**Prompt summary (condensed from the actual prompt used)**:

In a fresh conversation, investigate the preserved failed container using only Docker MCP evidence. Follow `container_list` → `container_inspect` → bounded `container_logs`, separate facts from interpretation, avoid Docker CLI as an RCA source, and document the root cause without applying remediation.

**Why it worked**:

- The fixture was reproducible and isolated.
- A fresh conversation prevented reliance on its creation explanation.
- Inspect data and logs supplied complementary evidence.
- The conclusion followed evidence rather than assumption.

**What I reviewed / changed**:

- Confirmed state and exit code through Docker MCP.
- Correlated the startup argument with the bounded application error.
- Created `debug-session-day2.md`; no remediation or mutation was performed.
