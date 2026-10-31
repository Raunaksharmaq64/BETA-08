# ==============================================================================
# RIGHT FIT — CloudWatch Logging, Metrics & Actionable Operational Alarms
# ==============================================================================

# 1. Centralized Log Group for Application & Nginx Access Logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/${var.project_name}/${var.environment}"
  retention_in_days = 30
  tags              = var.common_tags
}

# 2. SNS Topic for Operational Alerts & Incident Notification
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-operational-alerts"
  tags = var.common_tags
}

# 3. CloudWatch Metric Alarm: High EC2 CPU Utilization (> 85% for 10 minutes)
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ec2-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Triggered when EC2 application container host CPU exceeds 85% for 10 mins"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.app_server.id
  }

  tags = var.common_tags
}

# 4. CloudWatch Metric Alarm: RDS Free Storage Space (< 5GB remaining)
resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-storage-critical"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 5000000000 # 5 GB in bytes
  alarm_description   = "Triggered when PostgreSQL database remaining free disk drops below 5GB"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.identifier
  }

  tags = var.common_tags
}

# 5. CloudWatch Metric Alarm: RDS High Connection Starvation (> 85 active connections)
resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-connection-starvation"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 180
  statistic           = "Maximum"
  threshold           = 85
  alarm_description   = "Triggered when PostgreSQL active connections approach connection pool limits"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.identifier
  }

  tags = var.common_tags
}

