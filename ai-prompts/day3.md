# Day 3 AI Prompt Log

Host: ChatGPT-Codex
Model/version: Codex based on GPT-5; exact deployment identifier not exposed
Authentication mode: not exposed to this session

## Entry 1 — Local-only inventory and toolchain

- Time: 2026-09-30
- Prompt summary: Inventory the repository and Docker Desktop Kubernetes, create `day3-terraform`, and install a pinned user-local Terraform security toolchain without AWS access.
- Context/Evidence: Day 2 commit `4741b0f`; one Ready `docker-desktop` node; official checksums verified before extraction.
- Why it worked: The request separated local runtime capability from original cloud requirements and pinned every required tool.
- What I reviewed/changed: Created the branch and installed tools outside the repository. Corrected the Helm checksum using official release metadata; no repository source changed during installation.

## Entry 2 — Terraform foundation and policy contract

- Time: 2026-09-30
- Prompt summary: Create the Terraform backend-disabled foundation, required tags, Rego v1 policies, safe/unsafe plan fixtures, and executable Day 3 milestone tests.
- Context/Evidence: The verifier requires `test_policy_allows_valid`, `test_policy_denies_unsafe`, fmt, backend-disabled init, validate, and Checkov.
- Why it worked: Positive and negative fixtures made policy behavior observable instead of relying on static prose.
- What I reviewed/changed: Added native S3 lockfile source, typed variables, policies for tags/database/cache security, and two tests. Fixed the policy package to `main` after Conftest initially ignored the rules.

## Entry 3 — AWS static source, local Kubernetes, and CI

- Time: 2026-09-30
- Prompt summary: Harden AWS-oriented Terraform without executing AWS, build a no-secret Helm chart, deploy it to Docker Desktop Kubernetes, run smoke verification, and create no-AWS GitHub Actions validation source.
- Context/Evidence: `enable_aws=false`; Checkov initially reported five findings; local images were built and the `insighthub` Helm release was deployed in `insighthub-dev`.
- Why it worked: Security remediation was bounded by exact Checkov IDs, while runtime acceptance used the real API, worker, PostgreSQL/pgvector, Redis, and web components.
- What I reviewed/changed: Achieved Checkov 20 passed/0 failed/1 documented metadata-only suppression, five Ready workloads, pgvector/schema verification, Redis PONG, official smoke PASS, and locally reproduced all practical CI jobs. AWS and remote GitHub execution remain explicitly deferred.

## Entry 4 — GitHub CI and official verification

- Time: 2026-09-30
- Prompt summary: Finalize Git, run push and pull-request CI, verify the bound CI artifact, and execute the official Day 3 GitHub-profile verifier without AWS access.
- Context/Evidence: PR #2 targets `day2-mcp`; PR run `36657449428` completed successfully; `verification-source` matched source `763640c9887c2ce9602e392010855e059bb7d5a2a6a55075ce56d44d857be83c` and deployment `905edbf30933bc1e87b11a75568f627c4d3338f1387223e5b9375b27ab2546c6`.
- Why it worked: CI installation was made non-interactive, and the source fingerprint was canonicalized for text line endings so Windows and Linux produce the same digest without weakening any verification gate.
- What I reviewed/changed: Fixed one failed CI iteration, added a cross-platform fingerprint regression test, obtained a green push run and green PR run, and recorded official verifier PASS with `runtime_verified=true` and `milestone_complete=false`. AWS requirements remain `NOT_EXECUTED_NO_AWS`.
