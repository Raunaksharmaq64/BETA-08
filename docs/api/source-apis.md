# Job Source Framework & Opportunities — REST API Reference

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

All endpoints are hosted under `/api/v1` and wrapped in the platform's canonical `StandardResponse[T]` envelope.

---

## 1. Source Administration Endpoints

### `GET /api/v1/sources`
Lists registered data sources with optional filters.

- **Query Parameters:**
  - `policy_status` (string, optional): Filter by `ACTIVE`, `DRAFT`, `PENDING_REVIEW`, `APPROVED`, etc.
  - `enabled` (boolean, optional): Filter by enabled state.
  - `provider` (string, optional): Filter by provider slug (e.g. `greenhouse`, `ashby`).
  - `skip` (int, default 0): Pagination offset.
  - `limit` (int, default 50, max 100): Page size.
- **Response:** `200 OK` with `StandardResponse[List[SourceResponse]]`.

### `POST /api/v1/sources`
Registers a new opportunity source. Initial status is always `DRAFT`.

- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
```json
{
  "source_key": "greenhouse-stripe",
  "display_name": "Stripe Greenhouse Board",
  "source_type": "ATS_JOB_BOARD",
  "provider": "greenhouse",
  "base_url": "https://boards-api.greenhouse.io/v1/boards/stripe/jobs",
  "rate_limit_per_minute": 60,
  "timeout_seconds": 30.0,
  "retry_max_attempts": 3,
  "notes": "Verified official Greenhouse JSON board feed."
}
```
- **Response:** `201 Created` with `StandardResponse[SourceResponse]`.

### `GET /api/v1/sources/{source_id}`
Retrieves configuration, circuit breaker condition, and failure counters for a specific source.

- **Response:** `200 OK` or `404 Not Found`.

### `PATCH /api/v1/sources/{source_id}`
Updates runtime configuration attributes.

- **Request Body:** `SourceUpdateRequest` (`display_name`, `base_url`, `rate_limit_per_minute`, `timeout_seconds`, `retry_max_attempts`, `enabled`, `notes`).
- **Response:** `200 OK`.

### `PATCH /api/v1/sources/{source_id}/policy`
Updates governance status (e.g. transitioning `DRAFT` -> `ACTIVE`). Appends reviewer notes to audit trail.

- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
```json
{
  "policy_status": "ACTIVE",
  "review_notes": "Terms of Service and rate limits verified. Approved for ingestion."
}
```
- **Response:** `200 OK`.

---

## 2. Ingestion Execution & Telemetry Endpoints

### `POST /api/v1/sources/{source_id}/ingest`
Triggers an ingestion run for the target source.

- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
```json
{
  "max_records": 50,
  "force": false
}
```
- **Status Responses:**
  - `200 OK`: Ingestion succeeded. Returns `IngestionTriggerResponse`.
  - `403 Forbidden`: Source policy gate is not `ACTIVE`.
  - `429 Too Many Requests`: Per-source sliding-window rate quota exhausted.
  - `503 Service Unavailable`: Circuit breaker is `OPEN`.
- **Response Data Payload:**
```json
{
  "run_id": "9a12c4e8-...",
  "source_id": "...",
  "source_key": "greenhouse-stripe",
  "status": "SUCCESS",
  "records_fetched": 45,
  "records_inserted": 12,
  "records_updated": 33,
  "duplicates_skipped": 0,
  "duration_seconds": 2.45,
  "circuit_state": "CLOSED",
  "message": "Ingestion run completed successfully in 2.45s"
}
```

### `GET /api/v1/sources/{source_id}/runs`
Retrieves execution run history, metrics, and error summaries.

- **Response:** `200 OK` with `StandardResponse[List[SourceRunLogResponse]]`.

### `GET /api/v1/sources/{source_id}/observations`
Retrieves raw observation payloads and provenance hashes (SHA-256).

- **Response:** `200 OK` with `StandardResponse[List[SourceObservationResponse]]`.

---

## 3. Opportunities Query Endpoints

### `GET /api/v1/opportunities`
Searches canonical career opportunities ingested from all sources.

- **Query Parameters:**
  - `search` (string, optional): Keyword search across title, company, and description.
  - `remote_only` (bool, optional): Filter for remote listings.
  - `employment_type` (string, optional): `FULL_TIME`, `CONTRACT`, `INTERNSHIP`, etc.
  - `department` (string, optional): Filter by department.
  - `skip` (int, default 0): Pagination offset.
  - `limit` (int, default 50, max 100): Page size.
- **Response:** `200 OK` with `StandardResponse[List[CanonicalOpportunityResponse]]`.

### `GET /api/v1/opportunities/{opportunity_id}`
Retrieves a single opportunity by UUID.

- **Response:** `200 OK` or `404 Not Found`.

