resource "aws_secretsmanager_secret" "insighthub" {
  #checkov:skip=CKV2_AWS_57:Metadata only; no secret value is committed, live rotation requires a real rotation Lambda, and AWS runtime is intentionally not executed.
  count                   = var.enable_aws ? 1 : 0
  name_prefix             = "${var.eks_cluster_name}/runtime-"
  description             = "InsightHub runtime secret container; values are populated outside Terraform source"
  recovery_window_in_days = 7
  tags                    = local.common_tags
}

# No aws_secretsmanager_secret_version is committed. Secret values must be
# populated through an authorized runtime process when a real deployment exists.
