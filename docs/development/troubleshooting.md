# Developer Troubleshooting Guide

- **Title:** Engineering Troubleshooting & Common Failure Recovery
- **Purpose:** Diagnostic runbooks for database locks, port collisions, cache issues, and external API throttling.
- **Status:** APPROVED
- **Owner:** Backend Lead / DevOps (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Port Collisions
**Symptom:** `Error response from daemon: driver failed programming external connectivity on endpoint ... address already in use`  
**Diagnosis & Resolution:**
- Check for existing native services occupying ports 5432, 6379, 3000, or 8000.
- Windows PowerShell: `Get-NetTCPConnection -LocalPort 5432`
- Stop the colliding process or alter port mapping in `.env`.

## 2. Database Migration Conflicts (Alembic)
**Symptom:** `alembic.util.exc.CommandError: Multiple head revisions are present for given argument 'head'`  
**Diagnosis & Resolution:**
- Two branches created migrations simultaneously.
- Run `alembic merge heads -m "merge conflicting heads"` and test migration forward/backward.

## 3. Gemini / Third-Party API Quota Exhaustion
**Symptom:** `429 Too Many Requests: Resource has been exhausted`  
**Diagnosis & Resolution:**
- The system gracefully falls back to template mode.
- Update the API key in `.env` with a non-throttled key or adjust rate-limiting throttle parameters in `core/config.py`.

## 4. Open Questions & TBDs
- [TBD] Automated healthcheck diagnostic script (`scripts/maintenance/doctor.py`).

