# Technical Risk Register

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Phase 0 Technical, Security & Operational Risk Register
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. Risk Evaluation Matrix

| ID | Risk Description | Technical Evidence | Impact | Likelihood | Severity | Mitigation Strategy | Owner | Review Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **Docker Tooling Missing on Host Environment** | `docker : The term 'docker' is not recognized` returned when testing host PATH. | High (Blocks containerized local builds and deployment verification). | High | **CRITICAL** | Install Docker Desktop or Docker Engine on host Windows environment prior to Phase 1 containerization. | UNASSIGNED | TBD |
| **RSK-02** | **Startup Intelligence Concurrency Corruptions** | `Startups-problrms-hunter/main.py:50` reads and writes `leads.json` synchronously via `json.dump()`. | High (Data loss or race condition overwrites when multiple scans run). | High | **HIGH** | Replace JSON file persistence with PostgreSQL relational schema (`startup_intel.pain_points`) in Phase 1. | UNASSIGNED | TBD |
| **RSK-03** | **Host IP Blacklisting from Direct SMTP Verification** | `Startups-problrms-hunter/email_verifier.py:35` performs live SMTP `RCPT TO` commands against destination MX servers. | High (Host IP blacklisted by Spamhaus/Barracuda, blocking all outbound emails). | High | **HIGH** | Drop direct SMTP socket verification. Replace with passive DNS MX verification and B2B email lookup APIs. | UNASSIGNED | TBD |
| **RSK-04** | **Unbounded Third-Party Scraper Billing** | `ai agents/backend/services/search_service.py` invokes SerpApi / Apify with configurable `max_results`. | High (Unexpected cloud bills exceeding $500/mo if users launch repeated bulk scans). | Medium | **HIGH** | Enforce strict per-user daily search quotas and admin spend alert triggers in `services/leadhunter`. | UNASSIGNED | TBD |
| **RSK-05** | **Lack of Multi-Tenant Authorization in Career Engine** | `agentic-career-search/src/autoapply_agent/api/routes_runs.py` has no authentication dependencies. | High (Unauthorized access to candidate jobs and run cancellations). | High | **HIGH** | Ingest LeadHunter's JWT auth module into Core Backend and enforce user ID tenancy on all routes. | UNASSIGNED | TBD |
| **RSK-06** | **Third-Party AI API Quota Exhaustion** | Google Gemini Free tier limits (15 RPM) can be rapidly exhausted during multi-source signal analysis. | Medium (Temporary 429 throttling errors on AI pitch and STAR story generation). | Medium | **MEDIUM** | Implement exponential backoff, request queuing in Celery, and fallback to local deterministic templates. | UNASSIGNED | TBD |
| **RSK-07** | **Legacy Framework Duplication in LeadHunter** | `ai agents/backend` contains coexisting Flask (`app.py`) and FastAPI (`app_fastapi.py`) dependencies. | Medium (Confusion for future developers, dependency bloat, potential security holes). | Low | **MEDIUM** | Isolate and package only FastAPI modules when containerizing `services/leadhunter`. | UNASSIGNED | TBD |
| **RSK-08** | **Zero Automated Test Coverage in Startup Intelligence** | `Startups-problrms-hunter` contains 0 test files across its entire directory tree. | Medium (Undetected regressions during refactoring or schema migrations). | High | **MEDIUM** | Author comprehensive Pytest unit and contract test suites during Phase 1.5 satellite isolation. | UNASSIGNED | TBD |
| **RSK-09** | **ATS Scraping Fragility & Structural Breakage** | `agentic-career-search/src/autoapply_agent/adapters/*.py` relies on external HTML DOM selectors. | Medium (Job boards updating DOM classes breaks parsing for specific ATS providers). | Medium | **MEDIUM** | Maintain existing fallback selectors; leverage JSON-LD schemas where available; monitor adapter error metrics. | UNASSIGNED | TBD |
| **RSK-10** | **Candidate PII Exposure via Unencrypted Resume Files** | Candidate resumes contain personal emails, phone numbers, and career histories. | High (Compliance failure under GDPR/CCPA if documents are exposed publicly). | Low | **HIGH** | Store all uploaded resumes in encrypted AWS S3 buckets (AES-256) with expiring pre-signed URLs. | UNASSIGNED | TBD |

