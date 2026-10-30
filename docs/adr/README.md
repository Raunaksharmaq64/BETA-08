# Architecture Decision Records (ADRs)

- **Purpose:** Historical log of significant architectural choices, trade-offs, and governance policies for RIGHT FIT.
- **Status:** ACTIVE
- **Owner:** Principal Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## ADR Index

| ADR ID | Title | Status | Date | Primary Focus |
| :--- | :--- | :--- | :--- | :--- |
| **[ADR-0001](./0001-hybrid-architecture.md)** | **Option A — Hybrid Modular Architecture** | **ACCEPTED** | 2026-10-31 | Core Backend + Independent Satellites + Unified Frontend |
| **[ADR-0002](./0002-service-data-ownership.md)** | **Service & Database Schema Ownership** | **ACCEPTED** | 2026-10-31 | Schema boundaries (`career_core`, `leadhunter_db`, `startup_intel_db`) |
| **[ADR-0004](../audit/phase-0/adrs/ADR-004-career-engine-auth-strategy.md)** | **Career Engine Authentication Strategy** | **RECOMMENDATION** | 2026-10-30 | Ingesting LeadHunter JWT auth engine into Core |
| **[ADR-0005](../audit/phase-0/adrs/ADR-005-startup-intel-storage-evolution.md)** | **Startup Intel Storage Modernization** | **RECOMMENDATION** | 2026-10-30 | Migrating flat-file `leads.json` to PostgreSQL schema |

---

## ADR Lifecycle
1. **Proposed:** Documented and under team review.
2. **Accepted:** Formally approved by Principal Architect / Project Owner.
3. **Rejected:** Evaluated but determined unsuitable.
4. **Superseded:** Replaced by a subsequent ADR.

