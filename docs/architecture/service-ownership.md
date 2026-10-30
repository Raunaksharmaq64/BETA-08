# Service Ownership Specification

- **Title:** RIGHT FIT Service Ownership & Capability Mapping
- **Purpose:** Formally maps product capabilities, domain boundaries, data models, and communication interfaces to owning services.
- **Status:** APPROVED
- **Owner:** Principal Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## 1. Initial Service Ownership Map

| Service Name | Primary Responsibility | Data Ownership | Primary Interface |
| :--- | :--- | :--- | :--- |
| **Core Career Engine** | Career discovery, user identity, resume intelligence, ATS job matching, application tracking CRM, and opportunity orchestration | `career_core` | Core REST API (`/api/v1/*`) |
| **LeadHunter AI** | Freelance and local business lead discovery, website availability and broken-site auditing, social profile crawling | `leadhunter_db` | Internal REST API (Port 8001) |
| **Startup Intelligence** | Startup research, developer community scanning (Reddit, GitHub, HN), technical pain-point classification | `startup_intel_db` | Internal REST API (Port 8002) |
| **Next.js Frontend** | User experience, responsive dashboards, interactive Kanban pipelines, authentication sessions | No direct service DB ownership | Web Browser / Core REST API |

---

## 2. Capability & Asset Ownership Matrix

| System Capability / Asset | Primary Owning Service | Supporting Infrastructure | Access Policy |
| :--- | :--- | :--- | :--- |
| **Authentication & Identity** | Core Career Engine | `career_core.users` | Protected JWT Bearer tokens |
| **Candidate Profiles** | Core Career Engine | `career_core.profiles` | Authenticated user tenancy |
| **Resume Documents & Text** | Core Career Engine | AWS S3 Bucket (`resumes/`) & `career_core.resumes` | AES-256 encrypted, pre-signed URLs |
| **Job Postings & ATS Adapters** | Core Career Engine | `career_core.jobs`, `career_core.source_configs` | Ingested via 70+ source adapters |
| **Job Matches & Rationales** | Core Career Engine | `career_core.job_matches` | Deterministic score traces (0–100%) |
| **Application CRM Pipelines** | Core Career Engine | `career_core.applications` | Auditable stage transition machine |
| **Freelance Business Leads** | LeadHunter AI | `leadhunter_db.leads`, `businesses` | Internal REST queries from Core |
| **Website Audit Metrics** | LeadHunter AI | `leadhunter_db.website_audits` | Internal REST queries from Core |
| **Startup Pain Points** | Startup Intelligence | `startup_intel_db.pain_points` | Internal REST queries from Core |
| **Raw Scraped Evidence** | Startup Intelligence | `startup_intel_db.evidence` | Internal REST queries from Core |
| **Outbound Email & Outreach** | LeadHunter AI / Core | SMTP Gateway / Celery Worker | Strict Human-in-the-Loop review |
| **System Notifications** | Core Career Engine | Redis queue `notification_tasks` | In-app alerts and transactional email |
| **AI Gateway & Prompts** | Core Career Engine | Google Gemini API Adapter | Structured Pydantic validation |

---

## 3. Boundary Directives
1. **Frontend Isolation:** The frontend communicates strictly with the Core Career Engine. Private service ports (8001, 8002) are not exposed to the public internet or the browser.
2. **Database Isolation:** Cross-service database queries (`SELECT ... FROM leadhunter_db...`) are **strictly prohibited**. All data exchange occurs over HTTP REST contracts.
3. **Failure Isolation:** An outage or rate-limiting block in LeadHunter or Startup Intelligence must never prevent candidates from searching jobs or tracking applications in the Core Career Engine.

