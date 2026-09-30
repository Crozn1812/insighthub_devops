resource "aws_security_group" "eks_workloads" {
  count       = var.enable_aws ? 1 : 0
  name_prefix = "${var.eks_cluster_name}-workloads-"
  description = "Workload security context for InsightHub"
  vpc_id      = var.vpc_id

  tags = merge(local.common_tags, { Name = "${var.eks_cluster_name}-workloads" })
}

resource "aws_vpc_security_group_egress_rule" "eks_workloads_ipv4" {
  count             = var.enable_aws ? 1 : 0
  security_group_id = aws_security_group.eks_workloads[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Workload egress; ingress remains restricted"
}

resource "aws_security_group" "rds" {
  count       = var.enable_aws ? 1 : 0
  name_prefix = "${var.eks_cluster_name}-rds-"
  description = "Private PostgreSQL access from InsightHub workloads"
  vpc_id      = var.vpc_id

  tags = merge(local.common_tags, { Name = "${var.eks_cluster_name}-rds" })
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_workloads" {
  count                        = var.enable_aws ? 1 : 0
  security_group_id            = aws_security_group.rds[0].id
  referenced_security_group_id = aws_security_group.eks_workloads[0].id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  description                  = "PostgreSQL from InsightHub workloads only"
}

resource "aws_security_group" "redis" {
  count       = var.enable_aws ? 1 : 0
  name_prefix = "${var.eks_cluster_name}-redis-"
  description = "Private Redis access from InsightHub workloads"
  vpc_id      = var.vpc_id

  tags = merge(local.common_tags, { Name = "${var.eks_cluster_name}-redis" })
}

resource "aws_vpc_security_group_ingress_rule" "redis_from_workloads" {
  count                        = var.enable_aws ? 1 : 0
  security_group_id            = aws_security_group.redis[0].id
  referenced_security_group_id = aws_security_group.eks_workloads[0].id
  from_port                    = 6379
  to_port                      = 6379
  ip_protocol                  = "tcp"
  description                  = "Redis from InsightHub workloads only"
}
