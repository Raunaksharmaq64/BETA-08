# Feature Reuse & Disposition Matrix

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Feature Disposition & Technical Reuse Matrix
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. Governance Classifications
Every capability is mapped to exactly one primary strategy:
* `REUSE` — High code quality, modular, tested; port directly into RIGHT FIT Core with type annotations.
* `API_INTEGRATION` — Autonomous external service; maintain independently and integrate via versioned REST contracts.
* `REWRITE` — Fragile, unscalable, or incompatible implementation; rebuild cleanly to production standards.
* `DROP` — Redundant, obsolete, non-compliant with Human-in-the-Loop policies, or discarded.

---

## 2. Nine-Module Disposition Matrix

| Module & Feature | Source Repository | Implementation Evidence | Actual Status | Decision | Justification & Risk Analysis | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Module 1: Overview Dashboard** | | | | | | |
| Metric Aggregation & Funnel Charts | `ai agents` (LeadHunter) | `backend/routes_fastapi/dashboard.py` | VERIFIED | `REUSE` | Clean conversion and activity metrics logic; adaptable to Core opportunities. | HIGH |
| Glassmorphic UI Dashboard | `ai agents` (LeadHunter) | `frontend/src/app/(dashboard)/dashboard/` | VERIFIED | `REUSE` | Next.js 16 App Router UI with modern glassmorphism components; serves as unified UI baseline. | HIGH |
| Static Vanilla JS UI | `Startups-problrms-hunter`| `public/index.html`, `public/app.js` | VERIFIED | `DROP` | Replaced by unified Next.js 16 frontend; maintaining separate static UI creates fragmentation. | HIGH |
| **Module 2: Resume Intelligence** | | | | | | |
| ATS Keyword Coverage Scorer | `agentic-career-search` | `services/ats_keyword_coverage.py` | VERIFIED | `REUSE` | Deterministic keyword extraction from JD matched against resume text; 100% test pass. | HIGH |
| Skills-Profile Fit Evaluator | `agentic-career-search` | `services/skills_fit.py` | VERIFIED | `REUSE` | Pure function API producing `fit_score` (0.0 to 1.0) and matched/missing skill lists. | HIGH |
| Binary PDF/DOCX Parser | None | None (Only text strings supported) | NOT IMPLEMENTED | `REWRITE` | Neither repository has binary document parsing. Implement secure `pypdf` / `docx2txt` service in Phase 1. | HIGH |
| Candidate Fact Persistence | None | `Job` model only; no `Resume` model | NOT IMPLEMENTED | `REWRITE` | Create `core.resumes` table to store structured candidate facts and parsed skill vectors. | HIGH |
| **Module 3: AI Job Discovery** | | | | | | |
| 70+ ATS Source Adapters | `agentic-career-search` | `src/autoapply_agent/adapters/*.py` | VERIFIED | `REUSE` | Complete parsers for Greenhouse, Lever, Ashby, Workday, BambooHR, etc. Extensively unit-tested. | HIGH |
| Job Normalization & Deduplication| `agentic-career-search` | `services/cross_source_dedup.py` | VERIFIED | `REUSE` | Title, company, and location normalization with fuzzy title token overlap. | HIGH |
| Job Inactive / Ghosting Detector | `agentic-career-search` | `services/application_ghosting.py` | VERIFIED | `REUSE` | Evaluates posting freshness, cadence, and repost signals to flag stale listings. | HIGH |
| Automated Job Submissions | `agentic-career-search` | Mentioned in legacy roadmap | NOT IMPLEMENTED | `DROP` | Strictly prohibited by RIGHT FIT Human-in-the-Loop policy. | HIGH |
| **Module 4: Opportunity Intelligence Engine** | | | | | | |
| Deterministic Decision Engine | `agentic-career-search` | `services/agent_decision.py`, `scoring.py` | VERIFIED | `REUSE` | Scores listings deterministically with explicit audit rationale traces; 100% test pass. | HIGH |
| Explainable Match Traces | `agentic-career-search` | `services/scoring.py` | VERIFIED | `REUSE` | Produces human-readable explanations of why a role was ranked or prioritized. | HIGH |
| Multi-Modal Opportunity Hub | None | Concept only | NOT IMPLEMENTED | `REWRITE` | Build unified Core orchestrator querying Jobs, Freelance Leads, and Startup Pain Points. | HIGH |
| **Module 5: Application CRM** | | | | | | |
| Application Stage Machine | `agentic-career-search` | `services/application_stages.py` | VERIFIED | `REUSE` | Rigorous state machine enforcing valid transitions: `saved` ➔ `applied` ➔ `interview` ➔ `offer`. | HIGH |
| Follow-up Cadence Planner | `agentic-career-search` | `services/followup_cadence.py` | VERIFIED | `REUSE` | Recommends post-application check-in intervals (7-day, 14-day) without auto-sending. | HIGH |
| CRM Database Persistence | `ai agents` (LeadHunter) | `backend/models/models_async.py` | PARTIAL | `REUSE` | Extract LeadHunter's relational pipeline patterns and apply to `core.applications`. | HIGH |
| **Module 6: Freelance Opportunity Finder** | | | | | | |
| Google Maps Local Lead Scraper | `ai agents` (LeadHunter) | `backend/services/search_service.py` | VERIFIED | `API_INTEGRATION` | Discovers businesses lacking websites via SerpApi / Apify. Keep inside LeadHunter service. | HIGH |
| Broken Website Technical Auditor| `ai agents` (LeadHunter) | `backend/utils/site_health.py` | VERIFIED | `API_INTEGRATION` | Tests DNS, SSL, HTTP status, and mobile responsiveness. Keep inside LeadHunter service. | HIGH |
| Deep Social & Contact Scraper | `ai agents` (LeadHunter) | `backend/utils/social_scraper.py` | VERIFIED | `API_INTEGRATION` | Crawls Instagram, Facebook, and founder email contacts. Keep inside LeadHunter service. | HIGH |
| Outbound SMTP / IMAP Sequences | `ai agents` (LeadHunter) | `backend/celery_worker.py`, `imap_reader` | VERIFIED | `API_INTEGRATION` | Automated reply detection. Ensure sending strictly requires explicit human trigger. | HIGH |
| **Module 7: Startup Pain Point Discovery** | | | | | | |
| Community Signal Crawlers | `Startups-problrms-hunter`| `scraper.py` (Reddit, GitHub, HN, RSS) | VERIFIED | `API_INTEGRATION` | Robust crawlers across 7+ platforms with search fallback (DDG ➔ Yahoo). Keep as satellite service. | HIGH |
| Gemini Pain-Point Classifier | `Startups-problrms-hunter`| `ai_agent.py` | VERIFIED | `API_INTEGRATION` | Uses Gemini 2.0 Flash to extract startup issues and draft customized pitch ideas. | HIGH |
| File-based JSON Persistence | `Startups-problrms-hunter`| `data/leads.json` | BROKEN | `REWRITE` | Flat-file storage lacks concurrency safety. Rewrite persistence to PostgreSQL `startup_intel`. | HIGH |
| Direct SMTP Handshake Verifier | `Startups-problrms-hunter`| `email_verifier.py` | BROKEN | `DROP` | Direct SMTP RCPT handshakes risk IP blocklisting. Replace with passive MX validation or API. | HIGH |
| **Module 8: Market & Skill Intelligence** | | | | | | |
| Compensation & Salary Band Calc | `agentic-career-search` | `services/salary_band.py`, `col_adjusted` | VERIFIED | `REUSE` | Title and location based salary estimations with cost-of-living index multipliers. | HIGH |
| Equity & RSU Cliff Analysis | `agentic-career-search` | `services/rsu_refresh_cliff.py`, `equity` | VERIFIED | `REUSE` | Models 4-year vesting schedules, cliffs, and supplemental withholding tax implications. | HIGH |
| Benefit Gap Calculators | `agentic-career-search` | 80+ specialized gap services | VERIFIED | `REUSE` | Evaluates signing bonus clawbacks, severance Cobra top-ups, tuition assistance, and 401k matches. | HIGH |
| **Module 9: Interview Intelligence** | | | | | | |
| STAR Story Planner | `agentic-career-search` | `services/star_story.py` | VERIFIED | `REUSE` | Formulates structured Situation-Task-Action-Result narratives mapped to job criteria. | HIGH |
| Technical Interview Prep Briefs | `agentic-career-search` | `services/interview_prep.py` | VERIFIED | `REUSE` | Synthesizes likely behavioral and technical questions based on JD keyword gaps. | HIGH |
| Interview Schedule Conflict Guard| `agentic-career-search` | `services/interview_schedule_conflict.py` | VERIFIED | `REUSE` | Offline calendar interval overlap detector preventing double-booking during interviews. | HIGH |
| Post-Interview Debrief Synthesizer| `agentic-career-search` | `services/interview_feedback.py` | VERIFIED | `REUSE` | Analyzes candidate self-assessments to identify performance gaps and follow-up points. | HIGH |

