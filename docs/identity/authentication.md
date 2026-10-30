# RIGHT FIT — Authentication Architecture
**Version:** 1.0.0  
**Phase:** 3 — Identity, Candidate Profile & Privacy Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Overview

The Core Career Engine owns all user identity and authentication workflows for the RIGHT FIT platform. Satellite microservices (LeadHunter AI, Startup Intelligence) do not maintain independent user identity stores.

---

## 2. Password Security & Argon2id Hashing

RIGHT FIT implements the OWASP-recommended **Argon2id** password hashing algorithm:

- **Algorithm:** Argon2id (hybrid data-dependent and data-independent memory-hard function)
- **Time Cost ($t$):** 3 iterations
- **Memory Cost ($m$):** 64 MB ($65,536\text{ KiB}$)
- **Parallelism ($p$):** 4 threads
- **Salt Length:** 16 bytes cryptographically random
- **Hash Length:** 32 bytes

```python
# Hash generation
hash_str = argon2.PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4).hash(password)
```

> [!CAUTION]
> Raw passwords and password hashes are **strictly excluded** from API responses, serialization models, and security audit logs.

---

## 3. JWT Access Tokens

Access tokens are short-lived JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`):

- **Lifetime:** 15 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 15`)
- **Issuer (`iss`):** `rightfit_core`
- **Type (`type`):** `access`
- **Claims:**
  - `sub`: User UUID
  - `email`: Normalized email address
  - `role`: Role enum (`CANDIDATE`, `RECRUITER`, `ADMIN`)
  - `jti`: Unique token instance UUID (prevents replay)
  - `iat`: Issue timestamp (Unix seconds)
  - `exp`: Expiration timestamp (Unix seconds)

---

## 4. Dual Transport Support (Cookies & Bearer)

To support both modern Single Page Applications (Next.js) and programmatic API consumers:
1. **HttpOnly Cookies:** On successful login, the server sets `rightfit_session` with `HttpOnly`, `SameSite=Lax`, and `Secure` (in production). This eliminates XSS-based token theft from `localStorage`.
2. **Bearer Token Authorization:** Clients can also pass `Authorization: Bearer <token>` in HTTP headers.

---

## 5. API Endpoints

- `POST /api/v1/auth/register`: Creates candidate account and triggers verification token.
- `POST /api/v1/auth/login`: Verifies Argon2id hash and returns token pair + cookie.
- `POST /api/v1/auth/logout`: Revokes active refresh token and clears session cookies.
- `GET /api/v1/auth/me`: Returns public authenticated user profile.

