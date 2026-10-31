# Operational Playbook & Runbooks

## 1. Monitoring & Observability
- **Health Checks**:
  - `GET /health/live` — Core process liveness.
  - `GET /health/ready` — Database connection readiness.
  - `GET /api/v1/dashboard` — Metric reconciliation verification.
- **Circuit Breaker Status**:
  - Monitored via `service_availability.aggregation_state`.
  - Alert triggers when `aggregation_state != 'ALL_SERVICES_AVAILABLE'`.

## 2. Ingestion Outage Runbook
When a satellite service (e.g. LeadHunter or Startup Intelligence) experiences downtime:
1. **Immediate Reaction**: PyBreaker trips after 5 failures; requests fall back seamlessly to local DB cached records.
2. **Customer Experience**: The frontend surfaces the amber banner ("Partial Results Active — One or more satellites degraded"). Candidates can continue searching and saving existing opportunities uninterrupted.
3. **Recovery**:
   - Restart or restore satellite container.
   - Once satellite responds with 200 OK, PyBreaker enters `HALF_OPEN` and automatically resets to `CLOSED`.
   - Banner disappears; real-time synchronization resumes.

## 3. Database Maintenance
- Migrations are idempotent and run automatically on startup or via `migrate_phase11.py`.
- Indexes are maintained on `(user_id, created_at)` on all saved and feedback tables for sub-millisecond lookups.

