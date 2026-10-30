# Naming Conventions

- **Title:** RIGHT FIT Universal Naming Conventions
- **Purpose:** Standardizes identifier naming across backend Python, frontend TypeScript, database schemas, queues, and REST APIs.
- **Status:** APPROVED
- **Owner:** Principal Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## 1. Python Conventions (Backend & Services)
- **Files & Modules:** `snake_case.py` (e.g., `resume_service.py`, `job_matcher.py`)
- **Functions & Methods:** `snake_case()` (e.g., `calculate_fit_score()`, `extract_skills()`)
- **Variables & Attributes:** `snake_case` (e.g., `user_id`, `is_active`)
- **Classes & Pydantic Models:** `PascalCase` (e.g., `CandidateProfile`, `ResumeAnalysisResponse`)
- **Constants & Enums:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`, `JWT_ALGORITHM`)

---

## 2. TypeScript & React Conventions (Frontend)
- **Component Files:** `PascalCase.tsx` (e.g., `JobCard.tsx`, `LeadTable.tsx`)
- **Hook Files:** `useCamelCase.ts` (e.g., `useJobSearch.ts`, `useAuth.ts`)
- **Utility / Lib Files:** `camelCase.ts` (e.g., `apiClient.ts`, `formatters.ts`)
- **Types & Interfaces:** `PascalCase` (e.g., `CandidateProfile`, `OpportunityFilter`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PAGE_SIZE`, `API_TIMEOUT_MS`)

---

## 3. Database Conventions (PostgreSQL)
- **Schemas:** `snake_case` (e.g., `career_core`, `leadhunter_db`, `startup_intel_db`)
- **Tables:** `snake_case`, plural nouns (e.g., `users`, `resumes`, `job_postings`, `leads`)
- **Columns:** `snake_case` (e.g., `first_name`, `created_at`, `is_verified`)
- **Primary Keys:** Always `id` (`UUID` or `BIGINT`)
- **Foreign Keys:** `<singular_entity>_id` (e.g., `user_id`, `job_id`, `company_id`)
- **Timestamps:** `created_at`, `updated_at`, `deleted_at` (all `TIMESTAMPTZ`)
- **Booleans:** Prefix with `is_`, `has_`, or `can_` (e.g., `is_active`, `has_website`)

---

## 4. API & Endpoint Conventions
- **Base URI:** `/api/v1/`
- **Resource Nouns:** Plural nouns in lowercase kebab-case (e.g., `/api/v1/resumes`, `/api/v1/job-matches`)
- **HTTP Methods:**
  - `GET`: Retrieve resource or collection.
  - `POST`: Create resource or execute non-idempotent action.
  - `PUT`: Full update / replacement of resource.
  - `PATCH`: Partial update of resource fields.
  - `DELETE`: Remove or soft-delete resource.

---

## 5. Redis Queues & Asynchronous Events
- **Queue Names:** Lowercase `snake_case` nouns suffixed with `_tasks` (e.g., `career_tasks`, `lead_tasks`, `startup_tasks`, `notification_tasks`).
- **Event Type Names:** Dot-separated lowercase nouns with past-tense action (e.g., `run.created`, `resume.parsed`, `lead.audited`, `outreach.sent`).

---

## 6. Environment Variables
- **Naming Format:** `UPPER_SNAKE_CASE` with descriptive domain prefixes:
  - `DATABASE_URL`, `POSTGRES_USER`, `REDIS_URL`
  - `JWT_SECRET`, `JWT_ALGORITHM`
  - `GEMINI_API_KEY`, `SERPAPI_KEY`
  - `LEADHUNTER_BASE_URL`, `STARTUP_INTELLIGENCE_BASE_URL`

---

## 7. Folder & Directory Conventions
- **Backend Modules:** `snake_case` (e.g., `backend/app/modules/market_intelligence/`)
- **Frontend Routes & Features:** `kebab-case` (e.g., `src/app/(dashboard)/market-intelligence/`)
- **Documentation & Infrastructure:** Lowercase descriptive names (e.g., `docs/integrations/`, `infrastructure/nginx/`)
