# RIGHT FIT Documentation Library

Welcome to the central documentation index for **RIGHT FIT — AI-Powered Career Intelligence Platform**.

All technical specifications, engineering governance, architecture decisions, and operational runbooks are cataloged here.

---

## 1. Architecture Specifications (`docs/architecture/`)
Comprehensive system blueprints, boundary specifications, data models, and Mermaid diagrams.
* [System Architecture Overview](./architecture/overview.md) — High-level architecture, Option A Hybrid design, and topology.
* [Service Ownership Mapping](./architecture/service-ownership.md) — Detailed mapping of product capabilities to owning services.
* [Data Ownership & Schema Isolation](./architecture/data-ownership.md) — PostgreSQL schema boundaries (`core`, `leadhunter`, `startup_intel`).
* [API & Inter-Service Communication](./architecture/api-communication.md) — REST protocols, authentication headers, timeouts, and error envelopes.
* [Architecture Diagrams](./architecture/diagrams/)
  * [High-Level Architecture Diagram](./architecture/diagrams/high-level-architecture.md)
  * [Service Ownership Diagram](./architecture/diagrams/service-ownership-diagram.md)
  * [Data Ownership Diagram](./architecture/diagrams/data-ownership-diagram.md)
  * [Request Flow Diagram](./architecture/diagrams/request-flow-diagram.md)

---

## 2. Engineering & Governance Standards (`docs/standards/`)
Universal engineering policies mandatory for human engineers and AI coding assistants.
* [Development Workflow](./standards/development.md) — 11-step development lifecycle, branching, and Definition of Done.
* [Universal Naming Conventions](./standards/naming-conventions.md) — Python, TypeScript, Database, and API naming rules.
* [REST API Standards](./standards/api-standards.md) — Endpoint URI structure, HTTP status codes, envelope schemas, and pagination.
* [Database Standards](./standards/database-standards.md) — PostgreSQL standards, UTC timestamps, migration rules, and indexing.
* [Security & Privacy Standards](./standards/security-standards.md) — Secrets management, JWT, resume PII protection, and outreach safeguards.
* [Documentation Standards](./standards/documentation-standards.md) — Documentation-as-code synchronization rules and metadata headers.

---

## 3. Feature Documentation (`docs/features/`)
Feature-level specifications, user journeys, API contracts, and acceptance criteria.
* [Feature Catalog Overview](./features/README.md) — Master index of planned and active features.
* [Feature Specification Template (`_template.md`)](./features/_template.md) — Mandatory 18-point template for feature documentation.

---

## 4. Architecture Decision Records (`docs/adr/`)
Authoritative records of major architectural choices and trade-offs.
* [ADR Registry Index](./adr/README.md) — Status and summary of all Architecture Decision Records.
* [ADR-0001: Hybrid Modular Architecture](./adr/0001-hybrid-architecture.md) — Decision to adopt Option A Hybrid Architecture.
* [ADR-0002: Service & Data Ownership Boundaries](./adr/0002-service-data-ownership.md) — Decision on database schema and queue ownership.

---

## 5. Technical Audits (`docs/audit/`)
Forensic audits of existing legacy source systems and prototypes.
* [Phase 0 Audit Archive](./audit/phase-0/)
  * [01 — Executive Summary](./audit/phase-0/01%20—%20PHASE_0_EXECUTIVE_SUMMARY.md)
  * [02 — Legacy Repository Audit](./audit/phase-0/02%20—%20LEGACY_REPOSITORY_AUDIT.md)
  * [03 — Feature Reuse Matrix](./audit/phase-0/03%20—%20FEATURE_REUSE_MATRIX.md)
  * [04 — API & Dependency Inventory](./audit/phase-0/04%20—%20API_AND_DEPENDENCY_INVENTORY.md)
  * [05 — Test Execution Report](./audit/phase-0/05%20—%20TEST_EXECUTION_REPORT.md)
  * [06 — Security & Privacy Audit](./audit/phase-0/06%20—%20SECURITY_AND_PRIVACY_AUDIT.md)
  * [07 — Architecture Compatibility](./audit/phase-0/07%20—%20ARCHITECTURE_COMPATIBILITY.md)
  * [08 — Technical Risk Register](./audit/phase-0/08%20—%20RISK_REGISTER.md)
  * [09 — Dependency & Blocker Matrix](./audit/phase-0/09%20—%20DEPENDENCY_AND_BLOCKER_MATRIX.md)
  * [10 — Open Decisions Log](./audit/phase-0/10%20—%20OPEN_DECISIONS.md)

---

## 6. Operations & Execution Records (`docs/operations/`)
Phase execution records, deployment runbooks, and disaster recovery procedures.
* [Operations Directory Index](./operations/README.md)
* [Phase 1 Execution Record](./operations/phase-1-execution-record.md)

---

## 7. Open Decisions Log (`docs/decisions/`)
* [Open Decisions Registry](./decisions/README.md)

