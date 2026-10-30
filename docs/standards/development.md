# Engineering Development Standards

- **Title:** Universal Development Standards & Engineering Lifecycle
- **Purpose:** Establishes workflow policies, branching discipline, commit hygiene, testing gates, and the Definition of Done.
- **Status:** APPROVED
- **Owner:** Principal Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## 1. Development Lifecycle (11-Step Process)
Every feature, endpoint, or adapter must follow this 11-step lifecycle:
1. **Requirement Understanding:** Review the relevant PRD and active phase exit criteria.
2. **Existing Functionality Search:** Check `docs/` and existing modules before writing new code.
3. **Module Ownership Identification:** Map functionality to the correct service/module.
4. **Reuse Assessment:** Classify components under `REUSE`, `API_INTEGRATION`, `REWRITE`, or `DROP`.
5. **Architecture & Contract Planning:** Define schemas in `contracts/` first.
6. **Database Impact Analysis:** Check schema changes and Alembic migrations.
7. **Implementation Planning:** Implement logic cleanly with strict type annotations.
8. **Automated Testing:** Write unit, integration, and contract test cases. Record actual test results.
9. **Documentation Updates in Same PR:** Synchronize documentation with every code change.
10. **Peer / Architectural Review:** Review against the AGENTS.md quality checklist.
11. **Approval & Merge:** Merge into main branch only after all CI quality checks pass.

---

## 2. Branching & Commit Discipline
* **Branch Strategy:** Work on short-lived branches off `main` (`feature/*`, `fix/*`, `refactor/*`, `docs/*`, `test/*`, `chore/*`).
* **Focused Commits:** Each commit must encapsulate a single logical change. Avoid sweeping refactors mixed with bug fixes.
* **Commit Messages:** Follow the Conventional Commits format (`feat: ...`, `fix: ...`, `docs: ...`).

---

## 3. Testing Expectations
* **Unit Tests:** All business logic, algorithms, and parsers must have unit tests with mock fixtures.
* **Hermetic Execution:** Tests must run offline without requiring external internet or third-party API credentials.
* **No Production Mutation:** Test runners must never connect to live production databases or dispatch real emails.

---

## 4. Error Handling & Structured Logging
* **No Silent Failures:** Never use bare `except:` or suppress exceptions without logging.
* **Standard Exceptions:** Raise domain-specific exceptions inheriting from `RightFitBaseException`.
* **Structured JSON Logging:** Use standard logger configured in `core/logging.py`. Always include correlation IDs (`request_id`). Never log passwords, tokens, or PII.

---

## 5. Configuration & Dependency Management
* **Environment Configuration:** Read all settings through `core/config.py` backed by environment variables.
* **No Hardcoded Secrets:** Never commit `.env` files or credentials.
* **Dependency Discipline:** Do not add third-party dependencies without documented justification.

---

## 6. Definition of Done (DoD)
A task or pull request is complete only when:
- [ ] Code is implemented cleanly with full type annotations.
- [ ] Automated tests are authored and pass with 100% success rate.
- [ ] Static analysis tools (Ruff, ESLint, TypeScript) report zero errors.
- [ ] Documentation in `docs/` and `.env.example` is updated in the same PR.
- [ ] Architectural decisions are recorded in `docs/adr/` if applicable.
- [ ] No secrets or test credentials are committed.
- [ ] Peer review is completed and approved.

