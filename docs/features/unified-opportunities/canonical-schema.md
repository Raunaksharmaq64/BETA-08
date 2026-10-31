# Unified Opportunity Envelope v1.0 Schema Specification

## 1. Design Principles
The `OpportunityEnvelope` is a discriminated union providing a uniform shape for client consumers while encapsulating module-specific properties within `type_specific_payload`.

## 2. Common Envelope JSON Schema
```json
{
  "schema_version": "1.0",
  "opportunity_id": "string (UUID)",
  "opportunity_type": "JOB | FREELANCE | STARTUP_PAIN_POINT",
  "title": "string",
  "short_description": "string (max 280 chars)",
  "organization_name": "string",
  "source_service": "core | leadhunter | startup_intelligence",
  "source_name": "string",
  "source_record_id": "string",
  "source_url": "string | null",
  "location": "string",
  "is_remote": "boolean",
  "published_at": "ISO-8601 string",
  "first_discovered_at": "ISO-8601 string | null",
  "last_checked_at": "ISO-8601 string | null",
  "freshness_state": "FRESH | STALE | UNKNOWN",
  "classification_state": "string",
  "evidence_count": "integer",
  "is_saved": "boolean",
  "type_specific_payload": {}
}
```

## 3. Discriminated Payloads

### A. `JOB` Payload
- `employer`: String
- `job_role`: String
- `employment_type`: String (`FULL_TIME`, `PART_TIME`, `CONTRACT`)
- `required_skills`: List of Strings
- `salary_min`: Number or null
- `salary_max`: Number or null
- `salary_currency`: String
- `apply_url`: String
- `fit_score`: Float (0.0 to 1.0, based on candidate resume evidence)

### B. `FREELANCE` Payload
- `client_name`: String
- `service_category`: String (e.g. `Web Engineering`, `Performance`)
- `required_skills`: List of Strings
- `rating`: Float (Google Maps review score)
- `reviews_count`: Integer
- `is_broken_website`: Boolean
- `contact_evidence_status`: `OBSERVED | UNVERIFIED`
- `suggested_service`: String
- `phone`: String or null
- `email`: String or null

### C. `STARTUP_PAIN_POINT` Payload
- `startup_name`: String
- `domain`: String or null
- `category`: String
- `urgency_score`: Integer (1 to 10)
- `pain_point_description`: String
- `corroboration_count`: Integer
- `has_conflicting_evidence`: Boolean
- `ai_summary`: String or null
- `tech_stack`: List of Strings

