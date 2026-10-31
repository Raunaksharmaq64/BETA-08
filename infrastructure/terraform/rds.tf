# ==============================================================================
# RIGHT FIT — Production Amazon RDS PostgreSQL 16
# Fully isolated within private subnet tier, encrypted at rest, TLS enforced
# ==============================================================================

# 1. DB Subnet Group (Resides strictly in Tier 3 Isolated Subnets)
resource "aws_db_subnet_group" "main" {
  name        = "${var.project_name}-${var.environment}-db-subnet-group"
  description = "Isolated database subnet group with no public routing"
  subnet_ids  = [aws_subnet.isolated_db_1.id, aws_subnet.isolated_db_2.id]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  })
}

# 2. Parameter Group Enforcing SSL/TLS and Connection Logging
resource "aws_db_parameter_group" "pg16" {
  name        = "${var.project_name}-${var.environment}-pg16-params"
  family      = "postgres16"
  description = "Hardened parameter group for PostgreSQL 16"

  parameter {
    name  = "rds.force_ssl"
    value = "1" # Enforces TLS for all connections
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "statement_timeout"
    value = "30000" # 30 seconds query timeout to protect connection pool
  }

  tags = var.common_tags
}

# 3. Random Secret for Initial Master Password (Stored securely in AWS Secrets Manager)
resource "random_password" "db_master_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}/${var.environment}/rds-credentials"
  description             = "Master PostgreSQL credentials for RIGHT FIT RDS instance"
  recovery_window_in_days = 7

  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    username = var.rds_master_username
    password = random_password.db_master_password.result
    database = var.rds_database_name
  })
}

# 4. Amazon RDS PostgreSQL Database Instance
resource "aws_db_instance" "postgres" {
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.rds_instance_class

  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.rds_database_name
  username = var.rds_master_username
  password = random_password.db_master_password.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.pg16.name

  # Security: Absolute prohibition of public ingress
  publicly_accessible = false

  # High Availability & Backup
  multi_az                  = var.environment == "production" ? true : false
  backup_retention_period   = var.backup_retention_days
  backup_window             = "03:00-04:00"
  maintenance_window        = "sun:04:30-sun:05:30"
  copy_tags_to_snapshot     = true
  deletion_protection       = var.environment == "production" ? true : false
  skip_final_snapshot       = var.environment == "production" ? false : true
  final_snapshot_identifier = "${var.project_name}-${var.environment}-final-snapshot"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-postgres"
  })
}

