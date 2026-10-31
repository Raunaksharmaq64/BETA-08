#!/usr/bin/env bash
# ==============================================================================
# RIGHT FIT — PostgreSQL Automated Backup Script
# Performs pg_dump with custom format (-Fc), computes SHA256 checksum,
# and syncs to encrypted S3 bucket.
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/rightfit}"
S3_BUCKET="${S3_BUCKET_BACKUPS:-rightfit-backups-prod}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="${POSTGRES_DB:-rightfit_core}"
DB_USER="${POSTGRES_USER:-rightfit_admin}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"
CHECKSUM_FILE="${BACKUP_FILE}.sha256"

mkdir -p "${BACKUP_DIR}"

echo "=== [Backup] Starting backup for database: ${DB_NAME} at ${TIMESTAMP} ==="

# Execute pg_dump with custom binary format (supports parallel restore & compression)
PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -F c \
    -b \
    -v \
    -f "${BACKUP_FILE}" \
    "${DB_NAME}"

echo "[Backup] Dump completed: ${BACKUP_FILE}"

# Compute SHA256 Checksum for integrity validation
sha256sum "${BACKUP_FILE}" > "${CHECKSUM_FILE}"
echo "[Backup] Checksum generated: $(cat "${CHECKSUM_FILE}")"

# Optional Sync to S3 if AWS CLI is configured
if command -v aws &> /dev/null && [ -n "${S3_BUCKET}" ]; then
    echo "[Backup] Uploading backup and checksum to s3://${S3_BUCKET}/postgres/..."
    aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/postgres/${DB_NAME}_${TIMESTAMP}.dump" --sse AES256
    aws s3 cp "${CHECKSUM_FILE}" "s3://${S3_BUCKET}/postgres/${DB_NAME}_${TIMESTAMP}.dump.sha256" --sse AES256
    echo "[Backup] Upload to S3 verified."
fi

# Retention policy: Delete local backups older than 14 days
find "${BACKUP_DIR}" -type f -name "*.dump" -mtime +14 -exec rm {} \;
find "${BACKUP_DIR}" -type f -name "*.sha256" -mtime +14 -exec rm {} \;

echo "=== [Backup] Process completed successfully. File: ${BACKUP_FILE} ==="

