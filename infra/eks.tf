data "aws_iam_policy_document" "eks_cluster_assume" {
  count = var.enable_aws ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_cluster" {
  count              = var.enable_aws ? 1 : 0
  name_prefix        = "${var.eks_cluster_name}-cluster-"
  assume_role_policy = data.aws_iam_policy_document.eks_cluster_assume[0].json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "eks_cluster" {
  count      = var.enable_aws ? 1 : 0
  role       = aws_iam_role.eks_cluster[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

data "aws_caller_identity" "current" {
  count = var.enable_aws ? 1 : 0
}

data "aws_iam_policy_document" "eks_kms" {
  count = var.enable_aws ? 1 : 0

  statement {
    sid       = "AccountKeyAdministration"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current[0].account_id}:root"]
    }
  }

  statement {
    sid = "AllowEksSecretsEncryption"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*",
    ]
    resources = ["*"]

    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current[0].account_id]
    }
  }
}

resource "aws_kms_key" "eks" {
  count                   = var.enable_aws ? 1 : 0
  description             = "EKS secrets encryption for ${var.eks_cluster_name}"
  enable_key_rotation     = true
  deletion_window_in_days = 7
  policy                  = data.aws_iam_policy_document.eks_kms[0].json
  tags                    = local.common_tags
}

resource "aws_kms_alias" "eks" {
  count         = var.enable_aws ? 1 : 0
  name          = "alias/${var.eks_cluster_name}-secrets"
  target_key_id = aws_kms_key.eks[0].key_id
}

resource "aws_eks_cluster" "insighthub" {
  count    = var.enable_aws ? 1 : 0
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = var.eks_kubernetes_version

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = false
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks[0].arn
    }
    resources = ["secrets"]
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster]
  tags       = local.common_tags
}

data "aws_iam_policy_document" "eks_nodes_assume" {
  count = var.enable_aws ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_nodes" {
  count              = var.enable_aws ? 1 : 0
  name_prefix        = "${var.eks_cluster_name}-nodes-"
  assume_role_policy = data.aws_iam_policy_document.eks_nodes_assume[0].json
  tags               = local.common_tags
}

locals {
  eks_node_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
  ]
}

resource "aws_iam_role_policy_attachment" "eks_nodes" {
  for_each   = var.enable_aws ? toset(local.eks_node_policy_arns) : toset([])
  role       = aws_iam_role.eks_nodes[0].name
  policy_arn = each.value
}

resource "aws_launch_template" "eks_nodes" {
  count         = var.enable_aws ? 1 : 0
  name_prefix   = "${var.eks_cluster_name}-nodes-"
  instance_type = var.eks_node_instance_types[0]

  vpc_security_group_ids = [
    aws_eks_cluster.insighthub[0].vpc_config[0].cluster_security_group_id,
    aws_security_group.eks_workloads[0].id,
  ]

  tag_specifications {
    resource_type = "instance"
    tags          = merge(local.common_tags, { Name = "${var.eks_cluster_name}-node" })
  }

  tags = local.common_tags
}

resource "aws_eks_node_group" "insighthub" {
  count           = var.enable_aws ? 1 : 0
  cluster_name    = aws_eks_cluster.insighthub[0].name
  node_group_name = "${var.eks_cluster_name}-workers"
  node_role_arn   = aws_iam_role.eks_nodes[0].arn
  subnet_ids      = var.private_subnet_ids
  instance_types  = var.eks_node_instance_types

  scaling_config {
    min_size     = var.eks_node_min_size
    desired_size = var.eks_node_desired_size
    max_size     = var.eks_node_max_size
  }

  launch_template {
    id      = aws_launch_template.eks_nodes[0].id
    version = aws_launch_template.eks_nodes[0].latest_version
  }

  depends_on = [aws_iam_role_policy_attachment.eks_nodes]
  tags       = local.common_tags
}

resource "kubernetes_namespace_v1" "insighthub" {
  count = var.enable_aws ? 1 : 0

  metadata {
    name   = var.insighthub_namespace
    labels = local.common_tags
  }

  depends_on = [aws_eks_node_group.insighthub]
}
