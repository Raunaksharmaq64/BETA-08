# Development Workflow & Performance Conditions

- **Title:** Engineering Lifecycle & Performance Guidelines
- **Purpose:** Mandates feature engineering workflow, branch lifecycles, and performance requirements.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Feature Lifecycle Standards
All developers and AI assistants must follow this disciplined 11-step process:

1. **Requirement Understanding:** Clarify user story, inputs, outputs, and edge cases.
2. **Existing Functionality Search:** Check `docs/` and existing modules before writing code.
3. **Module Ownership Identification:** Map functionality to the correct service/module.
4. **Reuse Assessment:** Classify components under `REUSE`, `API_INTEGRATION`, `REWRITE`, or `DROP`.
5. **Architecture & Contract Planning:** Define schemas in `contracts/` first.
6. **Database Impact Analysis:** Check schema changes and Alembic migrations.
7. **Implementation Planning:** Implement logic cleanly with strict type annotations.
8. **Automated Testing:** Write unit, integration, and contract test cases.
9. **Documentation Updates:** Update docs in the same PR.
10. **Code Review:** Review against AGENTS.md quality checklist.
11. **Approval & Merge:** Merge into main branch after all CI quality checks pass.

## 2. Mandatory Performance Guidelines
- **Asynchronous Processing:** Heavy scraping, batch parsing, and AI summarization must run in Celery background workers.
- **Pagination Everywhere:** All list endpoints must support `limit` and `offset` (or cursor-based pagination). Never return unbounded collections.
- **Connection Pooling:** Use connection pooling for PostgreSQL (e.g., `pool_size=10`, `max_overflow=20`).
- **Idempotency:** Background tasks and retryable workers must be idempotent.
- **Frontend Optimization:** Leverage React Server Components (RSC) to minimize client-side JavaScript bundle sizes.

## 3. Open Questions & TBDs
- [TBD] Establish benchmark thresholds for automated regression testing.

