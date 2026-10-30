# Schema & Table Ownership Matrix

- **Title:** Database Schema Ownership & Entity Boundaries
- **Purpose:** Mandates strict ownership, table inventory, and cross-schema query restrictions.
- **Status:** APPROVED
- **Owner:** Database Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Core Career Engine Schema (`core`)
Owned exclusively by `backend/app/modules/`.
* `core.users` — User credentials, roles, settings, subscription tiers.
* `core.profiles` — Candidate personal data, education, target salary, location preferences.
* `core.skills` — Master skill taxonomy and ontology relations.
* `core.resumes` — Uploaded resume documents, extracted text, and parsed metadata.
* `core.jobs` — Aggregated and normalized job listings from 50+ ATS platforms.
* `core.job_matches` — Deterministic fit scores, matched skills, and rationale traces.
* `core.applications` — CRM pipeline records (`saved`, `applied`, `interview`, `offer`).
* `core.interviews` — STAR stories, interview schedules, and post-interview debrief notes.
* `core.market_intelligence` — Salary band benchmarks and company compensation signals.

## 2. LeadHunter Freelance Schema (`leadhunter`)
Owned exclusively by `services/leadhunter`.
* `leadhunter.businesses` — Discovered local business records and geolocations.
* `leadhunter.website_audits` — Audit results (DNS, SSL, HTTP status, load time, tech stack).
* `leadhunter.leads` — Qualified prospects missing websites or hosting broken sites.
* `leadhunter.contacts` — Discovered owner/manager emails, phone numbers, and social links.
* `leadhunter.outreach` — Generated proposal pitch drafts and SMTP dispatch status.
* `leadhunter.replies` — Inbound client responses tracked via IMAP.

## 3. Startup Intelligence Schema (`startup_intel`)
Owned exclusively by `services/startup_intelligence`.
* `startup_intel.startups` — Target startup profiles and online footprints.
* `startup_intel.discovery_sources` — Source metadata (Reddit posts, GitHub issues, Product Hunt launches).
* `startup_intel.pain_points` — Detected bugs, slow performance, framework upgrades, and hiring signals.
* `startup_intel.evidence` — Raw text excerpts and source permalinks.
* `startup_intel.tech_findings` — Identified technologies and libraries (React, Shopify, Postgres).
* `startup_intel.pitch_drafts` — Customized developer consulting proposals.

## 4. Cross-Schema Direct Query Prohibition
- **STRICT PROHIBITION:** No service may execute direct SQL joins or transactions across schema boundaries (e.g. `SELECT * FROM core.users JOIN leadhunter.leads`).
- Shared identifiers must be passed over REST API contracts.

## 5. Open Questions & TBDs
- [TBD] Separate database users with restricted schema-level GRANT permissions.

