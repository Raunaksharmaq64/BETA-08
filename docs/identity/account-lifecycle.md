# RIGHT FIT — Account Lifecycle & Recovery Specification
**Version:** 1.0.0  
**Phase:** 3 — Identity, Candidate Profile & Privacy Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Lifecycle State Machine

Every user account in the Core Career Engine transitions through five explicit states:

```
[ PENDING_VERIFICATION ] ──(Verify Email)──► [ ACTIVE ]
          │                                      │
          ├─────────(Admin Action)──────────────► [ SUSPENDED ]
          │                                      │
          └─────────(Delete Request)────────────► [ DELETION_PENDING ] ──(30d Grace)──► [ DELETED ]
```

### 1.1 State Definitions & Capabilities

| State | Authentication Allowed | Profile Modification | Application Matching | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `PENDING_VERIFICATION` | Yes | Limited | Disabled | Initial registration state until email verified. |
| `ACTIVE` | Yes | Full | Enabled | Standard operational account state. |
| `SUSPENDED` | No (HTTP 403) | Disabled | Disabled | Security hold or terms-of-service violation. |
| `DELETION_PENDING` | Status check only | Disabled (HTTP 403) | Disabled | Active 30-day statutory grace period. |
| `DELETED` | No (HTTP 401) | Disabled | Disabled | Permanent erasure; anonymized audit record. |

---

## 2. Email Verification Workflow

1. During registration, the server generates a cryptographically random 32-byte URL-safe token:
   $$\text{token} = \text{secrets.token\_urlsafe}(32)$$
2. Only the SHA-256 hash of the token is persisted to `email_verification_tokens`:
   $$\text{token\_hash} = \text{SHA-256}(\text{token})$$
3. Verification tokens expire after **24 hours**.
4. Upon submission to `POST /api/v1/auth/verify-email`, the token is redeemed, marked `is_used = True`, and the user's `is_email_verified` attribute is set to `True`.
5. Tokens are strictly single-use. Replay attempts are rejected with HTTP 400.

---

## 3. Account Recovery & Password Reset

### 3.1 Account Enumeration Protection
`POST /api/v1/auth/forgot-password` returns an identical success message regardless of whether the submitted email address exists in the database:
> *"If an account exists with this email address, a password recovery link has been dispatched."*

This completely mitigates account enumeration attacks.

### 3.2 Single-Use Reset Token Workflow
1. Reset tokens expire after **30 minutes**.
2. Only the SHA-256 hash is persisted in `password_reset_tokens`.
3. Upon redemption via `POST /api/v1/auth/reset-password`:
   - The token is validated and marked `is_used = True`.
   - The new password is encrypted with Argon2id.
   - **All existing active refresh sessions are immediately revoked**, forcing all client devices to re-authenticate.
   - A `PASSWORD_RESET_COMPLETE` security audit event is recorded.
