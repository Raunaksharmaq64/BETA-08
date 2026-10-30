# API & Service Communication Standards

- **Title:** Universal REST API Design Standards
- **Purpose:** Mandates endpoint structures, request/response formats, error models, and pagination patterns.
- **Status:** APPROVED
- **Owner:** Principal Architect / Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. REST Architecture Principles
- **JSON Exclusively:** All request payloads and response bodies must use `application/json` (except multi-part file uploads).
- **Versioning:** All public endpoints must be prefixed with `/api/v1/`. Breaking changes require a new version increment (`/api/v2/`).
- **HTTP Status Codes:** Use accurate HTTP status codes:
  - `200 OK`: Successful retrieval or update.
  - `201 Created`: Resource successfully created.
  - `202 Accepted`: Asynchronous task scheduled (returns task ID).
  - `204 No Content`: Successful deletion.
  - `400 Bad Request`: Client validation error.
  - `401 Unauthorized`: Missing or invalid authentication token.
  - `403 Forbidden`: Authenticated user lacks permission.
  - `404 Not Found`: Resource does not exist.
  - `422 Unprocessable Entity`: Semantic/schema validation error.
  - `429 Too Many Requests`: Rate limit reached.
  - `500 Internal Server Error`: Unhandled server exception.

## 2. Standard Envelope Schemas

### Success Envelope (Single Entity):
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "timestamp": "2026-10-30T22:00:00Z"
  }
}
```

### Error Envelope:
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Job posting with id 12345 does not exist.",
    "details": []
  },
  "meta": {
    "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "timestamp": "2026-10-30T22:00:00Z"
  }
}
```

## 3. Pagination & Query Parameters
- Collections must accept `limit` (default: 20, max: 100) and `offset` (or cursor `starting_after`).
- Filtering parameters must use snake_case (e.g., `?is_remote=true&min_salary=100000`).

## 4. Open Questions & TBDs
- [TBD] Rate limit tiers (Anonymous: 60 req/min, Authenticated: 300 req/min).

