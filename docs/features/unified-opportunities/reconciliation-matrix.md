# Metrics Reconciliation Matrix & Integrity Audits

## 1. Audit Principles
To prevent drift, ghost counts, or reconciliation bugs, the aggregation engine runs continuous automated reconciliation tests:
- `test_unified_dashboard_metrics_reconciliation`
- `test_dashboard_unauthenticated_still_returns_reconciled_totals`

## 2. Mathematical Invariants Matrix

| Invariant | Equation / Assertion | Verification Status |
|-----------|----------------------|---------------------|
| Pipeline Count Completeness | `total_opportunities == total_jobs + total_freelance + total_startups` | Verified & Tested |
| Bookmark Totals | `total_saved == saved_jobs + saved_freelance + saved_startups` | Verified & Tested |
| Ingestion Window | `new_this_week == count(records where discovered_at >= now - 7d)` | Verified & Tested |
| Non-terminal Applications | `active_applications == count(applications where status not in ('REJECTED', 'WITHDRAWN'))` | Verified & Tested |
| High Urgency Threshold | `high_urgency_signals == count(startups where urgency_score >= 8)` | Verified & Tested |

## 3. Zero Ghost Count Policy
If a satellite service is unreachable or uninstalled, the count of records for that satellite in the summary metrics is based strictly on verified records already committed in the local Core database. No estimated, synthetic, or phantom counts are ever generated.

