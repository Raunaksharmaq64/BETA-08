# Consent Management & Auditability

## 1. Overview & Compliance Objectives

Under GDPR (Art. 7), CCPA/CPRA, and global data privacy standards, consent must be freely given, specific, informed, unambiguous, and easily revocable. 

**RIGHT FIT** implements an immutable, append-only consent tracking architecture. Every consent granted or withdrawn is recorded as an independent transaction in PostgreSQL with client telemetry (IP address, user agent, timestamps, and terms version).

---

## 2. Consent Data Model

Consent records are persisted in table `consent_records`:

```sql
CREATE TABLE consent_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    consent_type VARCHAR(64) NOT NULL,
    granted BOOLEAN NOT NULL DEFAULT TRUE,
    terms_version VARCHAR(32) NOT NULL DEFAULT 'v1.0',
    ip_address VARCHAR(45),
    user_agent VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at TIMESTAMP WITH TIME ZONE
);
```

### Supported Consent Types (`consent_type`)
- `TERMS_OF_SERVICE`: Mandatory agreement to platform terms during registration.
- `PRIVACY_POLICY`: Mandatory acknowledgment of privacy notice during registration.
- `AI_DATA_PROCESSING`: Explicit opt-in for automated agentic processing and skill extraction.
- `MARKETING_COMMUNICATIONS`: Optional consent for email product announcements and newsletters.
- `THIRD_PARTY_INTEGRATIONS`: Specific consent before synchronizing data with external services.

---

## 3. Consent Lifecycle & Revocation

### 3.1 Granting Consent
- Occurs automatically at registration (`TERMS_OF_SERVICE`, `PRIVACY_POLICY`) or via `POST /api/v1/privacy/consent`.
- The system captures:
  - `consent_type`
  - `terms_version`
  - Client IP address & User-Agent string from the HTTP request headers.
  - `created_at` timestamp.
  - Generates audit event `CONSENT_GRANTED`.

### 3.2 Withdrawing Consent
- Triggered via `DELETE /api/v1/privacy/consent/{consent_type}` or via the Privacy Settings dashboard.
- The system marks `granted = False` and stamps `withdrawn_at = utc_now()`.
- Generates audit event `CONSENT_REVOKED`.
- Active background tasks honoring this consent purpose are immediately instructed to cease processing for that candidate.

---

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/privacy/consent` | Lists all active and historical consent records for the authenticated candidate. |
| `POST` | `/api/v1/privacy/consent` | Grants or refreshes a consent grant (`ConsentGrantRequest`). |
| `DELETE` | `/api/v1/privacy/consent/{consent_type}` | Revokes consent for the specified type. |

---

## 5. Security & Tamper Resistance

Consent records are append-logged. When a user withdraws consent, the record is not deleted; rather, `withdrawn_at` is set, preserving complete legal provenance of when consent was active and when it was rescinded.

