# Documentation Governance & Maintenance Policy

- **Title:** Engineering Documentation Standards
- **Purpose:** Mandates metadata headers, synchronization rules, and lifecycle requirements for all repository documentation.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Documentation as Code (Mandatory Rule)
Whenever an engineer or AI agent modifies:
- System features or user journeys
- REST API contracts or endpoint signatures
- Database schemas or Alembic migrations
- Third-party or inter-service integrations
- Environment variables or configurations
- Docker or deployment topology
- Security or authentication rules

**The corresponding document in `docs/` and `.env.example` MUST be updated within the exact same pull request.**

## 2. Mandatory Metadata Header
Every Markdown document in `docs/` must begin with the standardized header block:
```markdown
# Document Title

- **Title:** Full Descriptive Title
- **Purpose:** Concise 1-2 sentence statement of document utility.
- **Status:** DRAFT | ACTIVE | APPROVED
- **Owner:** Role or Domain Team (e.g., Backend Architect / TBD)
- **Last Updated:** YYYY-MM-DD
```

## 3. Strict Truthfulness Rules
- **No Hypothetical Claims:** Never mark an unimplemented feature as complete or active. Clearly tag unbuilt components as `[TBD]`, `[PLANNED]`, or `[DRAFT]`.
- **Obsolescence Cleanup:** When a service, model, or route is deprecated, update or archive its documentation immediately.

## 4. Open Questions & TBDs
- [TBD] Automated CI documentation linter checking for broken links in markdown.

