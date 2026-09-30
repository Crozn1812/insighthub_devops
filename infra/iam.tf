data "tls_certificate" "eks_oidc" {
  count = var.enable_aws ? 1 : 0
  url   = aws_eks_cluster.insighthub[0].identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  count = var.enable_aws ? 1 : 0
  url   = aws_eks_cluster.insighthub[0].identity[0].oidc[0].issuer

  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks_oidc[0].certificates[0].sha1_fingerprint]
  tags            = local.common_tags
}

data "aws_iam_policy_document" "insighthub_irsa_assume" {
  count = var.enable_aws ? 1 : 0

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks[0].arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_eks_cluster.insighthub[0].identity[0].oidc[0].issuer, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_eks_cluster.insighthub[0].identity[0].oidc[0].issuer, "https://", "")}:sub"
      values   = ["system:serviceaccount:${var.insighthub_namespace}:${var.insighthub_service_account}"]
    }
  }
}

resource "aws_iam_role" "insighthub_irsa" {
  count              = var.enable_aws ? 1 : 0
  name_prefix        = "${var.eks_cluster_name}-workload-"
  assume_role_policy = data.aws_iam_policy_document.insighthub_irsa_assume[0].json
  tags               = local.common_tags
}

data "aws_iam_policy_document" "insighthub_secret_read" {
  count = var.enable_aws ? 1 : 0

  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.insighthub[0].arn]
  }
}

resource "aws_iam_role_policy" "insighthub_secret_read" {
  count  = var.enable_aws ? 1 : 0
  name   = "read-insighthub-runtime-secret"
  role   = aws_iam_role.insighthub_irsa[0].id
  policy = data.aws_iam_policy_document.insighthub_secret_read[0].json
}
