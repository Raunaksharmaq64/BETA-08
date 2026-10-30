# Git & Version Control Standards

- **Title:** Version Control, Branching & Commit Conventions
- **Purpose:** Standardizes branch naming, commit message semantics, pull request workflows, and repository governance.
- **Status:** APPROVED
- **Owner:** DevOps Engineer / Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Branch Naming Conventions
All development branches must use explicit, lowercase prefixes followed by a descriptive slug:

* `feature/<feature-name>` — New feature implementation (e.g., `feature/ats-parser`)
* `fix/<bug-name>` — Bug correction (e.g., `fix/duplicate-job-keys`)
* `refactor/<module-name>` — Code improvement without functional change (e.g., `refactor/lead-scraper-adapter`)
* `docs/<document-name>` — Documentation updates (e.g., `docs/system-architecture-update`)
* `test/<test-suite>` — Adding or fixing test cases (e.g., `test/contract-schemas`)
* `chore/<task-name>` — Maintenance, tooling, or dependency updates (e.g., `chore/docker-compose-ports`)

## 2. Commit Message Standards (Conventional Commits)
Commits must follow the `<type>: <description>` format:

### Permissible Types:
- `feat:` Introduces a new feature or endpoint.
- `fix:` Fixes a software bug or regression.
- `refactor:` Code restructuring without behavioral change.
- `docs:` Documentation-only changes.
- `test:` Adding or correcting automated tests.
- `chore:` Tooling, configuration, or build system updates.
- `build:` Changes that affect the build system or external dependencies.
- `ci:` Changes to CI configuration files and scripts.

### Examples:
- `feat: add resume analysis contract schema`
- `fix: prevent duplicate job imports in multi-source adapter`
- `refactor: isolate job source adapter from database layer`
- `docs: update system architecture with LeadHunter integration`
- `chore: add docker-compose production template`

## 3. Pull Request & Branch Protection Rules
- **Protect `main` Branch:** Direct pushes to `main` are strictly forbidden. All changes require an approved Pull Request.
- **Single Responsibility Commits:** Avoid monolithic commits containing unrelated changes.
- **Never Commit Secrets:** Any commit containing secrets, keys, or `.env` files will be rejected and purged from Git history.
- **CI Verification:** PRs must pass automated linting, type checks, and tests before merge.

## 4. Open Questions & TBDs
- [TBD] Squash-and-merge vs. rebase-and-merge policy on Github.

