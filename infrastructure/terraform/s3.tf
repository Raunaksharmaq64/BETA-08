# ==============================================================================
# RIGHT FIT — S3 Private Object Storage & Lifecycle Management
# Enforces Block Public Access, TLS 1.2+, SSE Encryption, and Lifecycle Archival
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Candidate Resumes Storage Bucket
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "resumes" {
  bucket        = "${var.project_name}-resumes-${var.environment}"
  force_destroy = var.environment == "production" ? false : true

  tags = merge(var.common_tags, {
    Name    = "${var.project_name}-resumes-${var.environment}"
    Purpose = "CandidateResumeStorage"
  })
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning for auditability & recovery
resource "aws_s3_bucket_versioning" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Server-Side Encryption at Rest
resource "aws_s3_bucket_server_side_encryption_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle Management: Transition older versions to Standard-IA
resource "aws_s3_bucket_lifecycle_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  rule {
    id     = "archive-older-resumes"
    status = "Enabled"

    transition {
      days          = 60
      storage_class = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Strict TLS 1.2+ Only Policy
resource "aws_s3_bucket_policy" "resumes_tls_only" {
  bucket = aws_s3_bucket.resumes.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnforceTLSRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.resumes.arn,
          "${aws_s3_bucket.resumes.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# 2. Database & Artifact Backups Bucket
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "backups" {
  bucket        = "${var.project_name}-backups-${var.environment}"
  force_destroy = var.environment == "production" ? false : true

  tags = merge(var.common_tags, {
    Name    = "${var.project_name}-backups-${var.environment}"
    Purpose = "DisasterRecoveryBackups"
  })
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backup-retention-lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365 # 1 year compliance retention
    }
  }
}

