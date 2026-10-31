# Next.js Unified Dashboard UI Specification

## 1. Route: `/dashboard`
The Unified Dashboard serves as the command center for candidates, summarizing pipeline activity, system status, and recommended leads.

## 2. Layout & Components
- **Header**: Quick title, description, and direct links to `/opportunities` and `/saved-opportunities`.
- **System Health Pill**:
  - Displays real-time status of Core Engine, LeadHunter Satellite, and Startup Intelligence Satellite.
  - Automatically renders an alert if satellite services degrade.
- **KPI Metrics Grid**:
  - Reconciled Total Pipeline
  - Full-Time Canonical Jobs
  - Freelance & Local Opportunities
  - Startup Signals & Pain Points
  - Saved Bookmarks
  - Active CRM Applications
  - Urgent Founder Signals ($\ge 8/10$)
  - Ingested This Week
- **Recent Discoveries Feed**:
  - Card-based responsive grid showing latest discoveries across all three types.
  - Distinct badge accents (Blue for Jobs, Emerald for Freelance, Purple for Startups).
  - One-click bookmark toggle with optimistic UI updates.
  - External link to ATS application or original evidence source.

