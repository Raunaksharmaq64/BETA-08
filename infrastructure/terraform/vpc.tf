# ==============================================================================
# RIGHT FIT — Multi-Tier VPC Networking Architecture
# 3-Tier Subnet Topology: Public Ingress, Private App, Isolated Database
# ==============================================================================

# 1. Dedicated VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc"
  })
}

# 2. Internet Gateway for Public Subnets
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-igw"
  })
}

# 3. Public Ingress Subnets (Tier 1: ALB / NAT Gateway)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-1"
    Tier = "Public"
  })
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = var.availability_zones[1]
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-2"
    Tier = "Public"
  })
}

# 4. Elastic IP & NAT Gateway for Outbound Egress from Private Subnets
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  })
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1.id

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-nat-gw"
  })

  depends_on = [aws_internet_gateway.igw]
}

# 5. Private Application Subnets (Tier 2: Workloads / Containers)
resource "aws_subnet" "private_app_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = var.availability_zones[0]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-app-1"
    Tier = "PrivateApp"
  })
}

resource "aws_subnet" "private_app_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = var.availability_zones[1]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-app-2"
    Tier = "PrivateApp"
  })
}

# 6. Isolated Database Subnets (Tier 3: RDS PostgreSQL & Redis — ZERO Internet Route)
resource "aws_subnet" "isolated_db_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = var.availability_zones[0]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-isolated-db-1"
    Tier = "IsolatedDB"
  })
}

resource "aws_subnet" "isolated_db_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.21.0/24"
  availability_zone = var.availability_zones[1]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-isolated-db-2"
    Tier = "IsolatedDB"
  })
}

# 7. Route Tables
# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-public-rt"
  })
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Private App Route Table (Routes outbound internet via NAT Gateway)
resource "aws_route_table" "private_app" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-private-app-rt"
  })
}

resource "aws_route_table_association" "private_app_1" {
  subnet_id      = aws_subnet.private_app_1.id
  route_table_id = aws_route_table.private_app.id
}

resource "aws_route_table_association" "private_app_2" {
  subnet_id      = aws_subnet.private_app_2.id
  route_table_id = aws_route_table.private_app.id
}

# Isolated Database Route Table (Strictly Local VPC routing only — ZERO default route)
resource "aws_route_table" "isolated_db" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-isolated-db-rt"
  })
}

resource "aws_route_table_association" "isolated_db_1" {
  subnet_id      = aws_subnet.isolated_db_1.id
  route_table_id = aws_route_table.isolated_db.id
}

resource "aws_route_table_association" "isolated_db_2" {
  subnet_id      = aws_subnet.isolated_db_2.id
  route_table_id = aws_route_table.isolated_db.id
}

