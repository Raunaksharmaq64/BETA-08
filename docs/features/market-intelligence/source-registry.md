# Source Registry & Data Provenance

## 1. Objective
All market metrics, compensation distributions, and skill demand numbers displayed in RIGHT FIT are grounded in audited, registered data sources. Opaque web scrapes, synthetic benchmarks, and unattributed claims are strictly prohibited.

## 2. Model Structure: `market_data_sources`
Each data pipeline feeding the market engine is registered in `market_data_sources` with explicit provenance attributes:
- `id` (UUID): Primary key.
- `source_key` (String, Unique): Machine-readable identifier (e.g. `direct_employer_ats`, `curated_tech_boards`, `regulatory_filings`, `community_audited_reports`).
- `name` (String): Human-readable name.
- `source_type` (String): Structural taxonomy enum:
  - `EMPLOYER_ATS`: Direct verified employer applicant tracking feeds (Greenhouse, Lever, Ashby, Workday).
  - `JOB_BOARD`: Curated technology career boards with verified employer identity.
  - `PUBLIC_GOVERNMENT`: Official regulatory and labor statistics filings (e.g. US H-1B disclosure, BLS, EU transparency).
  - `COMMUNITY_REPORTED`: Audited compensation reports submitted by verified practitioners with corroborating pay stubs or offer letters.
- `website_url` (String, Optional): Documentation or landing page.
- `ingestion_frequency` (String): Pipeline cadence (`REAL_TIME`, `DAILY`, `WEEKLY`).
- `reliability_score` (Float, 0.0 - 1.0): Audited empirical accuracy and completeness rating.
- `is_active` (Boolean): Operational toggle for data ingestion.

## 3. Seeded Baseline Registry
| Source Key | Source Name | Type | Frequency | Reliability |
| :--- | :--- | :--- | :--- | :--- |
| `direct_employer_ats` | Direct Employer ATS Feeds | `EMPLOYER_ATS` | `REAL_TIME` | 0.98 |
| `curated_tech_boards` | Curated Engineering Job Boards | `JOB_BOARD` | `DAILY` | 0.92 |
| `regulatory_filings` | Statutory Salary & Labor Filings | `PUBLIC_GOVERNMENT` | `WEEKLY` | 0.99 |
| `community_audited_reports` | Verified Practitioner Reports | `COMMUNITY_REPORTED`| `DAILY` | 0.88 |

## 4. Ingestion Lifecycle & Audit Trail
1. Raw vacancy or salary reports are ingested through registered connectors.
2. The connector stamps each record with `source_id` referencing `market_data_sources`.
3. If a source experiences degradation, high error rates, or data quality violations, administrators can set `is_active = false`, instantly omitting stale or compromised records from macro calculations.

