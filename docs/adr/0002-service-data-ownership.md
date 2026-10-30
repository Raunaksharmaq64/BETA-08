# ADR-0002: Service Boundaries & Database Schema Ownership

- **Document ID:** ADR-0002
- **Title:** Relational Database Schema Ownership & Queue Partitioning
- **Status:** ACCEPTED
- **Author:** Principal Software Architect & Database Architect
- **Date:** 2026-10-31

---

## 1. Context & Problem Statement
In a distributed hybrid architecture, uncontrolled cross-service database coupling is a major anti-pattern. If Service A writes directly to Service B's tables or executes cross-database SQL joins, service boundaries collapse, table lock contention increases, and database migrations become tightly coupled.

RIGHT FIT requires strict data ownership rules that preserve service autonomy while maintaining transactional integrity.

---

## 2. Decision
We establish **strict schema isolation within a single PostgreSQL 16 database instance**, complemented by isolated Redis task queues:

### 1. Database Schema Ownership:
* **`career_core` Schema:** Owned exclusively by Core Career Engine (`backend/app/modules/`). Contains `users`, `profiles`, `skills`, `resumes`, `jobs`, `job_matches`, and `applications`. Managed via Core Alembic migrations.
* **`leadhunter_db` Schema:** Owned exclusively by LeadHunter AI (`services/leadhunter/`). Contains `businesses`, `website_audits`, `leads`, and `outreach_logs`.
* **`startup_intel_db` Schema:** Owned exclusively by Startup Intelligence (`services/startup_intelligence/`). Contains `startups`, `pain_points`, `evidence`, and `pitch_drafts`.

### 2. Boundary Directives:
* **Zero Cross-Schema Direct Access:** No service may execute SQL queries or joins across schema boundaries.
* **REST Data Exchange:** Data exchange between services occurs exclusively over authenticated HTTP REST APIs.
* **No Distributed Foreign Keys:** Tables in different schemas cannot share database-level foreign key constraints. Relationships are linked via logical UUID identifiers.

### 3. Redis Queue Partitioning:
* `career_tasks`: Owned by Core Career Engine worker.
* `lead_tasks`: Owned by LeadHunter worker.
* `startup_tasks`: Owned by Startup Intelligence worker.
* `notification_tasks`: Owned by Core Career Engine worker for transactional dispatch.

---

## 3. Consequences & Implications

### Positive Consequences:
* **Migration Autonomy:** Core Career Engine can migrate its schema without coordinating deployment locks with satellite services.
* **Failure Domain Containment:** A database lock or long-running query in `leadhunter_db` does not block transactional job applications or logins in `career_core`.
* **DevOps Simplicity:** Operates on a single managed PostgreSQL server with schema separation rather than requiring three independent database servers locally.

### Negative / Trade-Off Consequences:
* **No Database Joins:** Aggregating data across services requires application-level stitching in Core Career Engine.
* **Eventual Consistency:** Data between services is eventually consistent rather than immediately consistent across distributed transactions.

