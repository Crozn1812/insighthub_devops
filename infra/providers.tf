provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

data "aws_eks_cluster_auth" "insighthub" {
  count = var.enable_aws ? 1 : 0
  name  = aws_eks_cluster.insighthub[0].name
}

provider "kubernetes" {
  host  = var.enable_aws ? aws_eks_cluster.insighthub[0].endpoint : "https://127.0.0.1"
  token = var.enable_aws ? data.aws_eks_cluster_auth.insighthub[0].token : null
  cluster_ca_certificate = var.enable_aws ? base64decode(
    aws_eks_cluster.insighthub[0].certificate_authority[0].data
  ) : null
}
