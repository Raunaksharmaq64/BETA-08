# Operational Playbook: Market Intelligence

## 1. Routine Operational Cadence
1. **Daily Demand Snapshot Aggregations**:
   - A Celery background worker executes nightly at 02:00 UTC to compute rolling `7d`, `30d`, and `90d` demand snapshots across active opportunities.
   - Idempotent upserts update `skill_demand_snapshots` records without downtime.
2. **Weekly Source Reliability Audits**:
   - Data quality metrics compare total vacancies ingested vs rejected duplicates.
   - If anomaly thresholds exceed 15%, alerts notify engineering and the source is flagged for review.

## 2. Ingestion Anomaly Runbook
- **Symptom**: Sudden drop in demand counts for a major skill (e.g. Python drops by 80% overnight).
- **Diagnosis**:
  1. Inspect `market_data_sources` active flags (`SELECT source_key, is_active FROM market_data_sources;`).
  2. Verify ingestion connector health.
  3. Verify alias resolution rules (`SELECT * FROM skill_aliases WHERE alias = 'python';`).
- **Resolution**:
  - Re-run daily snapshot calculation job:
    ```bash
    python -m app.scripts.recalculate_market_snapshots --window 30d
    ```

## 3. Database Indexes for Performance
The following composite indexes ensure query execution stays below 50ms:
```sql
CREATE INDEX idx_skill_aliases_alias ON skill_aliases(alias);
CREATE INDEX idx_skills_tax_slug ON skills_taxonomy(slug);
CREATE INDEX idx_demand_snap_window ON skill_demand_snapshots(time_window, role_category);
CREATE INDEX idx_comp_obs_filters ON compensation_observations(compensation_type, currency, role_category);
CREATE INDEX idx_candidate_skill_gaps ON candidate_skill_gap_recommendations(user_id, target_role);
```

