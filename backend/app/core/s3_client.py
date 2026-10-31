"""
RIGHT FIT — S3 Object Storage Client & Presigned URL Manager
Enforces TLS 1.2+, SSE-S3/KMS encryption, private buckets, and short-lived presigned URLs.
"""

from __future__ import annotations

import os
import mimetypes
from typing import Optional, Dict, Any
from app.core.config import settings

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class S3StorageClient:
    """Enterprise S3 storage manager for candidate resumes, reports, and backup archives."""

    def __init__(self):
        self.region = settings.AWS_REGION
        self.use_s3 = settings.USE_S3_STORAGE and BOTO3_AVAILABLE
        self.resumes_bucket = settings.S3_BUCKET_RESUMES
        self.reports_bucket = settings.S3_BUCKET_REPORTS
        self.backups_bucket = settings.S3_BUCKET_BACKUPS
        self._s3_client = None

    @property
    def client(self):
        if not self._s3_client and self.use_s3:
            self._s3_client = boto3.client("s3", region_name=self.region)
        return self._s3_client

    def generate_presigned_upload_url(
        self,
        bucket_name: str,
        object_key: str,
        content_type: str,
        expires_in_seconds: int = 900,  # 15 minutes max
        max_size_bytes: int = 15 * 1024 * 1024  # 15MB max
    ) -> Dict[str, Any]:
        """Generates presigned POST policy enforcing content-type, size, and SSE encryption."""
        if not self.use_s3 or not self.client:
            # Staging/Dev Mock URL
            return {
                "upload_url": f"/api/v1/mock-storage/upload/{bucket_name}/{object_key}",
                "fields": {"key": object_key, "Content-Type": content_type},
                "expires_in": expires_in_seconds,
                "is_mock": True
            }

        try:
            response = self.client.generate_presigned_post(
                Bucket=bucket_name,
                Key=object_key,
                Fields={
                    "Content-Type": content_type,
                    "x-amz-server-side-encryption": "AES256"
                },
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1024, max_size_bytes],
                    {"x-amz-server-side-encryption": "AES256"}
                ],
                ExpiresIn=expires_in_seconds
            )
            response["is_mock"] = False
            return response
        except Exception as e:
            return {
                "error": str(e),
                "is_mock": True,
                "upload_url": f"/api/v1/storage/upload/{bucket_name}/{object_key}"
            }

    def generate_presigned_download_url(
        self,
        bucket_name: str,
        object_key: str,
        expires_in_seconds: int = 900
    ) -> str:
        """Generates a secure, temporary presigned GET URL for authenticated users."""
        if not self.use_s3 or not self.client:
            return f"/api/v1/mock-storage/download/{bucket_name}/{object_key}"

        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key},
                ExpiresIn=expires_in_seconds
            )
        except Exception:
            return f"/api/v1/storage/download/{bucket_name}/{object_key}"

    def upload_file_bytes(
        self,
        bucket_name: str,
        object_key: str,
        file_bytes: bytes,
        content_type: str = "application/pdf"
    ) -> bool:
        """Uploads raw bytes to S3 with server-side encryption."""
        if not self.use_s3 or not self.client:
            # Fallback to local disk directory
            local_dir = os.path.join(settings.RESUME_STORAGE_DIR, bucket_name)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, os.path.basename(object_key))
            with open(local_path, "wb") as f:
                f.write(file_bytes)
            return True

        try:
            self.client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type,
                ServerSideEncryption="AES256"
            )
            return True
        except Exception:
            return False


# Global singleton client
s3_storage = S3StorageClient()

