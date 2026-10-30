# AGENTS.md — Central Engineering Rulebook & Governance

> **CRITICAL DIRECTIVE FOR ALL AI AGENTS AND HUMAN DEVELOPERS:**  
> This file establishes the supreme architectural, governance, and development rules for **RIGHT FIT**. Every instruction in this document is mandatory. Never deviate, bypass, or invent behavior without explicit written architectural approval.

---

## 1. Project Identity & Vision

- **Official Product Name:** RIGHT FIT
- **Product Category:** AI-Powered Career & Opportunity Intelligence Platform
- **Core Identity:**  
  RIGHT FIT is a unified, next-generation career and opportunity intelligence system. It is **NOT merely a traditional job board or resume builder**, but a comprehensive opportunity intelligence platform serving students, freshers, experienced professionals, career changers, freelancers, and independent developers:
  - AI-driven resume parsing and skill-gap diagnostics.
  - Autonomous multi-source job discovery across 50+ ATS platforms.
  - Deterministic skill-to-role matching with auditable fit traces.
  - Job legitimacy verification and ghosting detection.
  - Full-lifecycle application management (CRM-lite).
  - Freelance client acquisition and broken-website lead intelligence.
  - Startup pain-point and "help-wanted" technical opportunity mining.
  - Market compensation, equity cliffs, and benefits analysis.
  - Structured interview preparation and negotiation intelligence.

### Technology Stack Standards (Architectural Target)
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons.
- **Core Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic.
- **Database:** PostgreSQL (with `pgvector` for semantic embeddings when required).
- **Background Processing:** Redis + Celery (with local background task fallbacks for local dev).
- **AI Integrations:** Provider-independent gateway (Google Gemini API initially; extensible to Claude, OpenAI, etc.).
- **Infrastructure & Deployment:** Docker, Docker Compose, Nginx (reverse proxy), AWS EC2, AWS S3 (for secure document storage), AWS Secrets Manager.
- **Code Quality & Testing:** Ruff, ESLint, TypeScript Compiler (`tsc`), Pytest, HTTPX, Playwright.

### Approved Architecture: Option A — Hybrid Modular Architecture
1. **Core Career Engine (`backend/`):** Primary orchestrator for user identity, candidate profiles, resume intelligence, ATS job matching, application CRM, and service aggregation. Evolves from `agentic-career-search`.
2. **Independent Freelance Service (`services/leadhunter/`):** Autonomous lead-generation service identifying local business website gaps and broken sites.
3. **Independent Startup Discovery Service (`services/startup_intelligence/`):** Autonomous scanner discovering startup pain points across Reddit, GitHub, Hacker News, and launch communities.
4. **Unified Presentation Layer (`frontend/`):** A single Next.js application presenting an integrated dashboard for jobs, freelance leads, and startup opportunities.
5. **Decoupled REST & Contract Boundaries:** All inter-service communication occurs over versioned HTTP/REST endpoints defined in `contracts/`. No shared in-memory state or direct database coupling.

---

## 2. Repository Rules & Boundary Protection

- **Single Project Root:** All development and configuration MUST reside within `C:\Users\Sahil\Desktop\manit\rightFIT`. Never create a nested root or duplicate project.
- **Never Create a Duplicate Core:** The existing `agentic-career-search` evolves into the Core Career Engine. Do not create an alternative Core service.
- **Inspect Before Creating:** Always inspect existing modules and documentation before creating files. Never duplicate existing functionality.
- **Preserve Legacy Source Code:** The three original repositories outside `rightFIT` (`../agentic-career-search`, `../ai agents`, `../Startups-problrms-hunter`) must remain untouched until integration phases are formally approved.
- **Service Isolation:** Frontend communicates exclusively with Core Backend. Private satellite services (`leadhunter`, `startup_intelligence`) are NEVER exposed directly to the frontend or public ingress.

---

## 3. Mandatory Development Workflow

Every developer and AI agent must adhere to the 11-step lifecycle:
1. **Requirement Understanding:** Review user needs, PRD, and active phase boundary.
2. **Existing Functionality Search:** Check `docs/` and existing modules before writing code.
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

## 4. Security & Privacy Rules

- **Zero Secrets in Code:** Never hardcode secrets, API keys, passwords, or tokens. Never commit `.env` files.
- **Input Validation:** Validate all inputs using strict Pydantic v2 models and TypeScript types.
- **Resume PII Protection:** Treat resumes as confidential candidate PII. Store files in private, encrypted S3 buckets with expiring pre-signed URLs.
- **Authorization:** Enforce user-level multi-tenant authorization on every protected route.
- **No Sensitive Logging:** Never log passwords, JWT tokens, Authorization headers, or candidate personal contact data.

---

## 5. API Design & Communication Rules

- **REST Conventions:** Follow REST semantics with standard HTTP status codes.
- **Versioning:** Version all public and internal service contracts under `/api/v1/`.
- **Pagination Everywhere:** All collection endpoints must implement bounded pagination (`limit`, `offset` or cursor).
- **Standard Error Envelopes:** Standardize errors using the unified error payload (`success: false`, `error: { code, message, details }`).
- **Resilience:** Configure explicit HTTP timeouts (5.0s max for internal REST) and exponential backoff retries on transient errors.
- **Service Authentication:** Authenticate internal service-to-service calls using pre-shared HMAC keys (`X-Internal-Service-Key`).
- **Idempotency:** Ensure background tasks and retryable operations are idempotent.

---

## 6. Database Governance Rules

- **Service-Owned Data:** Each service owns its database/schema (`career_core`, `leadhunter_db`, `startup_intel_db`).
- **No Cross-Service Direct Access:** Direct cross-database joins or cross-schema queries are **STRICTLY FORBIDDEN**. Data must be exchanged via REST APIs.
- **Migration Hygiene:** Run migrations only in approved implementation phases. Every migration must have a functional `downgrade()`.
- **UTC Timestamps:** All timestamp fields must be stored in UTC (`TIMESTAMPTZ`).

---

## 7. AI & LLM Integration Rules

- **Never Invent Facts:** AI models must never hallucinate candidate qualifications, company signals, or salary figures.
- **Explainable Recommendations:** Every match score, ranking, or priority tier must include an auditable explanation.
- **Evidence & Provenance:** Maintain source URLs, post excerpts, and retrieval timestamps for all startup pain-point signals.
- **Untrusted Output Validation:** Treat all AI responses as untrusted input; validate against strict Pydantic schemas before persisting.
- **Human-in-the-Loop:** External actions (job applications, outreach emails) **REQUIRE EXPLICIT HUMAN APPROVAL**. Never auto-submit or auto-send.

---

## 8. Documentation Governance Rules

- **Documentation as Code:** Update documentation in the exact same commit or pull request as code changes.
- **ADR Discipline:** Significant architectural decisions must be recorded as Architecture Decision Records (`docs/adr/`).
- **Truthful Status Labels:** Clearly distinguish between `Planned`, `In Development`, `Implemented`, and `Verified`. Never claim an unimplemented feature is complete.

---

## 9. Phase Discipline (Strict Scope Boundary)

Developers and AI agents must strictly follow the approved phase-by-phase roadmap:
- Never silently skip a phase.
- Never implement features belonging to future phases.
- Phase 1 scope is strictly **Product Foundation & Governance** (directory structure, documentation, standards, ADRs, templates).
- Application coding, feature implementation, and migrations are deferred to Phase 2 onwards.

---

## 10. Architectural Sign-off

- **Document Version:** 1.1.0
- **Status:** APPROVED & MANDATORY
- **Applies to:** All AI coding assistants, engineering leads, and contributing developers.
