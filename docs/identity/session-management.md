# RIGHT FIT — Session Management & Refresh Token Rotation
**Version:** 1.0.0  
**Phase:** 3 — Identity, Candidate Profile & Privacy Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Threat Model & Architecture

Traditional long-lived refresh tokens represent a high-value target for exfiltration. RIGHT FIT mitigates token theft using **Rotating Refresh Tokens** with **Token Family Tracking** and **Replay Attack Detection**.

```
[ Client ]                        [ Core Engine ]                        [ Database ]
    │                                    │                                    │
    │─── Refresh Request (Token A) ─────►│                                    │
    │                                    │─── Verify Token A Hash & State ───►│
    │                                    │    (Valid & unrevoked)             │
    │                                    │─── Mark Token A Revoked ──────────►│
    │                                    │─── Store Token B Hash (Family 1) ─►│
    │◄── Return (New Access + Token B) ──│                                    │
    │                                    │                                    │
    │=== IF ATTACKER REPLAYS TOKEN A === │                                    │
    │─── Replay Request (Token A) ──────►│                                    │
    │                                    │─── Query Token A Hash ────────────►│
    │                                    │    (Record is already REVOKED!)    │
    │                                    │                                    │
    │                                    │─── ALARM: Replay Attack Detected!  │
    │                                    │─── Revoke ENTIRE Family 1 ────────►│
    │◄── 401 Unauthorized (Terminated) ──│                                    │
```

---

## 2. Token Storage and Hashing

Raw refresh tokens are never persisted in the database. When a refresh token is generated:
1. `raw_refresh` is returned to the client in `TokenResponse`.
2. `token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()` is stored in `refresh_tokens`.
3. If the database is compromised, the attacker obtains only SHA-256 hashes that cannot be converted back into valid JWT refresh tokens.

---

## 3. Replay Attack Detection Mechanism

Every refresh token belongs to a cryptographic `family_id`:
1. When `POST /api/v1/auth/refresh` is called:
   - The token hash is looked up in `refresh_tokens`.
   - If the token is found and `is_revoked == False`, it is marked `is_revoked = True` and a new token is generated within the **same `family_id`**.
2. **Replay Scenario:**
   - If an attacker intercepts and attempts to reuse an old, already-revoked refresh token, Core identifies that a revoked token was submitted.
   - Core immediately executes an emergency revocation across all tokens sharing that `family_id`:
     ```sql
     UPDATE refresh_tokens SET is_revoked = true WHERE family_id = :family_id;
     ```
   - Core logs a `SESSION_REVOKED` security audit warning and forces both the legitimate user and attacker to re-authenticate.

---

## 4. Forced Invalidation Events

Active sessions are revoked upon:
- Explicit logout (`POST /api/v1/auth/logout`)
- In-session password update (`POST /api/v1/auth/change-password`)
- Password recovery reset (`POST /api/v1/auth/reset-password`)
- Account deletion initiation (`POST /api/v1/candidate/account-deletion`)
- Account suspension by administrative action

