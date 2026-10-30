# ADR-004: Career Engine Authentication & User Tenancy Strategy

- **Document ID:** ADR-004
- **Title:** Core Career Engine Authentication Strategy & UserModel Ingestion
- **Status:** RECOMMENDATION (REQUIRING APPROVAL)
- **Author:** Principal Software Architect & Security Reviewer
- **Date:** 2026-10-30

---

## 1. Context & Problem Statement
During the Phase 0 audit of `agentic-career-search`, it was discovered that while the repository contains mature ATS source adapters, compensation calculators, and scoring algorithms, it has **zero concept of user identity, authentication, or multi-tenancy**. All database models (`Run`, `Job`, `SourceConfig`) are unowned.

Conversely, the audit of `ai agents` (LeadHunter AI) revealed a **production-hardened authentication system**:
- Database model: `UserModel` (id, username, email, password_hash, is_admin, is_active).
- Password security: Werkzeug secure password hashing (`generate_password_hash`, `check_password_hash`).
- Token architecture: Stateless JWT with `HS256`, algorithm 'none' defense, unique `jti`, and token expiration validation.
- Brute-force protection: `login_tracker` lockout mechanism.
- Testing: 20 automated security test suites with 100% pass rate.

RIGHT FIT requires a unified authentication and multi-tenant authorization layer across the entire platform.

---

## 2. Decision Options Considered

### Option 1: Build a New Authentication Module from Scratch
- *Pros:* Custom-tailored to RIGHT FIT domain requirements.
- *Cons:* High development time, risks introducing new authentication vulnerabilities, redundant work.

### Option 2: Outsource to Third-Party Identity Provider (Auth0 / Clerk / Supabase)
- *Pros:* Fast initial integration.
- *Cons:* Adds external SaaS vendor lock-in, recurring per-user monthly costs, and network latency on every authentication check.

### Option 3 (Recommended): Ingest & Port LeadHunter's Authentication Module into Core Backend
- *Pros:*
  - Fully owned, zero-cost, battle-tested code.
  - Already passes 20 rigorous security test cases (signature tampering, expired tokens, algorithm downgrade attacks).
  - Directly compatible with FastAPI and SQLAlchemy / SQLModel.
- *Cons:* Requires minor migration to adapt table relationships to Core entities (`resumes`, `profiles`, `applications`).

---

## 3. Decision & Architectural Consequences
**We recommend Option 3:**
1. In Phase 1, port the authentication logic from `ai agents/backend/routes_fastapi/auth.py` and `models_async.py` into `rightFIT/backend/app/modules/auth/` and `rightFIT/backend/app/modules/users/`.
2. Core Career Engine becomes the supreme identity provider for the entire platform.
3. Satellite services (LeadHunter, Startup Intelligence) will receive user context via validated JWT claims passed by Core Backend.

---

## 4. Approval Status
- **Status:** PENDING ARCHITECTURAL APPROVAL

