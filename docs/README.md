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
* [Production Infrastructure & Disaster Recovery](./features/production-infrastructure/README.md) — Phase 13 Cloud Infrastructure, AWS Option B Topology, Terraform IaC, Non-Root Containerization & Disaster Recovery.
  * [Architecture & Boundaries](./features/production-infrastructure/architecture.md)
  * [AWS Topology ADR Summary](./features/production-infrastructure/aws-topology-adr.md)
  * [Network & Security Architecture](./features/production-infrastructure/network-and-security.md)
  * [Containerization Guide](./features/production-infrastructure/containerization-guide.md)
  * [Secrets & Environment Configuration](./features/production-infrastructure/secrets-and-environment.md)
  * [Database & RDS Management](./features/production-infrastructure/database-and-rds.md)
  * [Redis & Celery Processing](./features/production-infrastructure/redis-and-celery.md)
  * [S3 Storage & Lifecycle](./features/production-infrastructure/s3-storage-and-lifecycle.md)
  * [TLS, Domain & Nginx Ingress](./features/production-infrastructure/tls-and-nginx.md)
  * [Monitoring, Logs & Alerts](./features/production-infrastructure/monitoring-and-alerting.md)
  * [Backup & Restore Runbook](./features/production-infrastructure/backup-and-restore-runbook.md)
  * [Disaster Recovery Runbook](./features/production-infrastructure/disaster-recovery-runbook.md)
  * [Deployment Runbook](./features/production-infrastructure/deployment-runbook.md)
  * [Rollback Runbook](./features/production-infrastructure/rollback-runbook.md)
  * [Incident Response Guide](./features/production-infrastructure/incident-response-guide.md)
  * [Monthly AWS Cost Estimation](./features/production-infrastructure/cost-estimation.md)
  * [Production Release Checklist](./features/production-infrastructure/production-release-checklist.md)
* [Market & Compensation Intelligence Engine](./features/market-intelligence/README.md) — Phase 12 Skill Taxonomy, Deterministic Aliases, Distinct Vacancy Demand, Audited Compensation Explorer & Candidate Skill-Gap Diagnostics.
  * [Architecture & Boundaries](./features/market-intelligence/architecture.md)
  * [Audited Source Registry](./features/market-intelligence/source-registry.md)
  * [Skill Taxonomy Methodology](./features/market-intelligence/skill-taxonomy-methodology.md)
  * [Alias Resolution Engine](./features/market-intelligence/alias-resolution-engine.md)
  * [Demand Aggregation Rules](./features/market-intelligence/demand-aggregation-rules.md)
  * [Trend Analysis Methodology](./features/market-intelligence/trend-analysis-methodology.md)
  * [Compensation Methodology](./features/market-intelligence/compensation-methodology.md)
  * [Currency & Units Handling](./features/market-intelligence/currency-and-units-handling.md)
  * [Confidence Boundaries & Sample Disclosures](./features/market-intelligence/confidence-and-disclosure.md)
  * [Candidate Skill-Gap Engine](./features/market-intelligence/candidate-skill-gap-engine.md)
  * [Candidate Privacy & Evidence](./features/market-intelligence/candidate-privacy-and-evidence.md)
  * [Frontend Market Dashboard](./features/market-intelligence/frontend-market-dashboard.md)
  * [Frontend Compensation Explorer](./features/market-intelligence/frontend-compensation-explorer.md)
  * [API Contracts & Endpoints](./features/market-intelligence/api-contracts.md)
  * [Operational Playbook & Runbooks](./features/market-intelligence/operational-playbook.md)
* [Unified Opportunities Engine & Dashboard](./features/unified-opportunities/README.md) — Phase 11 Unified Opportunities Aggregation, Common Envelope v1.0, Polymorphic Bookmarks & Candidate Intelligence Dashboard.
  * [Aggregation Architecture & Boundaries](./features/unified-opportunities/architecture.md)
  * [Common Opportunity Envelope v1.0 Schema](./features/unified-opportunities/canonical-schema.md)
  * [Unified Aggregation Engine](./features/unified-opportunities/aggregation-engine.md)
  * [Multi-Source Query & Filtering](./features/unified-opportunities/query-and-filtering.md)
  * [Dashboard Summary Metrics](./features/unified-opportunities/dashboard-metrics.md)
  * [Service Failure Resilience](./features/unified-opportunities/service-resilience.md)
  * [Polymorphic Saved Bookmarks](./features/unified-opportunities/saved-items-polymorphism.md)
  * [Candidate Relevance Feedback](./features/unified-opportunities/relevance-feedback.md)
  * [Candidate Isolation & Privacy](./features/unified-opportunities/candidate-isolation.md)
  * [Frontend Dashboard Specification](./features/unified-opportunities/frontend-dashboard.md)
  * [Frontend Opportunities Specification](./features/unified-opportunities/frontend-opportunities.md)
  * [Frontend Saved Opportunities Specification](./features/unified-opportunities/frontend-saved.md)
  * [API Contracts & Endpoints](./features/unified-opportunities/api-contracts.md)
  * [Metrics Reconciliation Matrix](./features/unified-opportunities/reconciliation-matrix.md)
  * [Operational Playbook & Runbooks](./features/unified-opportunities/operational-playbook.md)
* [Startup Intelligence & Pain Point Explorer](./features/startup-intelligence/README.md) — Phase 10 Satellite Startup Intelligence Integration, Bottleneck Discovery, Technographics & Pitch Drafts.
  * [Source-by-Source Audit](./features/startup-intelligence/source-by-source-audit.md)
  * [Versioned REST API Contract](./features/startup-intelligence/versioned-api-contract.md)
  * [Core Adapter Architecture & Circuit Breaker](./features/startup-intelligence/core-adapter-architecture.md)
  * [Startup Problem Mapping](./features/startup-intelligence/startup-problem-mapping.md)
  * [Evidence Provenance & Timestamps](./features/startup-intelligence/evidence-provenance-and-timestamps.md)
  * [Observation vs AI Summary Policy](./features/startup-intelligence/observation-vs-ai-summary-policy.md)
  * [Deduplication & Corroboration Engine](./features/startup-intelligence/deduplication-and-corroboration.md)
  * [Technographic Stack Findings](./features/startup-intelligence/technology-findings-specification.md)
  * [Pitch Drafts & Assumptions Policy](./features/startup-intelligence/pitch-drafts-and-assumptions.md)
  * [JSON-to-PostgreSQL Migration Assessment](./features/startup-intelligence/json-to-postgresql-migration-assessment.md)
  * [Migration Dry-Run Report](./features/startup-intelligence/migration-dry-run-report.md)
  * [Independent Deployment Guide](./features/startup-intelligence/independent-deployment-guide.md)
  * [Downtime & Recovery Runbook](./features/startup-intelligence/downtime-and-recovery-runbook.md)
  * [Startup Frontend User Guide](./features/startup-intelligence/startup-frontend-guide.md)
  * [Security & Privacy Review](./features/startup-intelligence/security-and-privacy-review.md)
* [LeadHunter Integration & Freelance Discovery](./features/leadhunter-integration/README.md) — Phase 9 Satellite LeadHunter AI Integration, Freelance Opportunities & Governed Outreach.
  * [LeadHunter API Audit & Inventory](./features/leadhunter-integration/leadhunter-api-audit.md)
  * [Versioned REST API Contract](./features/leadhunter-integration/versioned-api-contract.md)
  * [Core Adapter Architecture & Circuit Breaker](./features/leadhunter-integration/core-adapter-architecture.md)
  * [Multi-Signal Lead Mapping](./features/leadhunter-integration/lead-to-freelance-mapping.md)
  * [Contact Evidence & Source Provenance](./features/leadhunter-integration/contact-evidence-and-provenance.md)
  * [Import & Tiered Deduplication](./features/leadhunter-integration/import-and-deduplication.md)
  * [Candidate-Governed Outreach Workflow](./features/leadhunter-integration/outreach-approval-workflow.md)
  * [Provider Delivery & Evidence Ledger](./features/leadhunter-integration/provider-delivery-evidence.md)
  * [Suppression List & Sending Quotas](./features/leadhunter-integration/suppression-and-rate-limits.md)
  * [Independent Deployment & Configuration](./features/leadhunter-integration/independent-deployment-guide.md)
  * [Recovery & Troubleshooting Runbook](./features/leadhunter-integration/recovery-and-troubleshooting.md)
  * [Freelance Frontend User Guide](./features/leadhunter-integration/freelance-frontend-guide.md)
  * [Security & Privacy Review](./features/leadhunter-integration/security-and-privacy-review.md)
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
* [Phase 9 Execution Record](./audit/phase-9/phase-9-execution-record.md) — LeadHunter Integration, Freelance Opportunities & Governed Outreach.
* [Phase 10 Execution Record](./audit/phase-10/phase-10-execution-record.md) — Startup Intelligence Integration, Bottleneck Discovery & Governed Pitch Drafts.
* [Phase 11 Execution Record](./audit/phase-11/phase-11-execution-record.md) — Unified Opportunities Engine and Dashboard, Aggregation & Polymorphic Bookmarks.
* [Phase 12 Execution Record](./audit/phase-12/phase-12-execution-record.md) — Market & Compensation Intelligence Engine, Taxonomy, Audited Salary & Skill Gaps.
* [Phase 13 Execution Record](./audit/phase-13/phase-13-execution-record.md) — Production Cloud Infrastructure, AWS Option B Topology, Non-Root Containers & Disaster Recovery.

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

