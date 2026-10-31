# LeadHunter to RIGHT FIT Comprehensive Migration Plan

**Project:** RIGHT FIT — Freelance Intelligence Integration  
**Date:** 2026-10-31  
**Architecture:** Modular Monolith  
**Status:** APPROVED FOR STAGE-BY-STAGE EXECUTION  

---

## 1. Migration Goals & Success Criteria

1. **Native Module Integration:** Transform LeadHunter into `backend/app/modules/freelance/` within the RIGHT FIT Core FastAPI application.
2. **Infrastructure Independence:** Eliminate port 8001, `LEADHUNTER_BASE_URL`, and separate satellite containers.
3. **Database Sovereignty:** Core PostgreSQL / SQLite owns all opportunity, evidence, and outreach records.
4. **Zero Auto-Send Safety:** Outreach requires mandatory explicit candidate approval.
5. **Full Feature Parity:** Preserve Google Maps discovery, phone classification, website auditing, AI pitch generation, and WhatsApp deep links.
6. **No Regressions:** Existing RIGHT FIT job, resume, startup, and CRM modules continue functioning with all 235 tests passing.

---

## 2. Stage Breakdown & Execution Roadmap

### Stage 0: Read-Only Source Audit & Documentation
- Comprehensive audit of `ai agents` repository.
- Inventory of files, features, dependencies, database models, and routes.
- Produce 7 migration governance documents in `rightFIT/docs/migrations/leadhunter/`.

### Stage 1: Dependency Migration
- Add `google-search-results`, `phonenumbers`, `apify-client`, and `PyYAML` to `rightFIT/backend/requirements.txt`.
- Verify runtime imports and environment compatibility.
- Ensure all legacy Flask dependencies are cleanly excluded.

### Stage 2: Backend Business Logic Migration
- Create `backend/app/modules/freelance/` with:
  - `collectors/`: `base_collector.py`, `serpapi_collector.py`, `apify_collector.py`
  - `utils/`: `data_cleaner.py`, `email_scraper.py`, `website_auditor.py`, `ai_writer.py`, `whatsapp.py`, `ssrf_guard.py`
  - `prompts/`: `outreach_pitches.yaml`
  - `services/`: `freelance_discovery_service.py`, `audit_service.py`, `mockup_service.py`, `freelance_outreach_service.py`
  - `repositories/`: `freelance_repository.py`, `setting_repository.py`
  - `schemas/`: Pydantic models for search requests, drafts, and audits

### Stage 3: Database & Repositories
- Register `FreelanceSearchHistoryRecord` and `FreelanceCandidateSettingsRecord` in `app/db/models.py`.
- Ensure multi-signal deduplication and cascade relationships on `FreelanceOpportunityRecord`.
- Run database schema migration scripts.

### Stage 4: Background Tasks & Celery
- Add `backend/app/workers/tasks/freelance_tasks.py`.
- Register background search, bulk scan, and reply sync tasks in `celery_app.py` routing to the `lead_tasks` queue.
- Include local task runner fallbacks when Celery is optional or running in local dev mode.

### Stage 5: Internal API Integration & Adapter Retirement
- Update `backend/app/api/v1/endpoints/freelance.py` to invoke internal services directly.
- Convert `LeadHunterAdapter` into an in-process local adapter or retire external HTTP calls.
- Remove `LEADHUNTER_BASE_URL` dependency.

### Stage 6: Modernize Next.js Frontend UI
- Update `frontend/src/app/(dashboard)/freelance/page.tsx` with:
  - Real-time KPIs (Total Leads, Verified, Broken Websites, Contact Ready)
  - Interactive discovery search controls (Keyword, City, Provider, Depth)
  - Detailed opportunity cards with status badges and quick action buttons
- Update `[opportunityId]/page.tsx` with website audit scorecard and contact evidence ledger.
- Update `[opportunityId]/draft/page.tsx` with AI pitch workspace (PAS/BAB generation, preview, edit, copy, approve, and send).
- Update `outreach/page.tsx` with delivery activity and suppression management.

### Stage 7: Security & Reliability Hardening
- Verify SSRF guard across all scrapers (block metadata IP `169.254.169.254`, loopback, and private ranges).
- Verify candidate approval state machine (edit invalidation, body hashing).
- Validate tenant isolation on all queries.

### Stage 8: Testing & Verification
- Execute complete test suite (both existing 235 tests and new freelance module tests).
- Verify zero runtime requests to port 8001.
- Verify end-to-end user journeys for freelance discovery and outreach.

### Stage 9: Docker & Deployment Cleanup
- Update `docker-compose.yml` and `docker-compose.prod.yml` to remove the separate LeadHunter container.
- Clean up obsolete `services/leadhunter` skeleton.
- Update `start_servers.bat` and `startserver.md`.

### Stage 10: Final Documentation & Handover
- Compile final migration report with status tracking, test counts, and operational verification.
