# Architecture Decision Registry (Summary)

- **Title:** Architecture Decisions Summary
- **Purpose:** Catalogs key architectural trade-offs, rationale, and links to detailed Architecture Decision Records (ADRs).
- **Status:** ACTIVE
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Summary of Adopted Architecture Decisions

### ADR-001: Hybrid Modular Architecture
- **Decision:** Adopt a hybrid modular architecture with a centralized Core Career API and independent satellite opportunity services.
- **Rationale:** Avoids the operational overhead of a pure microservices mesh while preserving the autonomy of existing, working scrapers.
- **Reference:** [`docs/decisions/ADR-001-hybrid-architecture.md`](../decisions/ADR-001-hybrid-architecture.md)

### ADR-002: Service Database Ownership & Schema Isolation
- **Decision:** Each service owns its database tables. A single PostgreSQL instance uses isolated schemas (`core`, `leadhunter`, `startup_intel`).
- **Rationale:** Prevents table locking contention, enables service-specific migrations, and simplifies future database extraction.
- **Reference:** [`docs/decisions/ADR-002-service-database-ownership.md`](../decisions/ADR-002-service-database-ownership.md)

### ADR-003: API-First Integration & Contract Boundaries
- **Decision:** All inter-service data exchange is mediated via versioned REST APIs and Pydantic JSON contracts.
- **Rationale:** Decouples internal data representations from transport payloads and eliminates distributed database joins.
- **Reference:** [`docs/decisions/ADR-003-api-first-integration.md`](../decisions/ADR-003-api-first-integration.md)

## 2. Decision Review Cadence
ADRs are reviewed quarterly or whenever a major dependency change, breaking schema modification, or infrastructure migration is proposed.

## 3. Open Questions & TBDs
- [TBD] Formal ADR for Vector Database selection (`pgvector` in PostgreSQL vs. dedicated Qdrant/Pinecone).

