# Architecture Compatibility & Gap Analysis

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Option A (Hybrid Architecture) Compatibility Analysis
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. Approved Target Architecture (Option A: Hybrid Modular Architecture)

Option A establishes:
1. **Unified Next.js 16 Presentation Layer:** Single dashboard serving Career intelligence, Freelance leads, and Startup pain points.
2. **Core Career Engine (FastAPI):** Central orchestrator managing identity, resumes, ATS matching, CRM stages, and satellite service brokering.
3. **Independent Freelance Service (LeadHunter):** Standalone FastAPI service running headless Google Maps scrapers and broken-site testing.
4. **Independent Startup Discovery Service (Startup Intelligence):** Standalone FastAPI service scraping community feeds and classifying pain points.
5. **Database Ownership & Schema Isolation:** Single PostgreSQL 16 engine with isolated schemas: `career_core`, `leadhunter_db`, `startup_intel_db`.
6. **Isolated Redis Task Queues:** Distinct queues: `career_tasks`, `lead_tasks`, `startup_tasks`, `notification_tasks`.

---

## 2. Compatibility Assessment Against Approved Target

| Architectural Dimension | Existing Legacy State | Target Option A Requirement | Compatibility Rating | Remediation Plan |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Presentation** | Three disconnected frontends (No frontend in `agentic-career-search`; Next.js in `ai agents`; Static HTML in `Startups-problrms-hunter`). | Unified Next.js 16 App Router dashboard in `frontend/`. | **HIGH COMPATIBILITY** | Adopt `ai agents/frontend` as baseline; integrate Job and Startup features into feature-sliced folders (`src/features/`). |
| **Core Career Engine** | `agentic-career-search` is an autonomous worker engine without user identity or resume storage. | Central identity provider and API orchestrator for RIGHT FIT. | **MEDIUM COMPATIBILITY** | Ingest LeadHunter's `UserModel` and JWT infrastructure into `backend/app/modules/auth/` and `backend/app/modules/users/`. |
| **LeadHunter Service** | Full-stack monolith tightly bound to its own Next.js UI and Celery workers. | Independent satellite service exposing REST endpoints (`services/leadhunter`). | **HIGH COMPATIBILITY** | Decouple backend from frontend; expose internal REST endpoints defined in `contracts/leads/`. |
| **Startup Intelligence Service**| Single script running FastAPI with synchronous JSON file writes (`data/leads.json`). | Independent satellite service with PostgreSQL persistence (`services/startup_intelligence`). | **MEDIUM COMPATIBILITY** | Replace `leads.json` with PostgreSQL `startup_intel.pain_points` table; wrap behind REST endpoints (`contracts/pain_points/`). |
| **Database Ownership** | Fragmented: SQLite/PostgreSQL in `agentic-career-search`; PostgreSQL in `ai agents`; JSON files in `Startups-problrms-hunter`. | Schema-isolated PostgreSQL database (`core`, `leadhunter`, `startup_intel`). | **HIGH COMPATIBILITY** | Implement schema separation in Phase 1 using SQLAlchemy / SQLModel multi-schema metadata. |
| **Background Processing** | Custom asyncio loop in `agentic-career-search`; Celery + Redis in `ai agents`; no queue in `Startups-problrms-hunter`. | Celery + Redis with isolated queues (`career_tasks`, `lead_tasks`, etc.). | **HIGH COMPATIBILITY** | Standardize worker definitions on Celery with `task_routes` mapping tasks to distinct Redis queues. |

---

## 3. Boundary & Coupling Vulnerabilities Identified

1. **Frontend-to-Private Service Coupling:**
   - In `ai agents`, frontend components directly trigger Celery background tasks.
   - *Target Rule:* The frontend must NEVER communicate directly with LeadHunter or Startup Intelligence. All requests must route through `backend/app/api/v1/` in Core.
2. **Missing Inter-Service Authentication:**
   - Neither satellite service currently supports service-to-service API key verification.
   - *Target Rule:* Core Backend must pass `X-Internal-Service-Key` header, validated by FastAPI middleware on satellite services.
3. **Circular Import & Dependency Hygiene:**
   - In `ai agents`, legacy Flask files (`app.py`, `models.py`) coexist with modern FastAPI files (`app_fastapi.py`, `models_async.py`).
   - *Target Rule:* Exclude all legacy Flask modules when packaging `services/leadhunter`.

---

## 4. Recommendations for Subsequent Phases

* **Phase 1 (Core Foundation):** Implement Core database schema (`core.users`, `core.profiles`, `core.resumes`, `core.jobs`) and establish JWT authentication before porting business logic.
* **Phase 1.5 (Satellite Migration):** Modernize Startup Intelligence data layer by introducing SQLAlchemy models for pain points and evidence.
* **Phase 2 (Unified Presentation):** Build the Next.js 16 UI using shadcn/ui components, pulling data exclusively from Core API endpoints.

