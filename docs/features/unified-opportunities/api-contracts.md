# OpenAPI v1 REST Contracts & Endpoint Specifications

## 1. Endpoints Overview

| Method | Path | Summary | Auth Required |
|--------|------|---------|---------------|
| `GET` | `/api/v1/dashboard` | Reconciled metrics and recent discoveries | Optional (Personalized if present) |
| `GET` | `/api/v1/opportunities/all` | Unified multi-source opportunity aggregation | Optional (Annotates `is_saved` if present) |
| `GET` | `/api/v1/opportunities/saved/all` | Unified bookmarks across all types | Required (Bearer / HttpOnly Cookie) |
| `POST`| `/api/v1/opportunities/{type}/{id}/save` | Polymorphic bookmark creation / update | Required |
| `DELETE`| `/api/v1/opportunities/{type}/{id}/save` | Polymorphic bookmark removal | Required |
| `POST`| `/api/v1/opportunities/{type}/{id}/feedback` | Candidate relevance feedback recording | Required |

---

## 2. Request / Response Contracts

### `GET /api/v1/dashboard`
**Response:**
```json
{
  "success": true,
  "data": {
    "summary_metrics": {
      "total_opportunities": 85,
      "total_jobs": 40,
      "total_freelance": 25,
      "total_startups": 20,
      "total_saved": 8,
      "active_applications": 3,
      "high_urgency_signals": 7,
      "new_this_week": 14
    },
    "source_health": {
      "core_career_engine": "HEALTHY",
      "leadhunter_satellite": "HEALTHY",
      "startup_intelligence_satellite": "HEALTHY",
      "all_systems_operational": true
    },
    "recent_opportunities": [...]
  }
}
```

### `GET /api/v1/opportunities/all`
**Query Parameters:**
`type` (`ALL|JOB|FREELANCE|STARTUP_PAIN_POINT`), `search`, `category`, `source`, `min_score`, `page`, `per_page`

**Response:**
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

### `POST /api/v1/opportunities/{type}/{id}/save`
**Request Body:**
```json
{
  "notes": "Candidate's private bookmark notes"
}
```

### `POST /api/v1/opportunities/{type}/{id}/feedback`
**Request Body:**
```json
{
  "feedback_category": "IRRELEVANT | ALREADY_APPLIED | INCORRECT_SKILLS | WRONG_LOCATION | OTHER",
  "explanation": "Optional detailed reasoning"
}
```

