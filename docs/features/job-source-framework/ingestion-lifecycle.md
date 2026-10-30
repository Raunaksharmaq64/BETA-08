# Ingestion Lifecycle & Resilience Architecture

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

---

## 1. Overview

The ingestion lifecycle coordinates external data retrieval, resilience mechanisms, provenance tracking, and data deduplication. Ingestion is triggered either manually on-demand (via REST API) or systematically via background jobs.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Operator / Scheduler
    participant API as Ingestion API
    participant Orch as IngestionService
    participant Gate as Policy Gate & Circuit
    participant Rate as Rate Limiter
    participant Conn as Job Connector
    participant Ext as Upstream Board API
    participant Norm as Normalization Engine
    participant DB as Core PostgreSQL / SQLite

    Admin->>API: POST /api/v1/sources/{id}/ingest
    API->>Orch: run_ingestion(source_id, max_records, force)
    Orch->>Gate: Verify policy_status == ACTIVE
    alt Policy not ACTIVE
        Gate-->>Orch: Raise PermissionError (403)
        Orch->>DB: Log FAILED run (POLICY_BLOCKED)
        Orch-->>API: 403 Forbidden
    end
    Orch->>Gate: Check Circuit Breaker (CLOSED or HALF_OPEN?)
    alt Circuit is OPEN & not force
        Gate-->>Orch: Raise CircuitOpenException (503)
        Orch->>DB: Log FAILED run (CIRCUIT_OPEN)
        Orch-->>API: 503 Service Unavailable
    end
    Orch->>Rate: Acquire slot (rate_limit_per_minute)
    alt Rate limit exceeded
        Rate-->>Orch: Raise RateLimitExceededException (429)
        Orch->>DB: Log FAILED run (RATE_LIMIT_EXCEEDED)
        Orch-->>API: 429 Too Many Requests
    end
    Orch->>DB: Create RUNNING SourceRunLogRecord
    Orch->>Conn: fetch_jobs(source, max_records) with RetryPolicy
    Conn->>Ext: GET /v1/boards/{token}/jobs
    Ext-->>Conn: 200 OK (Raw JSON Listings)
    Conn-->>Orch: ConnectorFetchResult (RawJobPayload items)
    loop For each raw listing
        Orch->>DB: Upsert SourceObservationRecord (SHA-256)
        Orch->>Norm: normalize_record(raw_job, source)
        Norm-->>Orch: Canonical Opportunity Dict
        Orch->>DB: Check Deduplication & Upsert Canonical Opportunity
    end
    Orch->>Gate: Record Circuit Success (reset failures to 0)
    Orch->>DB: Update SourceRunLogRecord (SUCCESS, timing, metrics)
    Orch-->>API: IngestionTriggerResponse
    API-->>Admin: 200 OK
```

---

## 2. 3-State Circuit Breaker State Transitions

Implemented in `backend/app/services/resilience.py`:

| Current State | Event | Condition | Next State | Action |
|---|---|---|---|---|
| `CLOSED` | Success | Operation completes cleanly | `CLOSED` | `consecutive_failures = 0` |
| `CLOSED` | Transient Error | Consecutive failures < `threshold` (default 3) | `CLOSED` | Increment `consecutive_failures` |
| `CLOSED` | Transient Error | Consecutive failures >= `threshold` (3) | `OPEN` | Set `cooldown_until = now() + 60s` |
| `OPEN` | Check | `now() < cooldown_until` | `OPEN` | Block execution; raise `CircuitOpenException` |
| `OPEN` | Check | `now() >= cooldown_until` | `HALF_OPEN` | Allow single trial execution |
| `HALF_OPEN` | Success | Trial execution succeeds | `CLOSED` | Reset `consecutive_failures = 0`, clear cooldown |
| `HALF_OPEN` | Failure | Trial execution fails | `OPEN` | Trip immediately back to `OPEN`, reset cooldown |

---

## 3. Retry Policy with Exponential Backoff & Jitter

When querying upstream APIs, transient network errors, socket timeouts, and HTTP 429/5xx responses are retried using exponential backoff with randomized jitter:

$$\text{delay} = \min\left(\text{max\_delay}, \text{base\_delay} \times \text{factor}^{\text{attempt}}\right) + \text{uniform}(0, 0.25 \times \text{delay})$$

- **Non-transient errors:** HTTP 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), and validation errors are **never retried**. They fail fast to prevent resource wastage.

