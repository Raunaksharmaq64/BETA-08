# Legacy Component Reuse Matrix

- **Title:** Component Disposition & Reuse Strategy Matrix
- **Purpose:** Classifies every major legacy module under REUSE, API_INTEGRATION, REWRITE, or DROP with architectural justification.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Strategy Taxonomy
- `REUSE`: Port logic directly into modular RIGHT FIT architecture with type enhancements and tests.
- `API_INTEGRATION`: Maintain as independent service; communicate via REST contracts.
- `REWRITE`: Rebuild from scratch to meet new performance or security requirements.
- `DROP`: Deprecate or discard due to redundancy or fragility.

## 2. Component Disposition Matrix

| Source Repository | Module / Component | Target Destination | Strategy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `agentic-career-search` | 50+ ATS Source Adapters | `backend/app/integrations/job_sources/` | `REUSE` | Mature, clean Pydantic data models and web scrapers. |
| `agentic-career-search` | Deterministic Decision & Fit Engine | `backend/app/modules/matching/` | `REUSE` | High value, explainable scoring with unit tests. |
| `agentic-career-search` | Compensation & Benefit Calculators | `backend/app/modules/compensation/` | `REUSE` | Comprehensive domain logic (RSU, clawback, cobra). |
| `agentic-career-search` | Application CRM State Machine | `backend/app/modules/applications/` | `REUSE` | Enforces auditable stage progressions. |
| `agentic-career-search` | Automated Submission Scripts | N/A | `DROP` | Violates Human-in-the-Loop policy. |
| `ai agents` (LeadHunter) | Full LeadHunter Platform | `services/leadhunter/` | `API_INTEGRATION` | Complete working service with Celery and Postgres. |
| `ai agents` (LeadHunter) | Standalone Next.js UI | N/A | `DROP` | Merged into unified Next.js 16 frontend in `frontend/`. |
| `Startups-problrms-hunter`| Community Scraper Engine | `services/startup_intelligence/` | `API_INTEGRATION` | Proven web crawling logic across 7+ platforms. |
| `Startups-problrms-hunter`| File-based JSON Database | PostgreSQL (`startup_intel`) | `REWRITE` | File persistence is unsuitable for concurrent production. |
| `Startups-problrms-hunter`| Vanilla HTML/JS Dashboard | N/A | `DROP` | Replaced by unified Next.js dashboard. |

## 3. Open Questions & TBDs
- [TBD] Refactoring legacy Celery task names to avoid namespace collisions.

