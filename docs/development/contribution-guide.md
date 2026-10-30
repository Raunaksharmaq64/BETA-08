# Contribution Guidelines

- **Title:** Engineering Contribution Guide & PR Standards
- **Purpose:** Standards for submitting code, managing branches, opening pull requests, and adhering to engineering governance.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Golden Rules for Contributors
1. **Never Commit Secrets:** Check `git status` and ensure `.env` or credential files are not staged.
2. **Synchronize Documentation:** PRs modifying features, models, APIs, or configuration MUST include documentation updates in the same PR.
3. **No Blind Legacy Copies:** Code reused from `agentic-career-search`, `ai agents`, or `Startups-problrms-hunter` must be refactored, type-annotated, and tested.
4. **Human-in-the-Loop Integrity:** Do not introduce autonomous submission or unsolicited mass email logic.

## 2. Pull Request Submission Checklist
- [ ] Branch named according to Git conventions (`feature/*`, `fix/*`, `refactor/*`).
- [ ] All unit, integration, and contract tests pass.
- [ ] Code formatted with Ruff (Python) and Prettier/ESLint (TypeScript).
- [ ] Relevant documentation in `docs/` updated.
- [ ] `.env.example` updated if new environment variables were introduced.
- [ ] Clear description of changes, motivation, and test proof provided.

## 3. Open Questions & TBDs
- [TBD] Code review assignment automation via `.github/CODEOWNERS`.

