# Legacy Repositories Technical Audit

- **Title:** Comprehensive Audit of Existing Source Systems
- **Purpose:** Rigorous architectural, technical, and readiness assessment of the three legacy prototypes.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. System A: `agentic-career-search`
- **Location:** `../agentic-career-search`
- **Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, Alembic, Pydantic, Pytest.
- **Key Assets:**
  - 50+ ATS and job board source adapters (`src/autoapply_agent/adapters/`).
  - Deterministic fit scoring engine with rationale traces (`services/scoring.py`, `services/skills_fit.py`).
  - Deep compensation & benefit calculators (RSU cliffs, signing bonus clawbacks, salary bands).
  - CRM state machine for application stages (`services/application_stage.py`).
- **Technical Health:** High code quality, modular architecture, extensive test suite, ready for modular reuse in Core Backend.

## 2. System B: `ai agents` (LeadHunter AI)
- **Location:** `../ai agents`
- **Tech Stack:** FastAPI, Next.js 16, PostgreSQL (SQLModel Async), Celery, Redis.
- **Key Assets:**
  - Local business Google Maps scraper (SerpApi & Apify routing).
  - Website availability, DNS, SSL, and performance auditor.
  - Deep social and contact crawler (Instagram, Facebook, LinkedIn, email).
  - Automated SMTP outreach and IMAP reply tracking.
- **Technical Health:** Solid full-stack architecture; best maintained as an independent satellite service wrapped behind clean REST endpoints.

## 3. System C: `Startups-problrms-hunter`
- **Location:** `../Startups-problrms-hunter`
- **Tech Stack:** Python, FastAPI, Vanilla JS, Gemini API, JSON file persistence.
- **Key Assets:**
  - Multi-source scraper (Reddit, GitHub "help wanted", Hacker News, Product Hunt).
  - Resilient search fallback (DuckDuckGo ➔ Yahoo Search).
  - Tech stack detection and startup pain-point classification.
- **Technical Health:** Lightweight script-based setup with file-based persistence (`data/leads.json`). Suitable for standalone containerization, with future migration to PostgreSQL.

## 4. Open Questions & TBDs
- [TBD] Final timeline for Phase 0 formal sign-off.

