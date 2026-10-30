# Database Backup & Recovery Runbook

- **Title:** PostgreSQL Backup & Disaster Recovery Procedures
- **Purpose:** Governs scheduled snapshots, WAL archiving, restore validation, and RTO/RPO targets.
- **Status:** APPROVED
- **Owner:** Database Administrator / DevOps (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Backup Schedule & Strategy
- **Nightly Full Backup:** Executed via `pg_dump` in custom compressed directory format at 02:00 UTC.
- **Offsite Replication:** Encrypted with AES-256 and pushed to AWS S3 (`s3://rightfit-db-backups/prod/`).
- **Retention Policy:**
  - Daily snapshots: Retained 14 days.
  - Weekly snapshots: Retained 8 weeks.
  - Monthly snapshots: Retained 12 months.

## 2. Restore Procedures (Dry-Run Verification)
1. Provision isolated staging database container.
2. Pull latest snapshot from S3:
   ```bash
   aws s3 cp s3://rightfit-db-backups/prod/db-2026-10-30.dump.gz ./
   ```
3. Execute restore using `pg_restore`:
   ```bash
   pg_restore -U rightfit_admin -d rightfit_recovery -v db-2026-10-30.dump.gz
   ```
4. Verify record counts and run integrity queries on `core.users` and `core.jobs`.

## 3. Recovery Targets
- **RTO (Recovery Time Objective):** < 60 minutes from incident declaration.
- **RPO (Recovery Point Objective):** < 24 hours (Phase 1); < 15 minutes with streaming WAL in Phase 3.

## 4. Open Questions & TBDs
- [TBD] AWS RDS automated snapshot retention vs. custom script.

