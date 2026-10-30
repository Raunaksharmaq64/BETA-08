# Security & Privacy Audit Report

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Technical Security, Privacy & Vulnerability Audit
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. Secrets Management & Exposure
- **Finding:** No plain-text production credentials, JWT signing keys, or live cloud API tokens were committed in tracked Git history across any of the three repositories.
- **Environment Isolation:** All projects use `.env` loaders (`python-dotenv`, `pydantic-settings`).
- **Enforcement Mechanism:** `ai agents` implements startup verification (`utils/security_fastapi.py:35`) requiring `SECRET_KEY` to be at least 32 characters, preventing deployment with weak default secrets.
- **Remediation Needed:** Ensure `.env` is universally excluded in `.gitignore` and that AWS Secrets Manager is integrated for production deployments.

---

## 2. Authentication & Authorization Controls
- **`agentic-career-search`:** Completely lacks authentication and user tenancy models. All endpoints (`/runs`, `/jobs`) are unauthenticated.
  - *Risk:* Anyone with network access can query or cancel scraping runs.
  - *Action:* Must integrate the Core JWT authentication system in Phase 1.
- **`ai agents` (LeadHunter):** Mature JWT implementation using HS256 with expiration checks (`exp`), issued-at validation (`iat`), and unique token IDs (`jti`).
  - *Brute-Force Protection:* `login_tracker` enforces temporary IP/email lockouts after 5 failed login attempts.
  - *Role-Based Authorization:* `admin_required` FastAPI dependency protects administrative routes (`routes_fastapi/dashboard.py`).
- **`Startups-problrms-hunter`:** Completely unauthenticated. Anyone can trigger expensive scraping runs or modify settings via `POST /api/settings`.
  - *Action:* Must be isolated as an internal satellite service accessible only by Core Backend via internal API keys.

---

## 3. Candidate Privacy & Document Storage (Resume Security)
- **Current State:** Neither `agentic-career-search` nor `Startups-problrms-hunter` stores binary PDF/DOCX files.
- **Target Standard for RIGHT FIT Core:**
  - Resumes must be treated as highly sensitive Personally Identifiable Information (PII).
  - Storage: Resumes must be stored in encrypted private AWS S3 buckets (AES-256) with pre-signed URLs expiring in 15 minutes.
  - Never store raw resume PDFs in local public directories or container images.
  - Data Minimization: Candidate contact data (phone numbers, addresses) should be masked in logging and telemetry.

---

## 4. Inbound / Outbound Outreach Safeguards (Anti-Spam & Reputation)
- **Direct SMTP Handshake Danger:** `Startups-problrms-hunter/email_verifier.py` connects directly to MX servers and executes `RCPT TO` commands.
  - *Critical Risk:* Mail server firewalls flag IP addresses performing automated `RCPT` handshakes as directory harvesting spam bots. Host IP will be blocklisted on Spamhaus or Barracuda.
  - *Mitigation:* **DROP direct SMTP verification.** Use syntax validation and DNS MX record checks, or delegate to reputable B2B enrichment APIs with rate limits.
- **Unsolicited Email Dispatch:** `ai agents/backend/routes_fastapi/api_outreach.py` contains SMTP email delivery.
  - *Compliance Rule:* Maintain strict Human-in-the-Loop controls. The system must NEVER automatically dispatch emails without explicit user review and a manual "Send Pitch" button click.

---

## 5. Network Security, CORS & Input Validation
- **CORS Configuration:**
  - `ai agents`: Reads `CORS_ALLOWED_ORIGINS` from environment variables, defaulting to explicit local frontend ports (`http://localhost:3000`).
  - `Startups-problrms-hunter`: Configures `allow_origins=["*"]` (wildcard CORS).
  - *Action:* Restrict CORS to explicit trusted domains in Core API.
- **SQL Injection Prevention:**
  - `agentic-career-search`: Fully parameterized queries via SQLAlchemy 2.0 ORM. Zero raw SQL string interpolation.
  - `ai agents`: Parameterized queries via SQLModel Async.
  - `Startups-problrms-hunter`: No SQL engine used (JSON storage).
- **SSRF (Server-Side Request Forgery) Defense:**
  - Source adapters in `agentic-career-search` fetch arbitrary user-configured URLs (`base_url`).
  - *Mitigation:* Source configs must validate URLs to block internal loopback/private subnet addresses (`127.0.0.1`, `169.254.169.254`, `10.0.0.0/8`, `192.168.0.0/16`).

