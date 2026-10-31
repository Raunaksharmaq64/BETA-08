# ==============================================================================
# RIGHT FIT — Security Groups & Least-Privilege Firewall Rules
# Strictly enforces zero public ingress to Database, Redis, and internal APIs
# ==============================================================================

# 1. Ingress Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Controls public inbound traffic to HTTPS/HTTP load balancer"
  vpc_id      = aws_vpc.main.id

  # Public HTTPS
  ingress {
    description = "Allow inbound HTTPS from public internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Public HTTP (For Let's Encrypt and 301 redirection)
  ingress {
    description = "Allow inbound HTTP for ACME challenge & redirect"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress to App Container Tier
  egress {
    description     = "Allow traffic to private application tier"
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  })
}

# 2. Private Application Workload Security Group (EC2 / ECS)
resource "aws_security_group" "app" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Controls traffic for private backend and frontend application containers"
  vpc_id      = aws_vpc.main.id

  # Ingress from ALB to Web Frontend (Port 3000)
  ingress {
    description     = "Inbound from ALB to Next.js frontend"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Ingress from ALB to Backend API (Port 8000)
  ingress {
    description     = "Inbound from ALB to FastAPI backend"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Inter-container communication within App tier
  ingress {
    description = "Allow container-to-container traffic within app security group"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  # Outbound HTTPS for package updates, AI APIs (Gemini), and S3
  egress {
    description = "Allow outbound HTTPS via NAT Gateway"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound to RDS PostgreSQL (Port 5432)
  egress {
    description     = "Outbound to private RDS PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rds.id]
  }

  # Outbound to Private Redis (Port 6379)
  egress {
    description     = "Outbound to private Redis cache/broker"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-app-sg"
  })
}

# 3. Isolated PostgreSQL RDS Security Group
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Controls traffic to isolated Amazon RDS PostgreSQL instance"
  vpc_id      = aws_vpc.main.id

  # Ingress strictly permitted ONLY from authorized application security group
  ingress {
    description     = "PostgreSQL ingress strictly from application tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # Zero outbound rules required for DB (No internet egress)
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  })
}

# 4. Isolated Redis Security Group
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Controls traffic to isolated Redis message broker"
  vpc_id      = aws_vpc.main.id

  # Ingress strictly permitted ONLY from application and worker security group
  ingress {
    description     = "Redis ingress strictly from application and background workers"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # Zero outbound rules required
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  })
}

