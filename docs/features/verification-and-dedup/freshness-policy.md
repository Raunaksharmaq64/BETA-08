# Freshness Policy & Timestamps

## 1. Overview

Job board aggregators frequently conflate when a job was posted by an employer with when it was scraped by a bot. RIGHT FIT enforces complete decoupling of these lifecycle moments through independent timestamps.

---

## 2. Independent Timestamps

`CanonicalOpportunityRecord` maintains 11 independent timestamps:

1. `source_published_at`: When the employer originally published the job.
2. `source_updated_at`: When the employer made substantive edits to the posting.
3. `first_seen_at`: When RIGHT FIT first discovered and ingested the record.
4. `last_seen_at`: When RIGHT FIT last observed the listing present in an upstream feed.
5. `last_checked_at`: Most recent timestamp a verification probe was attempted.
6. `last_successful_check_at`: Most recent timestamp a check returned without network error.
7. `last_verified_at`: Most recent timestamp the listing status was confirmed valid.
8. `status_changed_at`: When the record transitioned between verification states.
9. `closed_at`: When the employer closed or removed the listing.
10. `expires_at`: Explicit application cutoff date provided by employer.
11. `expiry_derivation_notes`: Auditable notes explaining how expiration was determined.

---

## 3. Freshness Categorization

Freshness is computed dynamically based on elapsed time since observation:

- `FRESH`: Verified or observed within the past 7 days (`days_since_seen <= 7.0`).
- `AGING`: Observed between 8 and 21 days ago (`days_since_seen <= 21.0`).
- `STALE`: Older than 21 days without fresh upstream confirmation (`days_since_seen > 21.0`).
- `CHECK_OVERDUE`: Listing has not received a verification probe in over 14 days.
- `LINK_UNAVAILABLE`: Verification proved the link dead or 404.

---

## 4. Candidate-Facing Explanations

The platform avoids misleading statements like *"Posted 2 hours ago"* when the posting is actually weeks old. Instead, candidates see clear evidentiary explanations:

- **Confirmed Open**: *"Verified active with employer board API within the last check window."*
- **Recently Observed**: *"Observed on official employer career portal within the last 7 days."*
- **Listing Outdated**: *"No recent verification evidence recorded; listing may be closed."*

