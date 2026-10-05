locals {
  common_tags = {
    project     = var.project
    environment = var.environment
    owner       = var.owner
    cost_center = var.cost_center
    managed_by  = var.managed_by
  }
}
