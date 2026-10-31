# ==============================================================================
# RIGHT FIT — Terraform Infrastructure as Code Variables
# Parameterized, environment-aware configuration with zero embedded secrets
# ==============================================================================

variable "aws_region" {
  description = "Target AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (production, staging, dev)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name identifier used in resource tagging and naming"
  type        = string
  default     = "rightfit"
}

variable "vpc_cidr" {
  description = "CIDR block for the dedicated Virtual Private Cloud"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for multi-AZ resiliency"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "app_instance_type" {
  description = "EC2 compute instance type for container application workload"
  type        = string
  default     = "t4g.xlarge" # 4 vCPU, 16GB RAM ARM64 Graviton
}

variable "rds_instance_class" {
  description = "Amazon RDS instance class for PostgreSQL 16"
  type        = string
  default     = "db.t4g.medium" # 2 vCPU, 4GB RAM
}

variable "rds_allocated_storage" {
  description = "Initial allocated storage for RDS in GB"
  type        = number
  default     = 50
}

variable "rds_max_allocated_storage" {
  description = "Autoscaling storage upper ceiling in GB"
  type        = number
  default     = 500
}

variable "rds_database_name" {
  description = "Initial master database name"
  type        = string
  default     = "rightfit_core"
}

variable "rds_master_username" {
  description = "Master database administrator username"
  type        = string
  default     = "rightfit_admin"
}

variable "backup_retention_days" {
  description = "Automated snapshot retention window in days"
  type        = number
  default     = 30
}

variable "common_tags" {
  description = "Common billing and ownership resource tags"
  type        = map(string)
  default = {
    Project     = "RIGHT_FIT"
    ManagedBy   = "Terraform"
    Environment = "production"
    CostCenter  = "CoreEngineering"
  }
}

