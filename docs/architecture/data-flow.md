# Data Flow & Lifecycle Architecture

- **Title:** RIGHT FIT Data Flow & Lifecycle Architecture
- **Purpose:** Traces data lifecycles from ingestion, enrichment, matching, to presentation and archiving.
- **Status:** APPROVED
- **Owner:** Principal Architect / Data Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Resume Parsing & Matching Data Flow
```
[User Uploads PDF]
       │
       ▼ HTTPS POST /api/v1/resumes/upload
[Core Backend: FastAPI]
       │
       ├─► 1. Stream file to AWS S3 (Encrypted, Private Bucket)
       ├─► 2. Dispatch parsing task to Celery Worker
       │        │
       │        ▼
       │     [Worker: Text Extraction & Skills Tokenizer]
       │        │
       │        ▼
       ├─► 3. Store structured resume entities in `core.resumes`
       │
       ▼
[Match Calculation Engine]
       │
       ├─► Fetches candidate skills & active job criteria
       ├─► Computes fit score (0.0 - 1.0) & missing skill tokens
       └─► Persists results in `core.job_matches`
```

## 2. Freelance Opportunity Discovery Data Flow
```
[User Queries "Dentists in Miami"]
       │
       ▼ HTTPS GET /api/v1/opportunities/freelance?query=...
[Core Backend Orchestrator]
       │
       ▼ HTTP POST http://service-leadhunter:8001/api/v1/scans
[LeadHunter Service Worker]
       │
       ├─► Queries Google Maps (SerpApi / Apify)
       ├─► Tests website DNS, HTTP status, and SSL certificates
       ├─► Audits broken websites / flags missing web presence
       ├─► Discovers social links & contact emails
       └─► Stores results in `leadhunter.businesses`
       │
       ▼ Returns LeadHunter Scan Payload
[Core Backend]
       │
       ▼ Normalized Response with Actionable Pitch Drafts
[Next.js Dashboard UI]
```

## 3. Data Retention & Archival Policies
- **Inactive Job Listings:** Closed or unverified listings are soft-deleted after 45 days.
- **Audit Reports:** Generated website audit PDF files are cached in S3 for 30 days, then pruned.
- **User Data Deletion:** Complete cascade deletion across `core.users`, `core.resumes`, and `core.applications` upon GDPR/CCPA user deletion request.

## 4. Open Questions & TBDs
- [TBD] WebSocket vs. Server-Sent Events (SSE) for streaming bulk scan progress to frontend.

