# Day 3 Infrastructure Specification

## 1. Purpose

Define a reviewable Infrastructure as Code foundation and policy contract for InsightHub.

## 2. Local-only decision

This project uses the local-only/no-cost track. AWS account access and cloud mutations are disabled.

## 3. Original cloud architecture intent

The source models EKS with KMS encryption, PostgreSQL 16, Redis 7, IAM/OIDC with narrowly bound IRSA, and a Secrets Manager container for learning and static analysis. Its status is `STATIC_VALIDATION_ONLY`: no AWS account was accessed and no cloud resource is claimed to exist.

## 4. Local runtime equivalent

Docker Desktop Kubernetes will run web, API, ingestion worker, PostgreSQL with pgvector, and Redis through a future Helm chart.

## 5. Security requirements

- No credentials, tokens, account IDs, or generated passwords are committed.
- Databases must be encrypted and non-public.
- Cache networking must be private and encryption enabled.
- Cloud execution remains disabled by default.

## 6. Required tags

Every managed AWS resource must carry `project`, `environment`, `owner`, `cost_center`, and `managed_by`.

## 7. Terraform validation gates

Run formatting, backend-disabled initialization, validation, TFLint, and Checkov locally. Terraform must remain compatible with native S3 lockfiles.

## 8. Policy gates

Conftest evaluates Terraform plan JSON for required tags, database security, and cache security. Both an accepted fixture and a deliberately rejected fixture are tested.

## 9. Acceptance criteria

- `terraform fmt -check -recursive infra` exits zero.
- `terraform -chdir=infra init -backend=false -input=false` and `validate -no-color` exit zero.
- TFLint and Checkov exit zero.
- Conftest accepts `valid-plan.json` and rejects `unsafe-plan.json` with meaningful denials.
- Both required Day 3 policy tests pass without network, AWS, or Kubernetes access.

## 10. Explicit non-goals

The local-only track does not initialize the live S3 backend, plan/apply infrastructure, create Helm charts in this phase, edit CI workflows, or deploy Kubernetes resources. Docker Desktop Kubernetes remains the runtime target.
