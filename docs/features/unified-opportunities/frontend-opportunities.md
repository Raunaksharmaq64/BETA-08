# Next.js Unified Opportunities Pipeline UI Specification

## 1. Route: `/opportunities`
Provides the full, multi-source searchable feed aggregating Core Jobs, LeadHunter Freelance Leads, and Startup Intelligence Pain Points.

## 2. Interactive Controls
- **Type Filter Tabs**:
  - `All Opportunities`
  - `Full-Time Jobs`
  - `Freelance Leads`
  - `Startup Pain Points`
  - Each tab displays live counter pills returned from the aggregation API.
- **Search Bar**:
  - Searches keywords, titles, companies, and clients.
- **Category Filter Dropdown**:
  - Cross-module category mapping (`Performance`, `Engineering`, `AI`, `Database`, `Security`).
- **Cards Display**:
  - Normalized envelope fields (Title, Org, Location, Remote pill, Short description).
  - Type-specific payload details (e.g. Salary + Employment type for Jobs; Rating + Broken Site Alert for Freelance; Urgency Score + Corroboration for Startups).
  - Save / Unsave bookmark toggle with optimistic state.
  - Candidate Feedback modal trigger.
- **Feedback Modal**:
  - Allows selecting reason (`IRRELEVANT`, `ALREADY_APPLIED`, `INCORRECT_SKILLS`, `WRONG_LOCATION`, `OTHER`).
  - Submits asynchronously to `POST /api/v1/opportunities/{type}/{id}/feedback`.

