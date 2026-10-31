# Frontend Discovery & Candidate UI Guide

## 1. Overview & Screen Inventory

Phase 7 introduces 4 comprehensive candidate screens in `rightFIT/frontend`:

| Route | Component File | Description |
| :--- | :--- | :--- |
| `/search` | `src/app/(dashboard)/search/page.tsx` | Main Job Discovery with multi-filter sidebar, coverage banners, and card lists. |
| `/jobs/[jobId]` | `src/app/(dashboard)/jobs/[jobId]/page.tsx` | Full job posting detail with provenance and deep match breakdown. |
| `/saved-jobs` | `src/app/(dashboard)/saved-jobs/page.tsx` | Bookmarked opportunity management with private application notes. |
| `/saved-searches` | `src/app/(dashboard)/saved-searches/page.tsx` | Search subscriptions and alert cadence controls. |

---

## 2. Key UI Components

### A. Job Result Card
- **Header**: Job title (links to `/jobs/:id`), remote badge, workplace mode (`REMOTE`, `HYBRID`, `ON_SITE`).
- **Metadata**: Company name, location, source name, and ingestion date.
- **Badges**:
  - Verification Status (`✓ Open Confirmed`, `Unverified`, etc.)
  - Freshness State (`Fresh (<24h)`, `Recent (<7d)`, `Stale`)
  - Skill Fit Pill (`★ 85% Skill Fit`)
  - Eligibility Badge (`Meets Requirements`, `Needs Review`, `Unknown`)
- **Skill Overlap Preview**: Lists matched required skills and missing skills.
- **Actions**: One-click bookmark button, "Match Breakdown →", and direct external application link.

### B. Deep Match Breakdown Panel (`/jobs/[jobId]`)
- **Skill Fit Progress**: Visual percentage ring and matched skill evidence quotes from candidate's resume.
- **Missing Skills**: Clearly highlights skills required by the job that are missing from candidate profile.
- **Mandatory Eligibility Card**: Shows line-by-line verification for remote mode, minimum years of experience, and degrees.
- **Trust Basis**: Human-readable explanation of why the listing was verified and when it was last checked.
- **Private Notes**: Inline textarea enabling candidates to maintain application notes.

---

## 3. Navigation Integration

The global navbar (`src/components/layout/Navbar.tsx`) surfaces:
- **Find Jobs** (`/search`)
- **Saved Jobs** (`/saved-jobs`)
- **Alerts** (`/saved-searches`)
- **Candidate Profile** (`/profile`)
- **Resumes** (`/resumes`)
- **Job Sources** (`/sources`)
- **Data Quality** (`/quality`)

