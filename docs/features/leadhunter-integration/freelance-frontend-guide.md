# Freelance Opportunity Frontend Guide

## Routes & Screens

### 1. `/freelance` (Dashboard & Discovery Catalog)
- Real-time KPI summaries: Total Opportunities, High-Fit Opportunities, Broken Websites.
- Google Maps search scan launcher (Category + City).
- Classification state filters (`VERIFIED_OPPORTUNITY`, `POTENTIAL_FREELANCE_OPPORTUNITY`, `DISCOVERED_LEAD`).
- Opportunity cards with broken website badges, required skills, and match scores.

### 2. `/freelance/[opportunityId]` (Detail & Evidence Workbench)
- Technical health breakdown (DNS, SSL, HTTP status).
- Contact Evidence Ledger showing audited channels with status badges (`VERIFIED`, `OBSERVED`, `INVALID`).
- Discovery source provenance links.

### 3. `/freelance/[opportunityId]/draft` (Outreach Workbench)
- Personalized draft editor with anti-hallucination warning banner.
- Real-time approval state badge (`DRAFT`, `PENDING_REVIEW`, `APPROVED`, `SENT`).
- Invalidation protection: editing an approved draft immediately resets its status.

### 4. `/freelance/saved` (Saved Bookmarks)
- Private list of candidate-curated freelance prospective clients.

### 5. `/freelance/outreach` (Outreach Activity & Delivery History)
- Audit log of dispatched messages and delivery status.
- Self-service recipient suppression management form.

