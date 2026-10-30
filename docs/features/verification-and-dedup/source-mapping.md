# Source Mapping & Cross-Source Provenance

## 1. Overview

When opportunities from different sources are merged into a single canonical record, the original source records and URLs must not be lost. `OpportunitySourceMappingRecord` links multiple external source sightings to the primary canonical opportunity.

---

## 2. Data Model

`opportunity_source_mappings` contains:

- `canonical_opportunity_id`: UUID of the primary canonical opportunity record.
- `source_id`: UUID of the job source from which the listing originated.
- `external_job_id`: Upstream ATS requisition identifier.
- `original_url`: External application URL on that specific source board.
- `mapping_status`: `ACTIVE`, `REASSIGNED`, or `DETACHED`.
- `match_tier`: Confidence tier (`TIER_1_EXACT`, `TIER_2_STRONG`, etc.).
- `match_method`: Strategy used to link the source record.
- `confidence_score`: Float between 0.0 and 1.0.
- `merge_decision_id`: Foreign key referencing the `MergeDecisionRecord` when mappings were repointed.

---

## 3. Provenance Integrity

Candidates viewing a canonical opportunity can inspect every source from which the job was observed via `GET /api/v1/opportunities/{id}/mappings`. This ensures complete transparency regarding data origin, compensation disclosures, and application links.

