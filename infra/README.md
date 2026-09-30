# Day 3 IaC — local-only track

The Terraform source includes an optional EKS control plane and node group, KMS encryption, private RDS PostgreSQL 16, private ElastiCache Redis 7, OIDC/IRSA, and Secrets Manager metadata. Every AWS resource is disabled by default with `enable_aws = false`. Its status is **STATIC_VALIDATION_ONLY**: no AWS account was accessed and none of these resources is deployed. Docker Desktop Kubernetes remains the runtime target.

Run the positive validation gates from the repository root:

```powershell
terraform fmt -check -recursive infra
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra validate -no-color
tflint --chdir=infra --recursive
checkov -d infra --quiet
conftest test infra/policies/fixtures/valid-plan.json --policy infra/policies/terraform
```

Confirm the negative policy fixture is rejected:

```powershell
conftest test infra/policies/fixtures/unsafe-plan.json --policy infra/policies/terraform
```

The S3 backend declaration is a disabled source contract. Always use `-backend=false` on this local-only track and never run a live AWS plan/apply. PostgreSQL initialization, including pgvector, remains in `db/init.sql` for an authorized migration/bootstrap mechanism. See [SPEC.md](SPEC.md) and the course [Day 3 specification](../Running-Project-Specification-Student.md#7-day-3--ai-powered-iac--pipeline).
