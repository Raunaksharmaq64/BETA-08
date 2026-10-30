# Source Registry & Administration

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

---

## 1. Concept & Requirements

The **Source Registry** manages the registration, configuration, and runtime health of all opportunity ingestion providers. It guarantees that no source can be queried without explicit registration and administrative configuration.

### Core Objectives
1. **Administrative Control:** Every feed is an entity in the `job_sources` table.
2. **Safe Credential Referencing:** Secret keys or tokens are never stored in plaintext within source records; only references to secrets managers/vaults (`credential_reference`) are allowed.
3. **Per-Source Rate and Timeout Quotas:** Configurable `rate_limit_per_minute` (1-1200), `timeout_seconds` (1-120s), and `retry_max_attempts` (0-10).
4. **State Auditing:** All modifications maintain UTC timestamps and policy audit histories.

---

## 2. Database Schema (`job_sources`)

| Column Name | Type | Modifiers | Description |
|---|---|---|---|
| `id` | `VARCHAR(36)` | PK, UUID | Unique internal source ID. |
| `source_key` | `VARCHAR(100)` | UNIQUE, INDEX, NOT NULL | Slug identifier (e.g. `greenhouse-stripe`). |
| `display_name` | `VARCHAR(150)` | NOT NULL | Human-readable name. |
| `source_type` | `VARCHAR(30)` | NOT NULL | `ATS_JOB_BOARD`, `OFFICIAL_API`, `PERMITTED_FEED`. |
| `provider` | `VARCHAR(50)` | NOT NULL | Connector adapter slug (`greenhouse`, `ashby`, `synthetic`). |
| `base_url` | `VARCHAR(500)` | NOT NULL | Base endpoint or board URL. |
| `integration_method`| `VARCHAR(30)` | NOT NULL | `REST_API`, `PULL_FEED`, `WEBHOOK`. |
| `auth_type` | `VARCHAR(30)` | NOT NULL | `NONE_PUBLIC`, `API_KEY`, `BEARER_TOKEN`, `OAUTH2`. |
| `credential_reference`| `VARCHAR(255)` | NULL | Reference key for secrets vault. |
| `enabled` | `BOOLEAN` | DEFAULT TRUE | Master kill switch for source. |
| `policy_status` | `VARCHAR(30)` | DEFAULT 'DRAFT' | Governance lifecycle gate. |
| `policy_decision_json`| `JSON` | DEFAULT `{}` | Complete review history and audit notes. |
| `rate_limit_per_minute`| `INTEGER` | DEFAULT 60 | Maximum calls per 60-second window. |
| `timeout_seconds` | `FLOAT` | DEFAULT 30.0 | Request timeout limit. |
| `retry_max_attempts`| `INTEGER` | DEFAULT 3 | Exponential retry attempts. |
| `circuit_breaker_state`| `VARCHAR(20)` | DEFAULT 'CLOSED' | `CLOSED`, `OPEN`, `HALF_OPEN`. |
| `consecutive_failures`| `INTEGER` | DEFAULT 0 | Counter for circuit tripping. |
| `last_failure_at` | `TIMESTAMP WITH TZ`| NULL | Timestamp of last recorded failure. |
| `last_success_at` | `TIMESTAMP WITH TZ`| NULL | Timestamp of last recorded success. |
| `cooldown_until` | `TIMESTAMP WITH TZ`| NULL | Timestamp when circuit cooldown expires. |
| `created_at` | `TIMESTAMP WITH TZ`| NOT NULL | UTC creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TZ`| NOT NULL | UTC last modification timestamp. |

---

## 3. Administrative REST Endpoints

### 1. Register Source
- **Method:** `POST /api/v1/sources`
- **Access:** Authenticated Admin / Manager
- **Payload:**
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
- **Response Status:** `201 Created`
- **Default Policy Status:** `DRAFT` (requires policy review to activate).

### 2. List Registered Sources
- **Method:** `GET /api/v1/sources?policy_status=ACTIVE&enabled=true`
- **Access:** Public or Authenticated

### 3. Update Configuration
- **Method:** `PATCH /api/v1/sources/{source_id}`
- **Payload:** Partial updates to `display_name`, `base_url`, `rate_limit_per_minute`, `timeout_seconds`, `retry_max_attempts`, or `enabled`.
