output "environment" {
  description = "Validated environment name."
  value       = var.environment
}

output "region" {
  description = "Region represented by the static architecture."
  value       = var.aws_region
}

output "required_tag_keys" {
  description = "Tag keys required by the policy contract."
  value       = sort(keys(local.common_tags))
}

output "aws_enabled" {
  description = "Whether optional AWS resources are enabled."
  value       = var.enable_aws
}

output "eks_cluster_name" {
  description = "Optional EKS cluster name."
  value       = try(aws_eks_cluster.insighthub[0].name, null)
}

output "rds_endpoint" {
  description = "Optional private RDS endpoint."
  value       = try(aws_db_instance.insighthub[0].address, null)
}

output "redis_primary_endpoint" {
  description = "Optional private Redis primary endpoint."
  value       = try(aws_elasticache_replication_group.insighthub[0].primary_endpoint_address, null)
}

output "irsa_role_arn" {
  description = "Optional InsightHub workload role ARN."
  value       = try(aws_iam_role.insighthub_irsa[0].arn, null)
}

output "secret_arn" {
  description = "Optional runtime secret container ARN; no secret value is exposed."
  value       = try(aws_secretsmanager_secret.insighthub[0].arn, null)
}
