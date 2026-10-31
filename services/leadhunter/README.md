# LeadHunter Service (Freelance Opportunity Engine) — RETIRED & MIGRATED

> [!NOTE]
> **Status:** MIGRATED & RETIRED (Phase 10 — Modular Monolith Integration)
> **Active Implementation:** `rightFIT/backend/app/modules/freelance/`

## Migration Notice
The standalone LeadHunter satellite service (previously configured on port 8001) has been completely migrated into the RIGHT FIT Core backend as the native **Freelance Intelligence Module** (`app/modules/freelance`).

### Architectural Changes:
1. **Single Monolith Runtime:** Discovery scanning, website auditing, email enrichment, AI pitch writing, and outreach management run directly in-process within the main FastAPI backend on port 8000.
2. **Unified Core Database:** All opportunities, contact evidence, search history, settings, and outreach drafts reside directly within PostgreSQL via async SQLAlchemy 2.0.
3. **No Port 8001 Required:** Port 8001, external HTTP satellite hops, and `LEADHUNTER_BASE_URL` are no longer needed for production deployments.
4. **Independent Deployment:** RIGHT FIT runs independently without referencing the legacy `ai agents` folder or separate LeadHunter docker containers.
