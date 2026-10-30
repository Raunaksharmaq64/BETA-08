# Open Decisions Log

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Open Architectural, Data & Product Decisions Log
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## Decision 1: Centralized User Authentication & Profile Engine

* **Question:** Which authentication system should serve as the authoritative identity provider for RIGHT FIT?
* **Context:** `agentic-career-search` completely lacks user authentication, user models, and session management. In contrast, `ai agents` (LeadHunter) has a fully implemented and tested JWT authentication engine (`UserModel`, password hashing via Werkzeug, brute-force lockout tracking, HTTP-only cookie management, OTP verification).
* **Available Options:**
  - *Option A:* Build a completely new authentication system from scratch for Core Backend.
  - *Option B (Recommended):* Port and adapt the battle-tested authentication models and JWT utilities from `ai agents` into `backend/app/modules/auth/` and `backend/app/modules/users/`.
  - *Option C:* Outsource authentication to a third-party managed provider (e.g. Auth0, Clerk, Supabase Auth).
* **Recommendation:** **Option B.** Reusing LeadHunter's existing authentication logic saves significant development time, leverages already verified security tests (20/20 test pass rate), and avoids third-party subscription costs.
* **Reason:** Proven security implementation with zero external SaaS lock-in.
* **Required Approver:** Principal Software Architect / Lead Developer
* **Status:** PENDING APPROVAL

---

## Decision 2: Startup Intelligence Data Persistence Evolution

* **Question:** How should data persistence for `Startups-problrms-hunter` be structured in RIGHT FIT?
* **Context:** `Startups-problrms-hunter` currently writes all scraped posts and opportunity leads to a single flat JSON file (`data/leads.json`). This approach has zero transaction isolation, fails under concurrent requests, lacks indexing, and cannot scale.
* **Available Options:**
  - *Option A:* Keep `leads.json` file persistence inside `services/startup_intelligence`.
  - *Option B (Recommended):* Modernize `services/startup_intelligence` to use PostgreSQL with an isolated schema (`startup_intel.pain_points`, `startup_intel.evidence`), managed via SQLAlchemy.
  - *Option C:* Use a NoSQL document database (e.g., MongoDB).
* **Recommendation:** **Option B.** Unifying on PostgreSQL eliminates flat-file concurrency corruption, aligns with Option A Hybrid Architecture, and avoids introducing an additional database engine.
* **Reason:** Prevents data corruption during concurrent scans and standardizes the database technology stack.
* **Required Approver:** Database Architect / Principal Architect
* **Status:** PENDING APPROVAL

---

## Decision 3: PDF / DOCX Resume Parsing Engine Selection

* **Question:** What library should be adopted for binary resume file extraction in the Core Career Engine?
* **Context:** The legacy `agentic-career-search` includes ATS keyword coverage and skills fit scoring, but operates exclusively on pre-extracted text strings. It lacks binary PDF/DOCX file extraction.
* **Available Options:**
  - *Option A:* `pypdf` + `python-docx` (Lightweight, pure Python, zero native system dependencies).
  - *Option B:* `pdfminer.six` (Detailed layout and coordinate extraction, higher CPU usage).
  - *Option C:* External OCR / Document AI API (e.g., AWS Textract, Google Document AI).
* **Recommendation:** **Option A (`pypdf` + `python-docx`).** Provides fast, secure, local offline text extraction suitable for 95% of standard resume layouts without recurring cloud API fees.
* **Reason:** Balances parsing speed, zero cost, and minimal infrastructure complexity.
* **Required Approver:** Backend Lead / Principal Architect
* **Status:** PENDING APPROVAL

---

## Decision 4: Email Verification Strategy in Startup Discovery

* **Question:** How should founder and startup contact emails be verified?
* **Context:** `Startups-problrms-hunter/email_verifier.py` currently initiates direct socket connections to destination MX servers and executes `RCPT TO` commands. This active probing triggers anti-spam defenses and risks getting the host server's IP blocklisted.
* **Available Options:**
  - *Option A:* Retain direct SMTP socket handshakes.
  - *Option B (Recommended):* Drop direct SMTP handshakes. Use passive syntax validation (Pydantic `EmailStr`) and DNS MX record checks, paired with B2B API verification (Hunter/Tomba) only when configured.
* **Recommendation:** **Option B.** Protects the application's domain and IP reputation from being blocklisted.
* **Reason:** Critical operational safety and deliverability safeguard.
* **Required Approver:** Security Reviewer / Lead Architect
* **Status:** PENDING APPROVAL

