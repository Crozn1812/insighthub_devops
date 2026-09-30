resource "aws_elasticache_subnet_group" "insighthub" {
  count      = var.enable_aws ? 1 : 0
  name       = "${var.eks_cluster_name}-redis"
  subnet_ids = var.private_subnet_ids
  tags       = local.common_tags
}

resource "aws_elasticache_replication_group" "insighthub" {
  count = var.enable_aws ? 1 : 0

  replication_group_id       = "${var.eks_cluster_name}-redis"
  description                = "Private Redis 7 for InsightHub"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = var.redis_node_type
  port                       = 6379
  num_cache_clusters         = var.redis_num_cache_clusters
  automatic_failover_enabled = true
  multi_az_enabled           = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  subnet_group_name          = aws_elasticache_subnet_group.insighthub[0].name
  security_group_ids         = [aws_security_group.redis[0].id]
  apply_immediately          = false
  tags                       = local.common_tags
}
