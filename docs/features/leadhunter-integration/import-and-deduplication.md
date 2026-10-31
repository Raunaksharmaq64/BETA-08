# Import and Multi-Signal Deduplication

## Overview
When LeadHunter returns batches of leads, Core performs idempotent import and deduplication to avoid creating duplicate opportunities.

## Multi-Signal Matching Sequence
```mermaid
flowchart TD
    Lead[Incoming Lead] --> S1{Does place_id match existing record?}
    S1 -->|Yes| Update[Update Metadata & Timestamps]
    S1 -->|No| S2{Does leadhunter_lead_id match?}
    S2 -->|Yes| Update
    S2 -->|No| S3{Does normalized Business Name + City match?}
    S3 -->|Yes| Update
    S3 -->|No| Insert[Insert New FreelanceOpportunityRecord]
```

## Update vs Insert Behavior
- **Match Found**: System refreshes `last_verified_at`, updates `is_broken_website`, and appends newly discovered contact channels to `contact_evidence` without replacing historical entries.
- **Ambiguous Match**: If business name matches but phone or website differs, classification is flagged as `REVIEW_REQUIRED`.

