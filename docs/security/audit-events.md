# Security Audit Logging & Sanitization Standards

## 1. Overview & Objectives

In compliance with SOC 2 Type II, ISO 27001, and GDPR accountability standards (Art. 5(2)), the **RIGHT FIT** Core Career Engine logs all authentication events, authorization modifications, privacy updates, and account lifecycle transactions into an immutable security audit trail.

Security audit logs provide forensics capability, intrusion detection telemetry, and legal proof of compliance.

---

## 2. Event Taxonomy (`AuditEventType`)

Standardized security event types are defined in `contracts/security/audit.py`:

| Event Type | Trigger | Security Relevance |
|---|---|---|
| `REGISTER` | New candidate account created. | User creation telemetry. |
| `LOGIN_SUCCESS` | Successful authentication with valid credentials. | Session tracking and anomaly detection. |
| `LOGIN_FAILED` | Failed authentication attempt (invalid password or email). | Brute-force & credential stuffing detection. |
| `LOGOUT` | Candidate explicitly terminates session or revokes refresh tokens. | Session lifecycle tracking. |
| `TOKEN_REFRESH` | Refresh token successfully exchanged for a new access token. | Normal token rotation monitoring. |
| `TOKEN_REUSE_DETECTED` | Re-use of an already rotated refresh token detected. | **CRITICAL ALERT**: Active session hijack or replay attack. |
| `PASSWORD_CHANGE` | Authenticated user modifies their account password. | Credential modification log. |
| `PASSWORD_RESET_REQUEST` | Password recovery initiated via email. | Account recovery tracking. |
| `PASSWORD_RESET_SUCCESS` | Password successfully reset with valid one-time token. | Credential modification log. |
| `EMAIL_VERIFICATION_SENT` | Verification link generated and dispatched. | Onboarding telemetry. |
| `EMAIL_VERIFIED` | Candidate confirms email address via verification token. | Account status transition. |
| `PRIVACY_SETTINGS_UPDATED`| Candidate adjusts visibility or AI sharing permissions. | Privacy compliance record. |
| `CONSENT_GRANTED` | User grants formal consent (terms, AI processing, marketing).| Legal compliance record. |
| `CONSENT_REVOKED` | User withdraws previously granted consent. | Legal compliance record. |
| `DATA_EXPORT_REQUESTED` | Machine-readable data export generated. | Data rights request tracking. |
| `ACCOUNT_DELETION_REQUESTED`| Candidate initiates account deletion and enters grace period. | Account termination log. |

---

## 3. Automated Sensitive Data Sanitization

Security logs must never become a source of credential leakage. The `audit_service.py` implements an automated recursive redaction algorithm:

```python
REDACTED_KEYS = {
    "password", "new_password", "old_password",
    "token", "refresh_token", "access_token",
    "secret", "hash", "password_hash",
    "authorization", "cookie", "credential"
}
```

### Redaction Rules:
1. Every dictionary passed to `audit_service.record_event()` is recursively inspected.
2. Any key whose lowercase string contains a redacted keyword has its value replaced with `"[REDACTED]"`.
3. Raw passwords, plaintext tokens, and cryptographic secrets are guaranteed never to appear in audit tables or application log streams.

---

## 4. Audit Table Schema

Audit records are stored in PostgreSQL table `security_audit_events`:

```sql
CREATE TABLE security_audit_events (
    id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(512),
    payload_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_security_audit_events_user_id ON security_audit_events(user_id);
CREATE INDEX ix_security_audit_events_event_type ON security_audit_events(event_type);
CREATE INDEX ix_security_audit_events_created_at ON security_audit_events(created_at);
```

### Immutability Standards
- `security_audit_events` is **INSERT-ONLY**.
- No application API endpoint exists to update or delete audit records.
- In the event of candidate account deletion, `user_id` is set to `NULL` via `ON DELETE SET NULL`, preserving the audit event itself while breaking linkability to the deleted user's personal identity.

