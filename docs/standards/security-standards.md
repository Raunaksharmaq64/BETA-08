# Security & Privacy Standards

- **Title:** Universal Security, Privacy & Compliance Standards
- **Purpose:** Establishes mandatory security controls, resume PII protection, authentication invariants, and outreach safeguards.
- **Status:** APPROVED
- **Owner:** Security Reviewer (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## 1. Secrets Management & Environment Isolation
* **Zero Hardcoded Secrets:** Never hardcode passwords, API keys, JWT signing secrets, or private tokens in source code.
* **Environment Configuration:** All credentials must be read from environment variables managed via AWS Secrets Manager in production.
* **Git Exclusions:** `.env` and all `.env.*` files (except `.env.example`) are strictly gitignored.
* **Key Entropy:** JWT signing secret (`JWT_SECRET`) must be at least 32 characters (64-character hex recommended).

---

## 2. Authentication & Authorization Controls
* **Stateless JWT:** Client requests require an `Authorization: Bearer <token>` header. Access tokens expire in 60 minutes.
* **Algorithm Hardening:** Strictly enforce `HS256` or `RS256`. Defense against algorithm `none` attacks is verified and mandatory.
* **Brute-Force Defense:** Account lockout tracking enforces temporary account locks after 5 consecutive failed login attempts.
* **Multi-Tenant Data Isolation:** Every query accessing candidate resumes, profiles, or job applications must enforce `WHERE user_id = :authenticated_user_id`.
* **Internal Service Authentication:** Inter-service calls from Core to satellite services must include `X-Internal-Service-Key` verification.

---

## 3. Resume PII Protection & File Upload Security
* **Candidate Confidentiality:** Resumes contain sensitive Personally Identifiable Information (PII) including full names, contact emails, phone numbers, and employment histories.
* **Encrypted Storage:** Stored in private AWS S3 buckets with server-side encryption (AES-256). Files are never accessible via public URLs.
* **Expiring Pre-Signed URLs:** File downloads are brokered through pre-signed S3 URLs with a maximum lifespan of 15 minutes.
* **Upload Validation:** Validate magic numbers / MIME types (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`). Max file size limit: 10 MB. Never execute uploaded files.

---

## 4. Human-in-the-Loop & Outreach Safeguards
* **No Autonomous Job Applications:** The platform must NEVER execute automated application submissions on external ATS systems without explicit human review and confirmation.
* **No Autonomous Cold Emails:** Outreach emails and sales pitches generated for freelance leads must NEVER be sent automatically. The user must review, edit, and click a manual "Send" button.
* **No Direct Socket Handshakes:** Outbound email address verification via direct SMTP `RCPT TO` socket probing is strictly forbidden to prevent IP blacklisting.

---

## 5. Network, CORS & API Ingress
* **CORS Policy:** Strict whitelisting of trusted origins (`FRONTEND_URL`). Wildcard CORS (`*`) is prohibited in production.
* **Rate Limiting:** Protect public endpoints against abuse (Anonymous: 60 req/min; Authenticated: 300 req/min).
* **Sanitized Structured Logging:** Never log passwords, authorization headers, credit card numbers, or candidate PII.

