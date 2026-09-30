variable "project" {
  description = "Project identifier used for resource tagging."
  type        = string
  default     = "insighthub"

  validation {
    condition     = length(trimspace(var.project)) > 0
    error_message = "project must not be blank."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "owner" {
  description = "Team accountable for the infrastructure."
  type        = string
  default     = "platform-team"

  validation {
    condition     = length(trimspace(var.owner)) > 0
    error_message = "owner must not be blank."
  }
}

variable "cost_center" {
  description = "Cost allocation label."
  type        = string
  default     = "training"

  validation {
    condition     = length(trimspace(var.cost_center)) > 0
    error_message = "cost_center must not be blank."
  }
}

variable "managed_by" {
  description = "Automation owner for managed resources."
  type        = string
  default     = "terraform"

  validation {
    condition     = length(trimspace(var.managed_by)) > 0
    error_message = "managed_by must not be blank."
  }
}

variable "aws_region" {
  description = "Region represented by the future static AWS architecture."
  type        = string
  default     = "ap-southeast-1"

  validation {
    condition     = length(trimspace(var.aws_region)) > 0
    error_message = "aws_region must not be blank."
  }
}

variable "enable_aws" {
  description = "Explicit opt-in for AWS resources; remains false on the local-only track."
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "Existing VPC for the disabled AWS architecture."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = !var.enable_aws || try(length(trimspace(var.vpc_id)) > 0, false)
    error_message = "vpc_id must be supplied when enable_aws is true."
  }
}

variable "private_subnet_ids" {
  description = "Existing private subnets spanning at least two availability zones."
  type        = list(string)
  default     = []

  validation {
    condition     = !var.enable_aws || length(var.private_subnet_ids) >= 2
    error_message = "At least two private_subnet_ids are required when enable_aws is true."
  }
}

variable "eks_cluster_name" {
  description = "Name of the optional EKS cluster."
  type        = string
  default     = "insighthub-dev"
}

variable "eks_kubernetes_version" {
  description = "Kubernetes minor version for the optional EKS cluster."
  type        = string
  default     = "1.34"
}

variable "eks_node_instance_types" {
  description = "Conservative instance types for the educational managed node group."
  type        = list(string)
  default     = ["t3.medium"]

  validation {
    condition     = length(var.eks_node_instance_types) > 0
    error_message = "eks_node_instance_types must not be empty."
  }
}

variable "eks_node_min_size" {
  description = "Minimum managed node count."
  type        = number
  default     = 1
}

variable "eks_node_desired_size" {
  description = "Desired managed node count."
  type        = number
  default     = 1
}

variable "eks_node_max_size" {
  description = "Maximum managed node count."
  type        = number
  default     = 2
}

variable "db_instance_class" {
  description = "Conservative RDS instance class for a short lab run."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GiB."
  type        = number
  default     = 20

  validation {
    condition     = var.db_allocated_storage >= 20
    error_message = "db_allocated_storage must be at least 20 GiB."
  }
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for a future non-lab deployment."
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Protect a future database from accidental deletion."
  type        = bool
  default     = false
}

variable "redis_node_type" {
  description = "Conservative ElastiCache node type for a short lab run."
  type        = string
  default     = "cache.t4g.micro"
}

variable "redis_num_cache_clusters" {
  description = "Number of cache nodes in the optional replication group."
  type        = number
  default     = 2

  validation {
    condition     = var.redis_num_cache_clusters >= 2 && var.redis_num_cache_clusters <= 6
    error_message = "redis_num_cache_clusters must be between 2 and 6 for failover."
  }
}

variable "insighthub_namespace" {
  description = "Namespace bound into the future IRSA trust policy."
  type        = string
  default     = "insighthub-dev"

  validation {
    condition     = length(trimspace(var.insighthub_namespace)) > 0
    error_message = "insighthub_namespace must not be blank."
  }
}

variable "insighthub_service_account" {
  description = "ServiceAccount bound into the future IRSA trust policy."
  type        = string
  default     = "insighthub"

  validation {
    condition     = length(trimspace(var.insighthub_service_account)) > 0
    error_message = "insighthub_service_account must not be blank."
  }
}
