# Compatibility & Dependency Analysis

- **Title:** Technical Compatibility Analysis Across Source Systems
- **Purpose:** Identifies version conflicts, framework differences, and modernization requirements.
- **Status:** APPROVED
- **Owner:** Principal Architect / Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Language & Framework Alignment
- **Python Runtime:**
  - `agentic-career-search`: Python 3.11+.
  - `ai agents`: Python 3.11+.
  - `Startups-problrms-hunter`: Python 3.11+.
  - *Outcome:* Full runtime parity. Unified baseline set to **Python 3.11+**.
- **Web Frameworks:**
  - All three prototypes utilize FastAPI for backend API endpoints.
  - *Outcome:* Clean alignment. Core and satellite services use standardized FastAPI patterns.

## 2. ORM & Database Layer Discrepancies
- `agentic-career-search`: SQLAlchemy 2.0 + Alembic.
- `ai agents`: SQLModel (SQLAlchemy wrapper) + asyncpg.
- `Startups-problrms-hunter`: Native JSON file storage (`data/leads.json`).
- *Modernization Plan:* Core Career Engine uses **SQLAlchemy 2.x + Alembic**. LeadHunter preserves internal SQLModel asynchronously. Startup Intelligence replaces JSON files with PostgreSQL `startup_intel` schema in Phase 1.

## 3. Pydantic Compatibility
- Prototype libraries mix Pydantic v1 (`@validator`) and v2 (`@field_validator`).
- *Resolution:* RIGHT FIT Core strictly enforces **Pydantic v2**. Legacy models are modernized during porting.

## 4. Open Questions & TBDs
- [TBD] Testing Alembic multi-database vs. single database schema migration management.

