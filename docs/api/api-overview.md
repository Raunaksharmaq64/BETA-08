# Core API Overview & Route Registry

- **Title:** RIGHT FIT Core API Overview
- **Purpose:** Catalogs public and internal REST routes exposed by the Core Career API.
- **Status:** DRAFT / ARCHITECTURE SETUP
- **Owner:** Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. API Architecture Summary
The RIGHT FIT Core API is served via FastAPI, providing automatic OpenAPI (Swagger) documentation at `/docs` and ReDoc at `/redoc`. All endpoints are namespaced under `/api/v1/`.

## 2. Master Endpoint Registry (Proposed Architecture)

### 2.1 Authentication & User Management (`/api/v1/auth`, `/api/v1/users`)
- `POST /api/v1/auth/register` — Register new user account.
- `POST /api/v1/auth/login` — Authenticate and obtain JWT access + refresh tokens.
- `POST /api/v1/auth/refresh` — Exchange refresh token for fresh access token.
- `GET  /api/v1/users/me` — Retrieve authenticated user profile and preferences.

### 2.2 Resume Intelligence (`/api/v1/resumes`)
- `POST /api/v1/resumes/upload` — Upload and parse resume document (PDF/DOCX).
- `GET  /api/v1/resumes` — List candidate resumes.
- `GET  /api/v1/resumes/{id}/skills` — Extract structured skills and proficiencies.

### 2.3 Job Discovery & Matching (`/api/v1/jobs`, `/api/v1/matching`)
- `GET  /api/v1/jobs` — Search aggregated ATS job listings.
- `GET  /api/v1/jobs/{id}` — Retrieve detailed job description and company signals.
- `POST /api/v1/matching/evaluate` — Calculate `fit_score` and rationale trace for a target job.

### 2.4 Application CRM (`/api/v1/applications`)
- `GET  /api/v1/applications` — List user tracked applications by stage.
- `POST /api/v1/applications` — Save job to application pipeline.
- `PATCH /api/v1/applications/{id}/stage` — Transition application stage (e.g. `saved` to `applied`).

### 2.5 Opportunity Hub (`/api/v1/opportunities`)
- `GET  /api/v1/opportunities/freelance` — Query local business leads (brokered to LeadHunter).
- `GET  /api/v1/opportunities/startups` — Query startup technical pain points (brokered to Startup Intel).

## 3. Open Questions & TBDs
- [TBD] Rate limits per endpoint group.

