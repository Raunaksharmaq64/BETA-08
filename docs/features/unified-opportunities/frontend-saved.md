# Next.js Unified Saved Opportunities UI Specification

## 1. Route: `/saved-opportunities`
Allows candidates to manage their unified bookmarks across all opportunity categories.

## 2. Features
- **Filter Tabs**: Filter bookmarks by `All Saved`, `Jobs`, `Freelance`, or `Startup Signals` with live count badges.
- **Card View**:
  - Displays original opportunity details normalized in `OpportunityEnvelope`.
  - Displays candidate's private notes attached during bookmarking.
  - Quick "Remove Bookmark" action with immediate optimistic local list removal.
  - "Visit / Apply" external link to proceed with outreach or formal application.
- **Empty State**: Friendly messaging with direct links to `/opportunities` to discover new leads.

