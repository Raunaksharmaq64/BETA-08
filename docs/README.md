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
Comprehensive feature specifications, user journeys, API contracts, and implementation guides.
* [Feature Catalog Overview](./features/README.md) — Master index of planned and active features.
* [Feature Specification Template (`_template.md`)](./features/_template.md) — Mandatory 18-point template for feature documentation.
* [CRM & Interview Intelligence](./features/crm-and-interview-intel/README.md) — Phase 8 Application CRM Pipeline, 48-Hour Sprint, STAR Builder, Mock Rubric & Reminders.
  * [Application State Machine](./features/crm-and-interview-intel/application-state-machine.md)
  * [Save and Apply Tracking](./features/crm-and-interview-intel/save-and-apply-tracking.md)
  * [Status History and Notes](./features/crm-and-interview-intel/status-history-and-notes.md)
  * [CRM Dashboard and Metrics](./features/crm-and-interview-intel/crm-dashboard-and-metrics.md)
  * [Reminders and Timezone](./features/crm-and-interview-intel/reminders-and-timezone.md)
  * [Interview Plans and Rounds](./features/crm-and-interview-intel/interview-plans-and-rounds.md)
  * [48-Hour Preparation Mode](./features/crm-and-interview-intel/48-hour-preparation-mode.md)
  * [STAR Answer Builder](./features/crm-and-interview-intel/star-answer-builder.md)
  * [Mock Interview and Rubric](./features/crm-and-interview-intel/mock-interview-and-rubric.md)
  * [Interview Debrief and Conflicts](./features/crm-and-interview-intel/interview-debrief-and-conflicts.md)
  * [Notifications and Preferences](./features/crm-and-interview-intel/notifications-and-preferences.md)
* [Job Search, Candidate Matching & Personalized Discovery](./features/job-search-and-matching/README.md) — Phase 7 Multi-Dimensional Search, Skill Fit, Mandatory Eligibility & Alerts.
  * [Search Architecture & Execution](./features/job-search-and-matching/search-architecture.md)
  * [Evidence-Based Skill Fit Engine](./features/job-search-and-matching/skill-fit-engine.md)
  * [Mandatory Eligibility Engine](./features/job-search-and-matching/mandatory-eligibility.md)
  * [Explainable Multi-Dimensional Ranking](./features/job-search-and-matching/explainable-ranking.md)
  * [Source Coverage & Partial Results Transparency](./features/job-search-and-matching/source-coverage-transparency.md)
  * [Candidate Saved Jobs & Private Notes](./features/job-search-and-matching/saved-jobs-and-notes.md)
  * [Saved Searches & Alert Subscriptions](./features/job-search-and-matching/saved-searches-and-alerts.md)
  * [Alert Delivery & Idempotency](./features/job-search-and-matching/alert-delivery-and-idempotency.md)
  * [Frontend Discovery & UI Guide](./features/job-search-and-matching/frontend-discovery-guide.md)
  * [Evaluation Dataset & Precision Benchmarks](./features/job-search-and-matching/evaluation-dataset-and-precision.md)
* [Verification, Deduplication & Quality Guide](./features/verification-and-dedup/README.md) — Phase 6 Verification, Deduplication, Freshness & Data Quality.
  * [Verification State Machine](./features/verification-and-dedup/verification-state-machine.md)
  * [Verification Evidence Ledger](./features/verification-and-dedup/verification-evidence.md)
  * [Source-Specific Status Rules](./features/verification-and-dedup/source-specific-status-rules.md)
  * [Freshness Policy & Timestamps](./features/verification-and-dedup/freshness-policy.md)
  * [Tiered Deduplication Engine](./features/verification-and-dedup/deduplication-engine.md)
  * [Source Mappings & Provenance](./features/verification-and-dedup/source-mapping.md)
  * [Merge & Unmerge Audit](./features/verification-and-dedup/merge-unmerge-audit.md)
  * [User Listing Feedback](./features/verification-and-dedup/user-feedback.md)
  * [Data Quality Metrics](./features/verification-and-dedup/quality-metrics.md)
  * [Frontend User Guide](./features/verification-and-dedup/frontend-guide.md)
* [Job Source Framework Guide](./features/job-source-framework/README.md) — Phase 5 Registry, Connectors, Normalization & Provenance.
  * [Source Registry & Administration](./features/job-source-framework/source-registry.md)
  * [Connector Interface & Adapters](./features/job-source-framework/connector-interface.md)
  * [Source Governance Policy Gate](./features/job-source-framework/source-policy.md)
  * [Canonical Normalization](./features/job-source-framework/normalization.md)
  * [Provenance, Freshness & Auditing](./features/job-source-framework/provenance-and-freshness.md)
  * [Ingestion Lifecycle & Resilience](./features/job-source-framework/ingestion-lifecycle.md)
  * [Source Operations Runbook](./features/job-source-framework/source-operations.md)
* [Resume Intelligence Guide](./features/resume-intelligence/README.md) — Phase 4 Resume Intelligence, Evidence Tracking & ATS Analysis.
  * [Upload & Storage](./features/resume-intelligence/upload-and-storage.md)
  * [Parsing Pipeline](./features/resume-intelligence/parsing-pipeline.md)
  * [Extraction & Evidence](./features/resume-intelligence/extraction-and-evidence.md)
  * [Review Workbench](./features/resume-intelligence/review-and-correction.md)
  * [Version Management](./features/resume-intelligence/version-management.md)
  * [ATS Analysis](./features/resume-intelligence/ats-analysis.md)

---

## 4. Architecture Decision Records (`docs/adr/`)
Authoritative records of major architectural choices and trade-offs.
* [ADR Registry Index](./adr/README.md) — Status and summary of all Architecture Decision Records.
* [ADR-0001: Hybrid Modular Architecture](./adr/0001-hybrid-architecture.md) — Decision to adopt Option A Hybrid Architecture.
* [ADR-0002: Service & Data Ownership Boundaries](./adr/0002-service-data-ownership.md) — Decision on database schema and queue ownership.

---

## 5. Technical Audits & Phase Records (`docs/audit/`)
Forensic audits of existing legacy source systems, test reports, and phase execution records.
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
* [Phase 2 Execution Record](./audit/phase-2/phase-2-execution-record.md) — Service contracts, OpenAPI, and schemas.
* [Phase 3 Execution Record](./audit/phase-3/phase-3-execution-record.md) — Identity, candidate profile, and GDPR/CCPA privacy foundation.
* [Phase 4 Execution Record](./audit/phase-4/phase-4-execution-record.md) — Resume Intelligence, reviewed evidence, and ATS analysis.
* [Phase 5 Execution Record](./audit/phase-5/phase-5-execution-record.md) — Job Source Framework, Connectors, Normalization & Provenance.
* [Phase 6 Execution Record](./audit/phase-6/phase-6-execution-record.md) — Verification, Deduplication, Freshness & Quality Intelligence.
* [Phase 7 Execution Record](./audit/phase-7/phase-7-execution-record.md) — Job Search, Candidate Matching & Personalized Discovery.
* [Phase 8 Execution Record](./audit/phase-8/phase-8-execution-record.md) — CRM and Interview Intelligence.

---

## 6. API & Testing References
* [Job Source & Opportunities REST API](./api/source-apis.md) — Specification of `/api/v1/sources` and `/api/v1/opportunities`.
* [Job Source Test Suite & Evidence](./testing/source-framework-tests.md) — Automated verification report and test runner commands.

---

## 6. Operations & Execution Records (`docs/operations/`)
Phase execution records, deployment runbooks, and disaster recovery procedures.
* [Operations Directory Index](./operations/README.md)
* [Phase 1 Execution Record](./operations/phase-1-execution-record.md)

---

## 7. Open Decisions Log (`docs/decisions/`)
* [Open Decisions Registry](./decisions/README.md)

