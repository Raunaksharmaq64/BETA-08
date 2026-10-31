# Search Architecture & Execution Guidelines

## 1. Multi-Dimensional Filter Execution

The search engine allows candidates to discover opportunities across several dimensions simultaneously:
- **Free-Text Keyword Search**: Matches across `title`, `company_name`, `description_clean`, `city`, and `required_skills_json`.
- **Role / Title**: Case-insensitive substring query on normalized title.
- **Company**: Case-insensitive substring query on company name.
- **Workplace Mode**: `REMOTE`, `HYBRID`, `ON_SITE`, and `UNKNOWN`.
- **Location**: Specific filtering by city, state, and country.
- **Compensation**: Threshold matching on `min_salary`, `max_salary`, and ISO `currency`.
- **Verification Status**: Filters by `OPEN_CONFIRMED`, `UNVERIFIED`, `CLOSED_CONFIRMED`, etc.
- **Freshness State**: Filters by `FRESH` (<24h), `RECENT` (<7d), `STALE`, etc.

---

## 2. Mandatory Non-Suppression Rule

In compliance with Phase 6 deduplication governance:
```sql
SELECT * FROM canonical_opportunities
WHERE is_suppressed = FALSE AND is_active = TRUE
```
Duplicate child records that have been merged into a primary canonical listing have `is_suppressed = TRUE`. The search engine strictly excludes suppressed records from all candidate-facing results to prevent duplicate spam and fragmented application links.

---

## 3. Cursor & Offset Pagination Standard

Pagination is enforced across all listing endpoints:
- Standard default: `page = 1`, `page_size = 20` (maximum 100).
- Response includes:
  - `total_count`: Total matches across database.
  - `page`: Current page number.
  - `page_size`: Records returned per page.
  - `total_pages`: Total calculated pages.
  - `has_next`: Boolean flag for subsequent page existence.
  - `has_prev`: Boolean flag for preceding page existence.

---

## 4. Upstream Source Outage Isolation

If an upstream source is currently unavailable:
- The search query does not fail or raise HTTP 500.
- Available database opportunities from all functional sources are returned immediately.
- `source_coverage` metadata alerts the client to partial coverage so candidates understand why expected listings from a specific provider may be absent.

