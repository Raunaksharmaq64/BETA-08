# Query and Filtering Mechanics

## 1. Parameters Specification

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | String | `"ALL"` | Target opportunity type: `ALL`, `JOB`, `FREELANCE`, `STARTUP_PAIN_POINT` |
| `search` | String | `null` | Keyword matching against title, company, and organization name |
| `category`| String | `null` | Module category (e.g. `Performance`, `Engineering`, `AI`) |
| `source` | String | `null` | Origin source connector or platform |
| `min_score`| Integer| `null` | Minimum rating (1-5) or urgency score (1-10) |
| `page` | Integer | `1` | Pagination page number |
| `per_page`| Integer | `20` | Items per page (max 100) |

## 2. Cross-Source Normalization
Because each module stores data with specialized terminology, the aggregation layer maps query parameters appropriately:
- When filtering by `category`:
  - Freelance maps to `FreelanceOpportunityRecord.service_category`
  - Startup Intelligence maps to `StartupOpportunityRecord.category`
  - Jobs pass through or match department.
- When filtering by `source`:
  - Freelance maps to `FreelanceOpportunityRecord.source`
  - Startup Intelligence maps to `StartupOpportunityRecord.primary_source`
  - Jobs map to `CanonicalOpportunityRecord.company_name` or `JobSourceRecord.name`.
- When searching by `search`:
  - Canonical Jobs: `title.ilike('%s%') OR company_name.ilike('%s%')`
  - Freelance: `opportunity_title.ilike('%s%') OR business_name.ilike('%s%')`
  - Startups: `detected_signal.ilike('%s%') OR startup_name.ilike('%s%')`

