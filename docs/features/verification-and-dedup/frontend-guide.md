# Phase 6 Frontend Guide

## 1. Overview

Phase 6 introduces dedicated user-facing and administrative screens in the Next.js frontend (`rightFIT/frontend`):

1. **Opportunities Discovery View (`/opportunities`)**:
   - Freshness badges (*"Status confirmed open"*, *"Recently observed"*, *"Listing may be outdated"*).
   - "Report Issue" action button and interactive feedback modal.
   - Clickable links to individual opportunity verification detail pages.
   - Suppression filter excluding closed and merged duplicate listings by default.

2. **Opportunity Verification Detail View (`/opportunities/[opportunityId]`)**:
   - Comprehensive independent timestamps panel (10 distinct timestamps).
   - "Verify Status Now" on-demand verification execution.
   - Immutable verification evidence audit trail showing HTTP status, provider signals, and timings.
   - Source provenance and requisition mappings table.

3. **Data Quality Dashboard (`/quality`)**:
   - 4 Top KPI cards: Freshness Rate, Verification Coverage, Confirmed Open Rate, Link Unavailable Rate.
   - Opportunity status distribution metrics.
   - Source ingestion and health breakdown table with circuit breaker status indicators.

4. **Duplicate Review Workbench (`/quality/duplicates`)**:
   - Filter tabs: Proposed, Confirmed Merges, All.
   - "Run Duplicate Detection" automated scanning trigger.
   - Side-by-side card comparison between primary and duplicate candidate.
   - Match tier badges (Tier 1 Exact, Tier 2 Strong, Tier 3 Probable).
   - Confidence percentage and match evidence criteria preview.
   - "Merge into Primary" confirmation modal with auditable reason logging.

