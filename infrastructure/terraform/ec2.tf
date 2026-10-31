# ==============================================================================
# RIGHT FIT — Application Compute Layer (EC2 / Docker Host)
# Bootstrapped with Docker, non-root user, AWS SSM, and automated recovery
# ==============================================================================

# 1. Latest Amazon Linux 2023 ARM64 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-arm64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# 2. Production EC2 Instance
resource "aws_instance" "app_server" {
  ami                  = data.aws_ami.amazon_linux_2023.id
  instance_type        = var.app_instance_type
  subnet_id            = aws_subnet.private_app_1.id
  iam_instance_profile = aws_iam_instance_profile.app_profile.name

  vpc_security_group_ids = [aws_security_group.app.id]

  root_block_device {
    volume_size           = 60
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true

    tags = merge(var.common_tags, {
      Name = "${var.project_name}-${var.environment}-root-ebs"
    })
  }

  user_data = <<-EOF
              #!/bin/bash
              set -euo pipefail
              echo "=== Bootstrapping RIGHT FIT Application Host ==="

              # System updates and package installation
              dnf update -y
              dnf install -y docker git curl htop jq python3-pip

              # Start and enable Docker engine
              systemctl enable --now docker
              usermod -aG docker ec2-user

              # Install Docker Compose Plugin v2
              mkdir -p /usr/local/lib/docker/cli-plugins
              curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-aarch64 \
                -o /usr/local/lib/docker/cli-plugins/docker-compose
              chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

              # Verify AWS Systems Manager Agent is running
              systemctl enable --now amazon-ssm-agent

              echo "=== Bootstrap Completed Successfully ==="
              EOF

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-app-server"
  })
}

