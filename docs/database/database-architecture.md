# Database Architecture Specification

- **Title:** RIGHT FIT Relational Database Architecture
- **Purpose:** Outlines PostgreSQL schema topology, connection pooling, and multi-tenant partitioning.
- **Status:** APPROVED
- **Owner:** Database Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Relational Engine Standards
- **Database System:** PostgreSQL 16+.
- **Extensions:**
  - `uuid-ossp`: For generating UUIDv4 primary keys.
  - `pgcrypto`: For cryptographic routines.
  - `pgvector`: For storing skill and job description semantic embeddings.
- **ORM / Query Layer:** SQLAlchemy 2.x with `asyncpg` async driver.

## 2. Schema Partitioning Model
Rather than running multiple database servers locally, RIGHT FIT uses schema-level isolation within a single PostgreSQL database:
```sql
-- Schema for Core Career Engine
CREATE SCHEMA IF NOT EXISTS core;

-- Schema for LeadHunter (Freelance Leads)
CREATE SCHEMA IF NOT EXISTS leadhunter;

-- Schema for Startup Intelligence
CREATE SCHEMA IF NOT EXISTS startup_intel;
```

## 3. Connection Pooling
- **Local Dev:** `NullPool` or small `AsyncAdaptedQueuePool` (`pool_size=5`).
- **Production:** Async pool (`pool_size=20`, `max_overflow=10`, `pool_timeout=30s`, `pool_recycle=1800s`).

## 4. Open Questions & TBDs
- [TBD] Dedicated read-replica endpoint configuration in `core/database.py`.

