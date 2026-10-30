# Dependency & Blocker Matrix

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Technical Dependencies, Infrastructure Preconditions & Blocker Matrix
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. Blocking Infrastructure Preconditions

| Blocker ID | Dependency / Precondition | Current Status | Impact on Phase 1 Implementation | Required Remediation | Resolution Owner |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BLK-01** | **Docker Engine / Docker Desktop** | NOT INSTALLED in host PATH. | **BLOCKER** for local multi-container testing and Docker Compose verification. | Install Docker Desktop on Windows host or configure remote Docker daemon. | Developer / DevOps (UNASSIGNED) |
| **BLK-02** | **PostgreSQL Database Instance** | PostgreSQL server not actively running locally. | **BLOCKER** for executing local Alembic database migrations. | Spin up local PostgreSQL container or provide cloud connection string (`DATABASE_URL`). | Database Lead (UNASSIGNED) |
| **BLK-03** | **Redis Server** | Redis server not actively running locally. | Blocks running Celery background worker tasks offline. | Launch local Redis container (`redis:7-alpine`) on port 6379. | DevOps (UNASSIGNED) |

---

## 2. API Quotas & External Service Dependencies

| Dependency | Category | Required For | Fallback Mechanism Present? | Quota Limitations | Criticality |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Gemini API** | AI & LLM | Resume bullet generation, pitch drafting, STAR stories | YES (Deterministic offline templates) | 15 requests per minute on free tier. | HIGH |
| **SerpApi Key** | External Scraper | Google Maps business discovery | YES (Can fall back to Apify) | 100 searches/mo on free tier. | HIGH |
| **Apify Token** | External Scraper | Google Maps scraping alternative | YES (Can fall back to SerpApi) | $5 monthly platform credit. | MEDIUM |
| **GitHub REST API** | Community Scraper | "Help wanted" issue discovery | NO (Public scraping blocked if rate-limited) | 60 requests/hr unauthenticated; 5,000 req/hr with PAT. | MEDIUM |
| **Reddit User-Agent** | Community Scraper | Reddit r/saas and r/startups feed ingestion | NO | Rate-limited if user-agent is generic. | MEDIUM |
| **SMTP Mailbox** | Email Outbound | Transactional alerts and pitch email dispatch | NO (Requires valid SMTP host & credentials) | Gmail personal limit: 500 emails/day. | MEDIUM |

---

## 3. Library & Framework Compatibility Dependencies

| Component | Upstream Dependency | Incompatible Downstream Elements | Resolution Strategy |
| :--- | :--- | :--- | :--- |
| **Core Database ORM** | SQLAlchemy 2.0.35 | Legacy SQLModel in LeadHunter relies on SQLAlchemy 2.x internally. | Align both services on SQLAlchemy 2.x async engines (`asyncpg`). |
| **Schema Validation** | Pydantic v2 | Legacy code in `Startups-problrms-hunter` uses untyped dictionaries; `agentic-career-search` uses Pydantic v2. | Enforce Pydantic v2 schemas across all API boundaries (`contracts/`). |
| **PDF/DOCX Extraction** | Binary file parser | No existing library present in `pyproject.toml` or `requirements.txt`. | Add `pypdf` (or `pdfminer.six`) and `python-docx` to `backend/requirements.txt` in Phase 1. |

---

## 4. Required Technical Decisions Prior to Phase 1

1. **Authentication Architecture Decision:** Formally approve porting the JWT authentication and user management system from `ai agents` into the Core Career Engine (`backend/app/modules/auth/`).
2. **Startup Intelligence Storage Decision:** Formally approve deprecating file-based `leads.json` in favor of a relational PostgreSQL schema (`startup_intel`).
3. **Frontend Integration Decision:** Formally approve adopting `ai agents/frontend` (Next.js 16 + Tailwind CSS) as the unified frontend baseline for RIGHT FIT.

