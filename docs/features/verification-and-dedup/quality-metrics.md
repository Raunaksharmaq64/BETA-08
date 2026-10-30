# Data Quality Intelligence & Metrics

## 1. Overview

The Data Quality Dashboard (`/quality`) provides real-time operational visibility into the integrity, freshness, and accuracy of all ingested career listings.

---

## 2. Core Metrics & Key Performance Indicators (KPIs)

- **Freshness Rate (%)**: Percentage of unsuppressed opportunities verified or observed within the past 7 days.
- **Verification Coverage (%)**: Percentage of opportunities that have received at least one verification check.
- **Confirmed Open Rate (%)**: Percentage of active opportunities verified open by employer APIs.
- **Link Unavailable Rate (%)**: Percentage of opportunities returning 404/dead URLs upon probing.

---

## 3. Operational Counts

- `total_opportunities`: Total active, unsuppressed opportunities in the platform.
- `fresh_opportunities`, `aging_opportunities`, `stale_opportunities`.
- `confirmed_open_count`, `confirmed_closed_count`, `unavailable_count`, `ambiguous_count`.
- `duplicate_candidates_count`: Proposed duplicate pairs awaiting administrative review.
- `confirmed_merges_count`: Auditable merges completed.
- `user_feedback_count`: Total reports submitted by candidates.

---

## 4. Per-Source Breakdown

For each registered job source, the metrics service computes:
- Provider name & type
- Ingestion enabled status
- Circuit breaker state (`CLOSED`, `OPEN`, `HALF_OPEN`)
- Total ingested listings
- Confirmed open count
- Freshness percentage

