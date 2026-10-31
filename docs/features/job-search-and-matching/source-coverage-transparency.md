# Source Coverage & Partial Results Transparency

## 1. Problem Statement

In job aggregators and intelligence platforms, upstream ATS feeds or APIs (e.g. Greenhouse, Ashby, Lever) periodically suffer outages, network timeouts, or rate-limiting circuit breaker trips.

When a candidate searches for a job and sees zero results, they traditionally cannot tell whether:
1. No such job exists in the industry, or
2. The platform's ingestion connectors for major employers are temporarily offline.

---

## 2. Platform Solution: Coverage Metadata

Every job search API response includes a dedicated `source_coverage` object:
```json
{
  "source_coverage": {
    "total_configured_sources": 4,
    "healthy_sources_count": 3,
    "degraded_sources_count": 1,
    "is_partial_results": true,
    "coverage_details": [
      {
        "source_key": "greenhouse_core",
        "display_name": "Greenhouse ATS Adapter",
        "status": "ACTIVE",
        "records_count": 142
      },
      {
        "source_key": "ashby_core",
        "display_name": "Ashby Ingestion Feed",
        "status": "OUTAGE",
        "records_count": 0,
        "outage_reason": "Upstream connector circuit breaker tripped after 3 consecutive failures."
      }
    ]
  }
}
```

---

## 3. Candidate Presentation

When `is_partial_results` is `true`, the frontend dynamically displays an amber notice banner:
> **Notice: Partial Upstream Source Coverage**
> One or more upstream source connectors (1 of 4) are currently degraded or in circuit breaker cooldown. Zero matches on certain queries may reflect upstream provider outages rather than a lack of market openings.

