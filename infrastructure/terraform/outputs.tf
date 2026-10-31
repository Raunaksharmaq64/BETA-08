# ==============================================================================
# RIGHT FIT — Terraform Outputs Reference
# ==============================================================================

output "vpc_id" {
  description = "Identifier of the created Virtual Private Cloud"
  value       = aws_vpc.main.id
}

output "public_subnets" {
  description = "Public subnet identifiers"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_app_subnets" {
  description = "Private application subnet identifiers"
  value       = [aws_subnet.private_app_1.id, aws_subnet.private_app_2.id]
}

output "isolated_db_subnets" {
  description = "Isolated database subnet identifiers"
  value       = [aws_subnet.isolated_db_1.id, aws_subnet.isolated_db_2.id]
}

output "app_server_id" {
  description = "Instance ID of the container compute host"
  value       = aws_instance.app_server.id
}

output "app_server_private_ip" {
  description = "Private IP address of the container compute host"
  value       = aws_instance.app_server.private_ip
}

output "rds_endpoint" {
  description = "Amazon RDS PostgreSQL connection address (Private)"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "Amazon RDS PostgreSQL listening port"
  value       = aws_db_instance.postgres.port
}

output "s3_resumes_bucket" {
  description = "Private S3 bucket name for candidate resumes"
  value       = aws_s3_bucket.resumes.bucket
}

output "s3_backups_bucket" {
  description = "Private S3 bucket name for automated backups"
  value       = aws_s3_bucket.backups.bucket
}

output "sns_alerts_topic_arn" {
  description = "Amazon SNS Topic ARN for operational alerts"
  value       = aws_sns_topic.alerts.arn
}

