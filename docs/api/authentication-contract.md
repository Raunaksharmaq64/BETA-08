# RIGHT FIT — Service Identity & Authentication Contract
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE GOVERNANCE  

---

## 1. Authentication Architecture

RIGHT FIT segregates authentication into two explicit tiers:
1. **User-to-Core Gateway Authentication:** JWT Bearer tokens issued to authenticated candidates, recruiters, and clients over HTTPS.
2. **Inter-Service Communication Authentication:** Private header-based shared secrets and HMAC signatures between Core Career Engine and internal satellite microservices (LeadHunter AI, Startup Intelligence).

```
[ Frontend Client ]
         │ (User JWT / Bearer)
         ▼
[ Core Career Engine (:8000) ]
         │
         ├─── (x-internal-service-key) ───► [ LeadHunter AI (:8001) ]
         │
         └─── (x-internal-service-key) ───► [ Startup Intelligence (:8002) ]
```

> [!WARNING]
> Direct frontend client communication with satellite services is strictly forbidden. All external requests must traverse the Core Career Engine gateway.

---

## 2. Inter-Service Request Headers (`ServiceAuthHeaders`)

All private HTTP requests dispatched from Core to satellite services must present the following headers:

| Header Name | Type | Description |
| :--- | :--- | :--- |
| `x-request-id` | `UUID string` | Distributed trace correlation ID generated at the gateway. |
| `x-service-source` | `ServiceName enum` | Name of the calling service (`core_engine`, `leadhunter`, etc.). |
| `x-internal-service-key` | `string` | Cryptographic pre-shared secret or signed internal token. |

### Example Header Payload

```http
GET /api/v1/leads/discovery/disc_lh_99182 HTTP/1.1
Host: service-leadhunter:8001
x-request-id: 7a9e223b-55c1-4ef8-a28b-b89280dfbb84
x-service-source: core_engine
x-internal-service-key: ${INTERNAL_SERVICE_SECRET}
Content-Type: application/json
```

---

## 3. Service Scope Authorization Model (`ServiceScope`)

Satellite microservices evaluate permissions based on assigned `ServiceScope` grants:

| Scope | Allowed Operations |
| :--- | :--- |
| `opportunities:read` | Read normalized and ingested opportunities. |
| `discovery:trigger` | Initiate asynchronous crawling or search scans. |
| `discovery:read` | Poll scan status and retrieve discovered opportunity batches. |
| `audit:read` | Retrieve deep website health diagnostic reports. |
| `outreach:trigger` | Schedule automated email or pitch dispatches. |
| `internal:all` | Full internal administrative rights across the service domain. |

---

## 4. Verification and Error Responses

When a service receives an internal call:
1. It validates the presence and accuracy of `x-internal-service-key`.
2. If invalid or missing, it immediately terminates with HTTP 401:
   ```json
   {
     "success": false,
     "error": {
       "code": "UNAUTHENTICATED",
       "message": "Invalid or missing internal service credentials",
       "request_id": "7a9e223b-55c1-4ef8-a28b-b89280dfbb84",
       "service": "leadhunter",
       "retryable": false
     }
   }
   ```
3. It evaluates if the calling identity has the required `ServiceScope`. If unauthorized, it responds with HTTP 403 `UNAUTHORIZED`.

