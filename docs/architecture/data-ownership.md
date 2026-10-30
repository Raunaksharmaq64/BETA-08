# Data Ownership & Schema Isolation Specification

- **Title:** RIGHT FIT Data Ownership & Storage Boundaries
- **Purpose:** Mandates database schema ownership, queue routing, cross-service boundary rules, and migration governance.
- **Status:** APPROVED
- **Owner:** Database Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## 1. Relational Database Ownership (PostgreSQL 16)

RIGHT FIT enforces schema-level database isolation within a single managed PostgreSQL instance:

```
                            PostgreSQL 16 Database Engine
        ┌──────────────────────────────────┬──────────────────────────────────┐
        │                                  │                                  │
        ▼                                  ▼                                  ▼
   [ Schema: career_core ]        [ Schema: leadhunter_db ]     [ Schema: startup_intel_db ]
   - users                        - businesses                  - startups
   - profiles                     - website_audits              - discovery_sources
   - skills                       - leads                       - pain_points
   - resumes                      - contacts                    - evidence
   - jobs                         - outreach_logs               - pitch_drafts
   - job_matches                  - imap_replies
   - applications
   - interviews
```

### Schema Authority:
1. **`career_core`:** Owned exclusively by the Core Career Engine (`backend/app/modules/`). Managed via Core Alembic migrations (`backend/alembic/`).
2. **`leadhunter_db`:** Owned exclusively by LeadHunter AI (`services/leadhunter/`). Managed via LeadHunter migrations.
3. **`startup_intel_db`:** Owned exclusively by Startup Intelligence (`services/startup_intelligence/`). Managed via Startup Intelligence migrations.

---

## 2. Strict Boundary Rules
* **No Cross-Schema Queries:** No service is permitted to execute SQL joins across schema boundaries (e.g. `SELECT * FROM career_core.users JOIN leadhunter_db.leads`).
* **API Data Exchange:** If Core requires lead data, it calls `GET http://service-leadhunter:8001/api/v1/leads` over internal HTTP.
* **Foreign Key Boundaries:** Foreign keys between tables belonging to different schemas are strictly prohibited. Inter-service relationships are modeled via logical string/UUID identifiers.

---

## 3. Redis Queue Ownership & Task Routing

Task queues are partitioned within Redis 7 using distinct queue names:

| Queue Name | Owning Service | Task Types Processed | Concurrency Policy |
| :--- | :--- | :--- | :--- |
| **`career_tasks`** | Core Career Engine | Resume parsing, deterministic match scoring, job ingestion batching | High concurrency (Worker pool: 4-8) |
| **`lead_tasks`** | LeadHunter AI | Google Maps API queries, headless browser website audits, social crawls | Rate-limited concurrency (Worker pool: 2-4) |
| **`startup_tasks`** | Startup Intelligence | Reddit/GitHub/HN scrapers, Gemini opportunity classification | Rate-limited concurrency (Worker pool: 2) |
| **`notification_tasks`**| Core Career Engine | Transactional emails, follow-up cadence reminders, alert dispatch | High priority, immediate dispatch |

---

## 4. Failure Isolation & Consistency
* **Eventual Consistency:** Data between Core and satellite services is eventually consistent.
* **Transactional Integrity:** Each service manages its own local database transactions. No distributed 2-Phase Commit (2PC) transactions are permitted.
* **Graceful Degradation:** If `leadhunter_db` is unavailable, Core returns cached results or an empty list with a service-degraded flag rather than failing the candidate's request.

