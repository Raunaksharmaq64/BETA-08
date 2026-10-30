# ADR-005: Startup Intelligence Persistence Modernization

- **Document ID:** ADR-005
- **Title:** Modernizing Startup Intelligence Persistence from Flat-File JSON to PostgreSQL
- **Status:** RECOMMENDATION (REQUIRING APPROVAL)
- **Author:** Principal Software Architect & Database Architect
- **Date:** 2026-10-30

---

## 1. Context & Problem Statement
During the Phase 0 audit of `Startups-problrms-hunter`, it was discovered that:
1. All scraped posts, detected pain points, and AI-generated pitches are persisted synchronously to a single flat JSON file: `Startups-problrms-hunter/data/leads.json`.
2. Whenever a new signal is found or updated, the entire JSON array is serialized and rewritten to disk via `json.dump()`.
3. This creates a severe technical risk:
   - **Concurrency Failure:** If two background scrapers or web requests attempt to write simultaneously, the file will be truncated or corrupted.
   - **Zero Indexing:** Filtering by tech stack, date, or category requires loading the entire file into memory and performing $O(N)$ linear scans.
   - **Zero Relational Integrity:** Evidence, raw URLs, and AI pitch drafts cannot be joined or foreign-keyed.

RIGHT FIT target architecture (Option A) mandates PostgreSQL as the single relational database engine, partitioned via isolated schemas.

---

## 2. Decision Options Considered

### Option 1: Maintain File-Based JSON Storage
- *Pros:* Simple, zero database setup for standalone prototype.
- *Cons:* Prone to catastrophic race conditions, unscalable beyond a few hundred records, unacceptable for production.

### Option 2: Introduce a Document Database (MongoDB)
- *Pros:* Native JSON document storage.
- *Cons:* Introduces an additional database technology into the stack, increasing operational and DevOps complexity.

### Option 3 (Recommended): Migrate to PostgreSQL Isolated Schema (`startup_intel`)
- *Pros:*
  - Fully transactional (ACID compliant) with concurrency locking.
  - Leverages PostgreSQL's native `JSONB` for raw signal payloads and unstructured evidence.
  - Aligns with the overall RIGHT FIT infrastructure without introducing new database engines.
- *Cons:* Requires authoring initial SQLAlchemy models and Alembic migration scripts.

---

## 3. Decision & Architectural Consequences
**We recommend Option 3:**
1. In Phase 1.5, introduce SQLAlchemy models for Startup Intelligence:
   - `startup_intel.startups`
   - `startup_intel.pain_points`
   - `startup_intel.evidence`
2. Implement a one-time data migration script to ingest existing records from `data/leads.json` into the `startup_intel` database tables.
3. Decouple `services/startup_intelligence` from local file paths, allowing stateless containerization.

---

## 4. Approval Status
- **Status:** PENDING ARCHITECTURAL APPROVAL

