# API & Inter-Service Communication Protocols

- **Title:** API Design, Inter-Service Communication & Contract Governance
- **Purpose:** Mandates protocols, authentication headers, error envelopes, resilience parameters, and request lifecycles.
- **Status:** APPROVED
- **Owner:** Backend Lead (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## 1. Protocol & Transport Standards
* **External Client Ingress:** HTTPS / HTTP/1.1 via Nginx reverse proxy.
* **Internal Inter-Service Mesh:** HTTP/1.1 over Docker bridge network (`rightfit-network`).
* **Content Type:** Strict `application/json; charset=utf-8` for all requests and responses (except multipart/form-data for resume uploads).

---

## 2. Standard Header Envelope
Every internal and external API request must carry:
* `X-Request-ID`: Distributed correlation UUIDv4 generated at ingress and propagated across all service calls.
* `Authorization`: Bearer JWT token (Client-to-Core calls).
* `X-Internal-Service-Key`: Pre-shared HMAC key (Core-to-Satellite calls).

---

## 3. Illustrative Response Envelopes

> [!NOTE]
> The examples below are **illustrative contract specifications**, not implemented runtime endpoints.

### Success Response Envelope (Single Entity)
```json
{
  "success": true,
  "data": {
    "id": "job_01h7x89q2",
    "title": "Senior Backend Engineer",
    "company": "Acme Cloud",
    "fit_score": 0.92,
    "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
    "missing_skills": ["Kafka"]
  },
  "meta": {
    "request_id": "4a1c5d9e-7f2a-4318-b2dc-9f4a12345678",
    "timestamp": "2026-10-31T00:00:00Z"
  }
}
```

### Success Response Envelope (Paginated Collection)
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "total_records": 450,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "request_id": "4a1c5d9e-7f2a-4318-b2dc-9f4a12345678",
    "timestamp": "2026-10-31T00:00:00Z"
  }
}
```

### Error Response Envelope
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed on request payload.",
    "details": [
      {
        "field": "email",
        "issue": "Invalid email address format"
      }
    ]
  },
  "meta": {
    "request_id": "4a1c5d9e-7f2a-4318-b2dc-9f4a12345678",
    "timestamp": "2026-10-31T00:00:00Z"
  }
}
```

---

## 4. Resilience, Timeouts & Retry Policy
* **Internal REST Calls:** Max timeout 5.0 seconds.
* **Bulk Scraping Tasks:** Enqueue asynchronously and return a `202 Accepted` job ticket immediately.
* **Retry Strategy:** Max 3 retries on transient network errors (502/503/504) with exponential backoff and jitter. Never retry on 4xx client errors.
* **Circuit Breaker:** Trip circuit after 5 consecutive failures within a 60-second window, returning a cached or degraded response.

