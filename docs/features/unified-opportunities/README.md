# Unified Opportunities Engine and Candidate Dashboard
**Phase 11 Implementation Catalog**

## Overview
Phase 11 establishes the centralized, unified aggregation layer and candidate intelligence dashboard for RIGHT FIT. It harmonizes heterogeneous career opportunities across:
1. **Core Career Engine Canonical Jobs** (`canonical_opportunities` table)
2. **LeadHunter AI Freelance Opportunities** (`freelance_opportunities` table)
3. **Startup Intelligence Pain Points** (`startup_opportunities` table)

This unification respects our core architectural boundaries:
- **Core Career Engine** owns aggregation, dashboard metrics reconciliation, polymorphic saved bookmarks, and candidate feedback.
- **LeadHunter AI** and **Startups-problems-hunter** satellites remain completely autonomous independent services with independent lifecycles, databases, and operational runtimes.
- **Strict Evidence Preservation**: Aggregation normalizes display fields into the common `OpportunityEnvelope` v1.0 without synthesizing artificial trust scores or altering underlying source corroboration.

---

## Document Index
1. [`architecture.md`](./architecture.md) — Hybrid aggregation architecture and boundaries.
2. [`canonical-schema.md`](./canonical-schema.md) — Opportunity envelope v1.0 schema specification.
3. [`aggregation-engine.md`](./aggregation-engine.md) — Cross-source querying, sorting, and pagination engine.
4. [`query-and-filtering.md`](./query-and-filtering.md) — Multi-source filtering mechanics and discriminator mappings.
5. [`dashboard-metrics.md`](./dashboard-metrics.md) — Summary metrics reconciliation principles and counts formulas.
6. [`service-resilience.md`](./service-resilience.md) — Partial degradation fallbacks and circuit breaker resilience.
7. [`saved-items-polymorphism.md`](./saved-items-polymorphism.md) — Polymorphic candidate bookmarking across heterogeneous entities.
8. [`relevance-feedback.md`](./relevance-feedback.md) — Candidate feedback loop mechanics and preference tuning.
9. [`candidate-isolation.md`](./candidate-isolation.md) — Absolute isolation between candidate personal actions and global records.
10. [`frontend-dashboard.md`](./frontend-dashboard.md) — Next.js `/dashboard` UI design and metric reconciliation displays.
11. [`frontend-opportunities.md`](./frontend-opportunities.md) — Unified `/opportunities` pipeline feed and interactive filters.
12. [`frontend-saved.md`](./frontend-saved.md) — `/saved-opportunities` polymorphic bookmark management screen.
13. [`api-contracts.md`](./api-contracts.md) — Complete OpenAPI v1 REST contracts and response schemas.
14. [`reconciliation-matrix.md`](./reconciliation-matrix.md) — Verification matrix ensuring zero discrepancy across counts.
15. [`operational-playbook.md`](./operational-playbook.md) — Runbooks, monitoring alerts, and incident recovery procedures.

