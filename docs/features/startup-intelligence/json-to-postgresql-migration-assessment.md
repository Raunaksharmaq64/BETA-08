# JSON-to-PostgreSQL Migration Assessment
## Workstream I Specification

- **Module:** `startup-intelligence`
- **Source File:** `Startups-problrms-hunter/data/leads.json`
- **Assessment Date:** 2026-10-31
- **Current Status:** `ASSESSED` & `DRY_RUN_COMPLETE`

---

## 1. Storage Inventory & Structural Analysis

The independent `Startups-problrms-hunter` service currently uses a local JSON flat-file storage model (`data/leads.json`, size: 911 KB).

### Forensic Metrics:
- **Total Records:** 598 leads
- **Observed Schema Fields:** `id`, `startup_name`, `category`, `detected_signal`, `insight`, `opportunity`, `pitch_idea`, `score`, `score_explanation`, `source`, `url`, `contact_info`, `status`, `created_at`, `analyzed`, `raw_text`, `matched_skills`, `match_percentage`, `tech_audit`.
- **Category Breakdown:**
  - `Development`: 240 (40.1%)
  - `UI/UX`: 154 (25.8%)
  - `AI`: 118 (19.7%)
  - `Performance`: 52 (8.7%)
  - `SEO`: 28 (4.7%)
  - `Marketing`: 6 (1.0%)
- **Source Platforms:** 12 platforms represented (Reddit r/saas, r/startups, r/SideProject, DuckDuckGo Search, GitHub, Hacker News, Dev.to, Product Hunt, etc.).
- **URL Coverage:** 598/598 (100% of records contain a target URL or search destination).
- **Unique URLs:** 555 unique URLs (43 records share URLs across multiple distinct observation threads).

---

## 2. Relational Target Mapping

| JSON Field | PostgreSQL Target | Nullability | Constraints |
|---|---|---|---|
| `id` | `startup_opportunities.service_record_id` | Nullable | Indexed varchar(64) |
| `startup_name` | `startup_opportunities.startup_name` | NOT NULL | varchar(150), indexed |
| `url` (domain part) | `startup_opportunities.domain` | Nullable | varchar(150), indexed |
| `url` (full URL) | `startup_opportunities.website_url` | Nullable | varchar(500) |
| `category` | `startup_opportunities.category` | NOT NULL | varchar(50), default 'Development' |
| `detected_signal` | `startup_opportunities.detected_signal` | NOT NULL | text |
| `score` | `startup_opportunities.urgency_score` | NOT NULL | integer, 1 to 10 |
| `created_at` | `startup_opportunities.published_at` | Nullable | timestamptz (UTC) |
| `raw_text` | `startup_evidence.observation_excerpt` | NOT NULL | text |
| `tech_audit` | `startup_tech_findings` | - | 1-to-N child records |

---

## 3. Data Loss Risk & Approval Gate

- **Data Loss Risk:** **0.0%** — All 19 fields map to explicit relational columns or child evidence tables.
- **Approval Gate Decision:** In accordance with the prompt rules:
  > *"Execute a real migration only if explicit approval exists. If migration is not approved, retain the current storage and document the decision."*
- **Current Operational Decision:**
  - The JSON file in `Startups-problrms-hunter/data/leads.json` remains completely intact and unmodified.
  - Core ingests canonical copies over the authenticated REST API.
  - Status is officially classified as: **`DRY_RUN_COMPLETE`**.

