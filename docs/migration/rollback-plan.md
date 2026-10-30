# Migration Rollback & Emergency Contingency Plan

- **Title:** Migration Rollback & Contingency Procedures
- **Purpose:** Governs failover strategies, data rollback procedures, and service isolation in the event of migration failures.
- **Status:** APPROVED
- **Owner:** Principal Architect / DevOps (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Zero-Risk Legacy Safeguard
- **Fundamental Rule:** The three legacy prototype directories (`../agentic-career-search`, `../ai agents`, `../Startups-problrms-hunter`) are never modified during the migration.
- If a catastrophic regression occurs in RIGHT FIT during integration, the legacy applications can be run independently in their original states immediately.

## 2. Database Migration Rollback Runbook
1. If an Alembic migration introduces schema corruptions in `core`:
   ```bash
   cd backend
   alembic downgrade -1
   ```
2. If schema rollback fails due to irreversible DDL:
   - Restore PostgreSQL from the pre-migration snapshot:
     ```bash
     pg_restore -U rightfit_admin -d rightfit_core -c pre_migration_backup.dump
     ```

## 3. Service Circuit Breaking Rollback
- If the new LeadHunter REST bridge fails to respond:
  - Toggle feature flag in `core/config.py`: `ENABLE_FREELANCE_MODULE=false`.
  - Core API will serve job matching and career workflows normally without 500 errors.

## 4. Open Questions & TBDs
- [TBD] Automated canary rollback triggers based on error rate thresholds (> 5%).

