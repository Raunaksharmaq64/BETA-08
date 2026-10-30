# API Authentication & Token Lifecycles

- **Title:** API Authentication Specification
- **Purpose:** Governs JWT structure, header formats, token expiration, and inter-service authentication.
- **Status:** APPROVED
- **Owner:** Security Architect / Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Client Authentication (JWT)
All protected endpoints require an `Authorization` header containing a valid Bearer token:
```http
Authorization: Bearer <jwt_access_token>
```

### Token Lifecycles:
- **Access Token:** Short-lived (60 minutes). Signed using HMAC-SHA256 (`HS256`) or asymmetric `RS256`. Contains `sub` (user_id), `email`, and `roles`.
- **Refresh Token:** Long-lived (7 days). Stored securely (HTTP-only, Secure cookie for web clients) and used exclusively at `/api/v1/auth/refresh`.

## 2. Internal Service-to-Service Authentication
Calls between Core Backend and satellite services (LeadHunter, Startup Intelligence) use pre-shared API keys passed via headers:
```http
X-Internal-Service-Key: <secret_service_key>
X-Originating-Service: rightfit-core
```

## 3. Open Questions & TBDs
- [TBD] Transition from symmetric HS256 to asymmetric RS256 with JWKS endpoint in Phase 3.

