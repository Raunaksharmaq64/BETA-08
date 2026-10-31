# Candidate Saved Jobs & Private Notes

## 1. Overview & Data Isolation

Candidates can bookmark career opportunities for ongoing tracking and attach private notes (e.g. referral names, interview stages, or compensation expectations).
Saved job records are isolated to the authenticated candidate's user ID and cascaded on account deletion.

---

## 2. Data Model

The `saved_jobs` table stores candidate bookmarks:
- `id`: UUID primary key
- `user_id`: Foreign key to `users.id` (CASCADE)
- `opportunity_id`: Foreign key to `canonical_opportunities.id` (CASCADE)
- `notes`: Optional candidate text notes (up to 1,000 characters)
- `created_at`: Timezone-aware UTC timestamp

---

## 3. Supported Operations

| Action | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Bookmark Job** | `POST` | `/api/v1/saved-jobs` | Saves job and initializes optional notes. Duplicate calls idempotently update notes. |
| **List Saved Jobs** | `GET` | `/api/v1/saved-jobs` | Returns all bookmarked jobs with current verification and freshness statuses. |
| **Update Notes** | `PATCH` | `/api/v1/saved-jobs/{id}` | Updates private notes without altering save date. |
| **Unsave Job** | `DELETE` | `/api/v1/saved-jobs/{id}` | Removes bookmark by saved job ID or opportunity ID. |

---

## 4. Freshness & Closure Alerts on Saved Jobs

When viewing `/saved-jobs`, the application displays real-time verification badges. If a saved job has closed since the candidate bookmarked it (`CLOSED_CONFIRMED`), the card immediately updates its status to alert the candidate.

