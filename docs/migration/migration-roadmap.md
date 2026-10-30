# Migration Execution Roadmap

- **Title:** Phased Migration & Service Porting Roadmap
- **Purpose:** Step-by-step sequencing for migrating, adapting, and integrating legacy functionality into RIGHT FIT.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Migration Milestones

### Step 1: Foundation & Governance (Phase 0 - Completed)
- [x] Establish directory tree, AGENTS.md, root README, and all documentation.
- [x] Complete technical audit and reuse matrices.
- [x] Establish configuration placeholders and Docker templates.

### Step 2: Core Foundation & Contracts (Phase 1)
- [ ] Implement Core database models (`core.users`, `core.profiles`, `core.jobs`) and initial Alembic migration.
- [ ] Port ATS source adapters from `agentic-career-search` into `backend/app/integrations/job_sources/`.
- [ ] Port deterministic match scoring engine into `backend/app/modules/matching/`.
- [ ] Define shared contract DTOs in `contracts/`.

### Step 3: Satellite Service Isolation (Phase 1.5)
- [ ] Containerize LeadHunter behind versioned REST endpoints (`services/leadhunter`).
- [ ] Containerize Startup Intelligence behind REST endpoints (`services/startup_intelligence`).
- [ ] Implement Core API integration clients (`backend/app/integrations/leadhunter`, `backend/app/integrations/startup_intelligence`).

### Step 4: Presentation Layer Unification (Phase 2)
- [ ] Scaffold Next.js 16 app with App Router and Tailwind.
- [ ] Deliver unified Dashboard, Resume upload, ATS match view, Freelance leads, and Startup pain points.

## 2. Open Questions & TBDs
- [TBD] Final sign-off on Phase 1 sprint timeline.

