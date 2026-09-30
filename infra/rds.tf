resource "aws_db_subnet_group" "insighthub" {
  count       = var.enable_aws ? 1 : 0
  name_prefix = "${var.eks_cluster_name}-db-"
  subnet_ids  = var.private_subnet_ids
  tags        = local.common_tags
}

resource "aws_db_parameter_group" "insighthub" {
  count       = var.enable_aws ? 1 : 0
  name_prefix = "${var.eks_cluster_name}-postgres16-"
  family      = "postgres16"
  description = "PostgreSQL 16 logging baseline for InsightHub"

  parameter {
    name         = "log_statement"
    value        = "all"
    apply_method = "immediate"
  }

  parameter {
    name         = "rds.force_ssl"
    value        = "1"
    apply_method = "immediate"
  }

  tags = local.common_tags
}

resource "aws_db_instance" "insighthub" {
  count = var.enable_aws ? 1 : 0

  identifier_prefix               = "${var.eks_cluster_name}-"
  engine                          = "postgres"
  engine_version                  = "16"
  instance_class                  = var.db_instance_class
  allocated_storage               = var.db_allocated_storage
  storage_type                    = "gp3"
  storage_encrypted               = true
  db_name                         = "insighthub"
  username                        = "insighthub_admin"
  manage_master_user_password     = true
  db_subnet_group_name            = aws_db_subnet_group.insighthub[0].name
  parameter_group_name            = aws_db_parameter_group.insighthub[0].name
  vpc_security_group_ids          = [aws_security_group.rds[0].id]
  publicly_accessible             = false
  multi_az                        = var.db_multi_az
  backup_retention_period         = 7
  copy_tags_to_snapshot           = true
  deletion_protection             = var.db_deletion_protection
  skip_final_snapshot             = true
  auto_minor_version_upgrade      = true
  performance_insights_enabled    = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  apply_immediately               = false
  tags                            = local.common_tags
}

# PostgreSQL 16 is provisioned here. The pgvector extension is initialized by
# infra/db/init.sql through an authorized migration/bootstrap step in a real
# deployment. It is not a shared_preload_libraries setting.
