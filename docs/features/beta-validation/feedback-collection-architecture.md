# Beta Feedback Collection & Triage Architecture

**Document ID:** RF-SPEC-1404  
**Phase:** 14 — Beta Testing & Product Validation  
**Status:** Approved  

---

## 1. Architecture Overview

The Beta Feedback subsystem provides an end-to-end mechanism for capturing, classifying, prioritizing, and resolving user-observed defects and experience friction.

```mermaid
flowchart TD
    UI["Feedback Form (Frontend /beta/feedback)"] -->|POST /api/v1/beta/feedback| Router["Beta Router (endpoints/beta.py)"]
    Router --> Svc["BetaValidationService"]
    Svc --> DB[("beta_feedback Table")]
    Svc --> AutoTriage{"Severity & Category Analyzer"}

    AutoTriage -->|CRITICAL / HIGH| Alert["Engineering On-Call Alert (SLA < 2h)"]
    AutoTriage -->|MEDIUM / LOW| Backlog["Weekly Triage Backlog (SLA < 24-72h)"]

    Engineer["Triage Engineer"] -->|PATCH /api/v1/beta/feedback/{id}/triage| Svc
    Svc --> DBUpdate["Update triage_status & resolution_notes"]
```

---

## 2. Category Taxonomy & Severity Rubric

### Feedback Categories
- `BUG`: Functional defects, crashes, 500 errors, or unexpected UI failures.
- `DATA_QUALITY`: Stale job postings, broken external URLs, expired listings, or incorrect compensation numbers.
- `UX_CONFUSION`: Unclear copy, ambiguous filter controls, confusing error messages, or unintuitive workflow steps.
- `OPPORTUNITY_RELEVANCE`: Inaccurate fit scores, irrelevant recommendations, or mismatched skill requirements.
- `FEATURE_REQUEST`: Candidate enhancement suggestions for future post-beta phases.
- `OTHER`: General user feedback and uncategorized beta observations.

### Severity Rubric & SLA Targets

| Severity | Criteria | Response SLA | Resolution Target |
|:---|:---|:---|:---|
| **CRITICAL** | Total workflow block, data corruption, auth outage, or security vulnerability | &lt; 2 Hours | &lt; 8 Hours |
| **HIGH** | Major feature impaired (e.g., job search failing, resume upload broken) with workaround | &lt; 8 Hours | &lt; 24 Hours |
| **MEDIUM** | Moderate defect, cosmetic flaw causing confusion, minor relevance drift | &lt; 24 Hours | &lt; 3 Days |
| **LOW** | Minor suggestion, typo, cosmetic styling inconsistency | &lt; 72 Hours | Scheduled in Sprint |

---

## 3. Database Schema

```sql
CREATE TABLE beta_feedback (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    category VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    expected_behavior TEXT NULL,
    opportunity_id VARCHAR(64) NULL,
    metadata_json JSONB NULL,
    triage_status VARCHAR(32) NOT NULL DEFAULT 'NEW',
    resolution_notes TEXT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### Supported Triage Status Transitions:
`NEW` &rarr; `TRIAGED` &rarr; `IN_PROGRESS` &rarr; `RESOLVED` &rarr; `CLOSED`

