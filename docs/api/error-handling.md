# API Error Handling & Status Codes

- **Title:** Error Handling & Fault Taxonomy
- **Purpose:** Standardizes error payload formats, fault classification, and client remediation messages.
- **Status:** APPROVED
- **Owner:** Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Unified Error Envelope
All error responses from the API must strictly conform to this envelope structure:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The payload failed schema validation.",
    "details": [
      {
        "field": "email",
        "issue": "Invalid email address format"
      }
    ]
  },
  "meta": {
    "request_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
    "timestamp": "2026-10-30T22:30:00Z"
  }
}
```

## 2. Standard Domain Error Codes
| Code | HTTP Status | Meaning |
| :--- | :--- | :--- |
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid Bearer token |
| `PERMISSION_DENIED` | 403 | User does not have access to resource |
| `RESOURCE_NOT_FOUND` | 404 | Entity ID not found in database |
| `VALIDATION_FAILED` | 422 | Pydantic validation failure |
| `RATE_LIMIT_EXCEEDED` | 429 | Request quota exhausted |
| `UPSTREAM_SERVICE_ERROR` | 502 | Satellite service (LeadHunter/Scraper) returned failure |
| `INTERNAL_SERVER_ERROR` | 500 | Unhandled server exception |

## 3. Open Questions & TBDs
- [TBD] Error masking in production vs. detailed diagnostic traces in development.

