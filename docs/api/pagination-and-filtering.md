# Pagination, Sorting & Filtering Standards

- **Title:** Query Parameter Standards for Collections
- **Purpose:** Establishes consistent pagination envelopes, sorting keys, and filter expressions.
- **Status:** APPROVED
- **Owner:** Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Pagination Envelope
List endpoints must return data wrapped with pagination metadata:
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "total_records": 1420,
    "limit": 20,
    "offset": 40,
    "has_next": true,
    "has_prev": true
  },
  "meta": {
    "request_id": "b1a79f53-b295-44ee-bce8-ec2b55f9cfb8",
    "timestamp": "2026-10-30T22:35:00Z"
  }
}
```

## 2. Parameter Conventions
- `limit`: Integer (Default: 20, Min: 1, Max: 100).
- `offset`: Integer (Default: 0, Min: 0).
- `sort_by`: Field name (e.g., `created_at`, `fit_score`, `salary_max`).
- `order`: `asc` or `desc` (Default: `desc`).

## 3. Filter Conventions
- Equality: `?status=applied&is_remote=true`
- Range queries: `?min_salary=120000&max_salary=180000`
- Multi-select values: comma-separated list (`?skills=python,fastapi,react`)

## 4. Open Questions & TBDs
- [TBD] Cursor-based keyset pagination for high-throughput continuous feeds.

