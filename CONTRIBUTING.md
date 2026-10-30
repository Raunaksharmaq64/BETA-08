# Contributing to RIGHT FIT

Thank you for your interest in contributing to **RIGHT FIT — AI-Powered Career Intelligence Platform**.

RIGHT FIT enforces rigorous architectural standards, documentation governance, and development discipline. Before beginning any work, review this guide and the supreme rulebook: [`AGENTS.md`](./AGENTS.md).

---

## 1. Verified Prerequisites

Before setting up your workspace, ensure the following host tools are installed:
- **Python:** Version 3.11+ (Python 3.13.x verified in Phase 0 audit).
- **Node.js:** Version 20.x or 22.x LTS (Node v22.23.4 verified in Phase 0 audit).
- **npm:** Version 10.x+ (npm 10.9.9 verified in Phase 0 audit).
- **Git:** Version 2.40+.
- **Docker & Docker Compose:** Optional for Phase 1 documentation and design; required for multi-service container builds in subsequent phases.

For detailed local workspace configuration, see [`docs/standards/development.md`](./docs/standards/development.md).

---

## 2. Architecture & Service Boundaries

RIGHT FIT is architected under **Option A — Hybrid Modular Architecture**:
- **Core Career Engine:** Central orchestrator for user identity, resume intelligence, ATS job matching, and application workflows.
- **LeadHunter AI:** Independent satellite service discovering freelance leads and auditing broken websites.
- **Startup Intelligence:** Independent satellite service discovering startup pain points across Reddit, GitHub, and developer feeds.
- **Unified Frontend:** Next.js 16 web application communicating strictly with Core Backend over authenticated REST APIs.

> [!IMPORTANT]
> **Strict Rule:** Never implement cross-service database access. All communication between Core and satellite services must use versioned REST APIs.

---

## 3. Branching & Git Conventions

### Branch Naming
All branches must branch off `main` and use standard lowercase prefixes:
- `feature/<feature-name>` — New capabilities or endpoints (e.g., `feature/resume-parser`).
- `fix/<bug-name>` — Bug fixes (e.g., `fix/token-expiration-check`).
- `refactor/<module-name>` — Code cleanup without functional change (e.g., `refactor/ats-adapter-base`).
- `docs/<doc-name>` — Documentation-only additions or updates (e.g., `docs/phase-1-governance`).
- `test/<test-suite>` — New or updated test suites (e.g., `test/contract-schemas`).
- `chore/<task-name>` — Tooling, linting, or configuration updates (e.g., `chore/editorconfig-update`).

### Commit Message Standards
Commits must follow the Conventional Commits specification:
```
<type>: <short description>
```
*Types:* `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `build`, `ci`.

*Examples:*
- `feat: add PDF resume extraction adapter`
- `fix: prevent duplicate job records in ATS normalizer`
- `docs: add service ownership diagram`

---

## 4. Development & Pull Request Workflow

1. **Phase Discipline:** Work must remain strictly within the currently active phase. Never implement out-of-scope features without explicit architectural approval.
2. **Inspect Existing Implementations:** Before adding new logic, inspect existing modules to avoid duplicating functionality.
3. **Write Tests:** Every new endpoint, service, or adapter must include automated unit or contract tests.
4. **Update Documentation in the Same PR:** If code, schema, API contracts, or environment variables change, the corresponding documentation in `docs/` and `.env.example` MUST be updated in the same pull request.
5. **No Hardcoded Secrets:** Never commit `.env` files, API keys, database credentials, or tokens.

### Submitting a Pull Request
- Ensure all automated checks pass locally.
- Use the repository [Pull Request Template](.github/pull_request_template.md).
- Request review from the designated module or architectural owner.

