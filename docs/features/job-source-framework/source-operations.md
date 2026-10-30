# Source Operations & Observability Runbook

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

---

## 1. Source Run Metrics (`source_run_logs`)

Every ingestion execution logs structured operational telemetry in `source_run_logs`:

| Metric Field | Description | Target SLA |
|---|---|---|
| `records_fetched` | Total raw items returned by provider. | Monitored for empty feed anomalies. |
| `records_normalized` | Total items successfully transformed to canonical schema. | > 99% normalization yield. |
| `records_inserted` | New canonical opportunities created. | Tracked for freshness volume. |
| `records_updated` | Existing opportunities whose `last_seen_at` was bumped. | Stable active inventory metric. |
| `duplicates_skipped` | Cross-source or duplicate listings suppressed. | Monitored to detect feed overlaps. |
| `duration_seconds` | Total ingestion elapsed time. | < 15.0s per 50 records. |
| `error_category` | High-level failure classification. | Alerting trigger on persistent errors. |
| `safe_error_summary` | Sanitized error message (secrets stripped). | Auditable incident diagnosis. |

---

## 2. Common Operational Runbooks

### Runbook A: Investigating a Circuit Breaker in `OPEN` State
1. **Symptom:** API returns HTTP `503 Service Unavailable` with message `"Circuit breaker is OPEN"`.
2. **Diagnosis:**
   - Query run logs: `GET /api/v1/sources/{source_id}/runs`.
   - Inspect the most recent `FAILED` run log records.
   - Common causes: upstream ATS maintenance, board URL typo, temporary network outage.
3. **Remediation:**
   - Wait for `cooldown_until` timestamp to elapse. The circuit will transition to `HALF_OPEN`.
   - Alternatively, test a trial run via `POST /api/v1/sources/{source_id}/ingest` with `"force": true`.
   - If the upstream endpoint changed, update `base_url` using `PATCH /api/v1/sources/{source_id}`.

### Runbook B: Handling Upstream Rate Limit Warnings (`429`)
1. **Symptom:** Ingestion run fails with `RATE_LIMIT_EXCEEDED` or provider returns HTTP 429.
2. **Remediation:**
   - Reduce source request frequency or increase sliding-window limit in database:
     `PATCH /api/v1/sources/{source_id}` with `{"rate_limit_per_minute": 30}`.
   - The sliding-window rate limiter will enforce the lower ceiling automatically.

### Runbook C: Retiring or Pausing a Deprecated Board
1. **Action:**
   - Send `PATCH /api/v1/sources/{source_id}/policy` with `{"policy_status": "PAUSED", "review_notes": "Company migrated ATS from Greenhouse to Workday"}`.
   - All subsequent ingestion runs will be cleanly rejected by the Policy Gate.

