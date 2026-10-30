# Service Boundaries & Ownership

- **Title:** RIGHT FIT Service Boundaries & Domain Ownership
- **Purpose:** Establishes strict architectural boundaries, data ownership, and permissible communication patterns across services.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Domain Ownership Matrix

| Domain Entity | Primary Owning Service | Database Schema | Access Rules |
| :--- | :--- | :--- | :--- |
| Users & Authentication | Core Career API | `core.users` | Read/Write by Core ONLY |
| Candidate Profiles | Core Career API | `core.profiles` | Read/Write by Core ONLY |
| Master & Tailored Resumes | Core Career API | `core.resumes` | Read/Write by Core ONLY |
| Jobs & ATS Listings | Core Career API | `core.jobs` | Read/Write by Core ONLY |
| Fit Scores & Rationales | Core Career API | `core.job_matches` | Read/Write by Core ONLY |
| Application CRM Pipelines | Core Career API | `core.applications` | Read/Write by Core ONLY |
| Local Businesses & Audits | LeadHunter Service | `leadhunter.businesses` | Read/Write by LeadHunter ONLY |
| Freelance Outreach Sequences | LeadHunter Service | `leadhunter.outreach` | Read/Write by LeadHunter ONLY |
| Startup Pain Points & Signals | Startup Intelligence | `startup_intel.pain_points` | Read/Write by Startup Intel ONLY |

## 2. Permissible Inter-Service Communication
1. **Frontend ➔ Core API:** Allowed. All client traffic flows through the Core API `/api/v1/` routes.
2. **Frontend ➔ Satellite Services:** **FORBIDDEN.** The frontend NEVER connects directly to LeadHunter or Startup Intelligence. All requests are brokered by the Core Career API.
3. **Core API ➔ Satellite Services:** Allowed via internal REST endpoints (`http://service-leadhunter:8001/api/...`) with authorization headers.
4. **Cross-Service Direct Database Writes:** **STRICTLY FORBIDDEN.** LeadHunter never writes to `core` tables; Core never writes directly to `leadhunter` tables. Data exchange must occur over REST APIs.

## 3. Failure Domain Isolation
- If the LeadHunter service experiences high latency or crashes due to Google Maps scraping limits, the Core Career API must continue serving job search, resume matching, and CRM tracking without interruption.
- Core API uses circuit breaker patterns and returns cached or empty freelance results with a `service_degraded: true` flag.

## 4. Open Questions & TBDs
- [TBD] Shared Redis instance vs. isolated Redis DB indices (DB 0 for Core, DB 1 for LeadHunter).

