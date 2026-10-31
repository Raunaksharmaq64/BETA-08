#!/usr/bin/env bash
# ==============================================================================
# RIGHT FIT — PostgreSQL Disaster Recovery Restore Script
# Restores from verified .dump file into target database
# WARNING: NEVER RESTORE OVER ACTIVE PRODUCTION DATABASE
# ==============================================================================
set -euo pipefail

BACKUP_FILE="${1:-}"
TARGET_DB="${2:-rightfit_restore_test}"
DB_USER="${POSTGRES_USER:-rightfit_admin}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

if [ -z "${BACKUP_FILE}" ] || [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file must be provided and must exist."
    echo "Usage: $0 /path/to/backup.dump [target_db_name]"
    exit 1
fi

CHECKSUM_FILE="${BACKUP_FILE}.sha256"
if [ -f "${CHECKSUM_FILE}" ]; then
    echo "=== [Restore] Verifying SHA256 integrity checksum ==="
    sha256sum -c "${CHECKSUM_FILE}"
    echo "[Restore] Integrity check PASSED."
else
    echo "WARNING: Checksum file not found; proceeding with unverified restore."
fi

echo "=== [Restore] Restoring ${BACKUP_FILE} into ${TARGET_DB} on ${DB_HOST}:${DB_PORT} ==="

# Create isolated target database if it does not exist
PGPASSWORD="${POSTGRES_PASSWORD:-}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${TARGET_DB};" || true

# Execute pg_restore
PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_restore \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${TARGET_DB}" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    -v \
    "${BACKUP_FILE}"

echo "=== [Restore] Database restore completed successfully into ${TARGET_DB} ==="

