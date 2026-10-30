# RIGHT FIT — Universal API Error Conventions
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE GOVERNANCE  

---

## 1. Overview

To deliver a predictable and consistent developer experience across all microservices and frontend clients, RIGHT FIT enforces a universal error response structure.

Every non-2xx HTTP response emitted by **Core Career Engine**, **LeadHunter AI**, or **Startup Intelligence** must adhere to the `APIErrorResponse` contract.

---

## 2. Error Response Envelope Specification

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request payload failed schema validation",
    "details": [
      {
        "field": "query.city",
        "issue": "Field is required and must have at least 2 characters",
        "rejected_value": ""
      }
    ],
    "request_id": "4b6e7684-f3a7-4b71-a48a-6b4d3c332194",
    "service": "core_career_engine",
    "retryable": false
  }
}
```

### 2.1 Field Schema Definitions

| Field | Type | Description |
| :--- | :--- | :--- |
| `success` | `boolean` | **Always false** for error responses. |
| `error.code` | `string (ErrorCode)` | Stable, machine-readable classification enum. |
| `error.message` | `string` | Safe, human-readable summary of the error. |
| `error.details` | `array[ErrorDetail]` | Field-level validation or item-specific diagnostic issues. |
| `error.request_id` | `string (UUID)` | Distributed correlation UUID identifying the trace. |
| `error.service` | `string` | Originating service identifier (`core_career_engine`, `leadhunter`, etc.). |
| `error.retryable` | `boolean` | Indicates whether client should automatically retry with backoff. |

---

## 3. Standard Error Code Enumeration (`ErrorCode`)

| ErrorCode | HTTP Status | Retryable | Description |
| :--- | :--- | :--- | :--- |
| `BAD_REQUEST` | 400 | No | Malformed HTTP syntax, unparseable JSON, or illegal query parameter. |
| `VALIDATION_ERROR` | 422 | No | Pydantic model validation failure on request payload or query parameters. |
| `UNAUTHENTICATED` | 401 | No | Missing, expired, or malformed JWT or internal service token. |
| `UNAUTHORIZED` | 403 | No | Authenticated identity lacks required permission scope. |
| `RESOURCE_NOT_FOUND` | 404 | No | Requested entity UUID or URI route does not exist. |
| `RESOURCE_CONFLICT` | 409 | No | Unique constraint violation (e.g. duplicate email or application). |
| `RATE_LIMIT_EXCEEDED` | 429 | Yes | Token bucket or sliding window limit exceeded. Respect `Retry-After`. |
| `IDEMPOTENCY_VIOLATION` | 409 | No | Duplicate request submission detected on idempotent endpoint. |
| `INTERNAL_SERVER_ERROR`| 500 | Yes | Unhandled backend exception. Detailed logs stored internally. |
| `UPSTREAM_SERVICE_ERROR`| 502 | Yes | Satellite service returned 5xx or bad gateway response. |
| `SERVICE_UNAVAILABLE` | 503 | Yes | Database pool exhausted, Redis broker down, or circuit-breaker active. |
| `UPSTREAM_TIMEOUT` | 504 | Yes | Upstream API call exceeded execution budget (e.g. >5.0s). |

---

## 4. Information Leak Prevention Policy

> [!CAUTION]
> **Strict Security Boundary:** Under no circumstances should runtime stack traces, SQL syntax strings, database credentials, internal IP addresses, or secret API keys be returned in error responses.

1. **Production Masking:** All unhandled exceptions (`Exception`) caught by FastAPI exception handlers return generic message `"An unexpected server error occurred. Please try again later."` with a unique `request_id`.
2. **Correlation Log Tracing:** The exact stack trace and debug context is logged internally tagged with `request_id`. Developers search server logs using the returned `request_id` for diagnostics.
3. **Safe Field Values:** The `rejected_value` field in `ErrorDetail` must redact passwords, tokens, and personally identifiable information (PII).

