# Backup & Restore Runbook

## 1. Automated Backup Cadence
- Daily database dumps execute via cron at 02:30 UTC:
  ```bash
  bash infrastructure/backups/backup_postgres.sh
  ```
- Generates custom binary archive (`pg_dump -F c`), computes SHA256 checksum, and uploads to `s3://rightfit-backups-production/postgres/`.

## 2. Restore Procedure into Isolated Database
> **WARNING**: Never restore a backup directly over the active production database without disaster recovery authorization.

1. Download backup artifact and verify SHA256 integrity:
   ```bash
   aws s3 cp s3://rightfit-backups-production/postgres/rightfit_core_20261031.dump .
   aws s3 cp s3://rightfit-backups-production/postgres/rightfit_core_20261031.dump.sha256 .
   sha256sum -c rightfit_core_20261031.dump.sha256
   ```
2. Execute restore script against isolated recovery database:
   ```bash
   bash infrastructure/backups/restore_postgres.sh rightfit_core_20261031.dump rightfit_isolated_test
   ```
3. Run verification test script:
   ```bash
   python infrastructure/backups/test_backup_restore_cycle.py
   ```

