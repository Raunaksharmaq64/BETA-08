# Save and Apply Tracking

## Overview
RIGHT FIT provides friction-free transition from verified discovery to active pipeline management. Candidates can save opportunities with a single click and track the full external application lifecycle.

## Architectural Flow

```mermaid
sequenceDiagram
    autonumber
    actor Candidate
    participant UI as Next.js Frontend
    participant Core as Core Career Engine
    participant DB as Core PostgreSQL / SQLite
    participant ATS as Employer ATS / External URL

    Candidate->>UI: Click "Save Job"
    UI->>Core: POST /api/v1/applications (opportunity_id)
    Core->>DB: Check canonical opportunity exists & verified
    Core->>DB: Insert ApplicationRecord (status="SAVED")
    Core-->>UI: 201 Created (Application details)

    Candidate->>UI: Click "Apply Now"
    UI->>Core: POST /api/v1/applications/{id}/apply-intent
    Core->>DB: Update status to "APPLYING"
    UI->>ATS: Open outbound application URL in new tab
    UI-->>Candidate: Display confirmation prompt ("Did you submit your application?")

    Candidate->>UI: Clicks "Yes, Application Submitted"
    UI->>Core: POST /api/v1/applications/{id}/confirm-applied
    Core->>DB: Transition status to "APPLIED", record applied_at=UTC
    Core->>DB: Insert ApplicationStatusHistoryRecord
    Core-->>UI: 200 OK
```

## Key Capabilities
1. **Deduplication Check**: Ensures candidate does not accidentally create duplicate active applications for the same canonical opportunity.
2. **Provenance Preservation**: Links application to source observation, ATS portal identifier, and original listing snapshot.
3. **Outbound Intent Logging**: Emits audit telemetry when candidate leaves the platform to submit on third-party ATS (Workday, Greenhouse, Lever, etc.).
4. **Offline / Custom Opportunity Support**: Allows candidate to manually log applications for private leads or unlisted positions (`canonical_opportunity_id` can be null).

