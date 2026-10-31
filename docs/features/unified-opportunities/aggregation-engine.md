# Unified Aggregation Engine Specification

## 1. Aggregation Lifecycle
`UnifiedOpportunityService.aggregate_opportunities` executes structured queries across three database tables:
1. `canonical_opportunities` (owned by Core)
2. `freelance_opportunities` (ingested by LeadHunter adapter)
3. `startup_opportunities` (ingested by Startup Intelligence adapter)

## 2. Multi-Source Filtering & Ordering
- **Type Selection**:
  - `ALL`: Queries all three sources, normalizes into `OpportunityEnvelope`, and combines results ordered chronologically by `first_discovered_at DESC`.
  - `JOB`: Exclusively queries `canonical_opportunities`.
  - `FREELANCE`: Exclusively queries `freelance_opportunities`.
  - `STARTUP_PAIN_POINT`: Exclusively queries `startup_opportunities` ordered by `urgency_score DESC, first_seen_at DESC`.
- **Search Terms**: Performs case-insensitive matching across `title` and `organization_name` / `business_name` / `startup_name`.
- **Category Filter**: Filters freelance leads and startup pain points by category.
- **Min Score Filter**: Applies urgency threshold to startup signals or rating threshold to freelance leads.

## 3. Candidate Bookmark Lookup
If an authenticated user request is provided, the aggregation engine performs a batch lookup of the user's saved IDs across `saved_jobs`, `saved_freelance_opportunities`, and `saved_startup_opportunities`. This allows the `is_saved` boolean on each envelope to be set without N+1 query overhead.

## 4. Metadata Payload
Every aggregation response returns:
```json
{
  "success": true,
  "data": [...],
  "page": 1,
  "per_page": 20,
  "total": 85,
  "counts_by_type": {
    "jobs": 40,
    "freelance": 25,
    "startup_pain_points": 20,
    "total": 85
  },
  "service_availability": {
    "aggregation_state": "ALL_SERVICES_AVAILABLE",
    "core": "AVAILABLE",
    "leadhunter": "AVAILABLE",
    "startup_intelligence": "AVAILABLE",
    "is_partial_results": false
  }
}
```

