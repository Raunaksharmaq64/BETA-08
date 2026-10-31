# ==============================================================================
# RIGHT FIT — IAM Roles & Least-Privilege Instance Profiles
# Session Manager (No SSH port 22), S3 Object Access, and SSM Parameter Decryption
# ==============================================================================

# 1. EC2 Service Assume Role Policy
data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app_role" {
  name               = "${var.project_name}-${var.environment}-app-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
  tags               = var.common_tags
}

# 2. Attach AWS Systems Manager Core Policy (Replaces SSH ingress with secure IAM console access)
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# 3. Custom S3 Document Access Policy (Strictly scoped to project buckets)
resource "aws_iam_policy" "s3_access" {
  name        = "${var.project_name}-${var.environment}-s3-policy"
  description = "Scoped read/write access to RIGHT FIT S3 storage buckets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3BucketListing"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.resumes.arn,
          aws_s3_bucket.backups.arn
        ]
      },
      {
        Sid    = "S3ObjectReadWrite"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.resumes.arn}/*",
          "${aws_s3_bucket.backups.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# 4. Custom SSM Parameter Store & Secrets Manager Decrypt Policy
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.project_name}-${var.environment}-secrets-policy"
  description = "Allows fetching encrypted production configurations and parameters"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "SSMParameterRead"
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}/${var.environment}/*"
      },
      {
        Sid    = "SecretsManagerRead"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.project_name}/${var.environment}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# 5. EC2 Instance Profile Container
resource "aws_iam_instance_profile" "app_profile" {
  name = "${var.project_name}-${var.environment}-instance-profile"
  role = aws_iam_role.app_role.name
  tags = var.common_tags
}

