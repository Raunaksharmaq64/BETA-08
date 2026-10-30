# Product Requirements Document (PRD)

- **Title:** RIGHT FIT Comprehensive Product Requirements
- **Purpose:** Specifies functional and non-functional requirements for the RIGHT FIT platform across all modules.
- **Status:** DRAFT
- **Owner:** Product Management (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Functional Requirements

### 1.1 Authentication & Profile Management
* **FR-AUTH-01:** System must support secure email/password registration with email verification.
* **FR-AUTH-02:** System must issue short-lived JWT access tokens (60 min) and rotating refresh tokens (7 days).
* **FR-USER-01:** Candidates must be able to maintain multiple tailored resumes, skills taxonomies, and compensation goals.

### 1.2 Resume Analysis & ATS Matching
* **FR-RES-01:** System must parse PDF and DOCX resume uploads and extract structured skills, experiences, and education.
* **FR-RES-02:** Engine must compute a deterministic `fit_score` (0.0 to 1.0) against target job descriptions.
* **FR-RES-03:** Engine must output clear missing keyword recommendations to improve ATS compatibility.

### 1.3 Job Discovery & Aggregation
* **FR-JOB-01:** Platform must ingest job postings from 50+ ATS sources (Ashby, Greenhouse, Lever, Workday, etc.).
* **FR-JOB-02:** Engine must deduplicate listings based on title, company, and location normalization.
* **FR-JOB-03:** System must detect ghost job signals (post age > 60 days, repost frequency).

### 1.4 Application Management (CRM-Lite)
* **FR-APP-01:** Kanban stage tracker for `saved`, `applied`, `interviewing`, `offer`, `rejected`, `withdrawn`.
* **FR-APP-02:** Automated follow-up cadence reminders (7-day, 14-day check-in alerts).
* **FR-APP-03:** Human-in-the-loop: No automated application submissions without explicit user confirmation.

### 1.5 Freelance & Local Business Intelligence (LeadHunter)
* **FR-LEAD-01:** Discovers local businesses from Google Maps without active or working websites.
* **FR-LEAD-02:** Performs automated technical audits (DNS, HTTP, SSL, mobile responsiveness).
* **FR-LEAD-03:** Extracts owner emails and social profiles; drafts personalized outreach pitches.

### 1.6 Startup Opportunity Mining
* **FR-START-01:** Scrapes developer discussions on Reddit, GitHub ("help wanted"), and Hacker News.
* **FR-START-02:** Classifies detected pain points (performance, migrations, bugs) into outreach leads.

## 2. Non-Functional Requirements
* **NFR-PERF-01:** API response time P95 < 250ms for cached/indexed queries.
* **NFR-SEC-01:** All stored documents encrypted at rest using AES-256.
* **NFR-AVAIL-01:** 99.9% uptime target for Core API and frontend dashboard.
* **NFR-SCALE-01:** Support 10,000 active daily users and 500,000 indexed job postings.

## 3. Open Questions & TBDs
- [TBD] Rate limit quotas per user subscription tier.
- [TBD] Storage retention period for uploaded candidate resumes.

