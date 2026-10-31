# Polymorphic Candidate Bookmarking

## 1. Unified Bookmark Model
Rather than forcing heterogeneous data models into a single rigid schema or requiring separate bookmark endpoints, RIGHT FIT implements polymorphic bookmark routing in `UnifiedOpportunityService`:

- `POST /api/v1/opportunities/{opportunity_type}/{opportunity_id}/save`
- `DELETE /api/v1/opportunities/{opportunity_type}/{opportunity_id}/save`
- `GET /api/v1/opportunities/saved/all`

## 2. Table Dispatch Mapping
- `JOB` $\rightarrow$ `SavedJobRecord` (`saved_jobs` table)
- `FREELANCE` $\rightarrow$ `SavedFreelanceOpportunityRecord` (`saved_freelance_opportunities` table)
- `STARTUP_PAIN_POINT` $\rightarrow$ `SavedStartupOpportunityRecord` (`saved_startup_opportunities` table)

## 3. Candidate Isolation and Idempotency
- Saving an already saved opportunity is idempotent and updates candidate `notes`.
- Deleting an unsaved opportunity returns 404.
- Candidate bookmarks are strictly scoped by `user_id`. One candidate saving an opportunity has zero impact on other candidates or the underlying opportunity state.

