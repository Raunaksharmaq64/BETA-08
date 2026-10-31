# Market & Compensation Intelligence Engine
**Phase 12 Implementation Catalog**

## Overview
Phase 12 delivers an empirical, transparent Market & Compensation Intelligence engine for the RIGHT FIT Career Intelligence Platform. It provides:
1. **Canonical Skill Taxonomy & Deterministic Alias Resolution**: Standardized skill nodes mapped to synonyms and colloquial abbreviations without false merges (e.g. `js` -> `JavaScript`, `postgres` -> `PostgreSQL`, `k8s` -> `Kubernetes`).
2. **Distinct Opportunity Demand Aggregation**: Time-windowed demand tracking across `7d`, `30d`, and `90d` intervals, strictly counting unique vacancies (never multiplying keyword repetitions within a single posting).
3. **Audited Compensation Explorer**: Isolated compensation benchmarks strictly separating Base Salary, Total Compensation, Equity, and Contract/Hourly rates while preserving native currencies (USD, EUR, GBP, INR).
4. **Sample Disclosures & Statistical Boundary Invariants**: Complete prevention of false precision; median calculations are mathematically suppressed when sample size $N < 5$, alongside explicit disclosure of non-disclosure rates.
5. **Candidate Skill-Gap Diagnostics**: Profile-grounded diagnostic engine comparing verified candidate resume skills with live market demand, providing interactive status tracking (`INTERESTED`, `ALREADY_LEARNING`, `NOT_RELEVANT`, `COMPLETED`) without mutating candidate profiles.
6. **Audited Source Registry & Methodology Transparency**: Public registry of data sources, ingestion frequencies, and statistical governance rules.

---

## Document Index
1. [`architecture.md`](./architecture.md) — Architectural overview, data model topology, and service boundaries.
2. [`source-registry.md`](./source-registry.md) — Audited market sources, reliability scoring, and provenance tracking.
3. [`skill-taxonomy-methodology.md`](./skill-taxonomy-methodology.md) — Skill node modeling, categorization, and hierarchy.
4. [`alias-resolution-engine.md`](./alias-resolution-engine.md) — Synonym resolution, normalization pipeline, and collision protection.
5. [`demand-aggregation-rules.md`](./demand-aggregation-rules.md) — Time-window aggregation, distinct vacancy counting, and frequency math.
6. [`trend-analysis-methodology.md`](./trend-analysis-methodology.md) — Period-over-period direction computation and sample thresholds.
7. [`compensation-methodology.md`](./compensation-methodology.md) — Empirical salary modeling, pay structure isolation, and percentiles.
8. [`currency-and-units-handling.md`](./currency-and-units-handling.md) — Native currency preservation and pay frequency normalization.
9. [`confidence-and-disclosure.md`](./confidence-and-disclosure.md) — Minimum sample rule ($N \ge 5$), false-precision guards, and unstated salary metrics.
10. [`candidate-skill-gap-engine.md`](./candidate-skill-gap-engine.md) — Comparative gap analysis against verified candidate skills.
11. [`candidate-privacy-and-evidence.md`](./candidate-privacy-and-evidence.md) — Non-mutation invariants and privacy boundaries.
12. [`frontend-market-dashboard.md`](./frontend-market-dashboard.md) — Next.js market demand dashboard and skill profile views.
13. [`frontend-compensation-explorer.md`](./frontend-compensation-explorer.md) — Next.js compensation explorer and pay breakdown interface.
14. [`api-contracts.md`](./api-contracts.md) — Complete OpenAPI v1 endpoint specifications and payload schemas.
15. [`operational-playbook.md`](./operational-playbook.md) — Ingestion runbooks, snapshot lifecycle, and operational monitoring.

