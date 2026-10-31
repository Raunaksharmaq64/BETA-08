# Startup Frontend User Guide
## Workstream J & N Specification

- **Module:** `startup-intelligence`
- **Application Root:** `rightFIT/frontend`
- **Design Framework:** Next.js 16 (App Router), Tailwind CSS

---

## 1. Routes & Screens Catalog

| Route | Page Component | Key Functionality |
|---|---|---|
| `/startups` | `src/app/(dashboard)/startups/page.tsx` | Startup Intelligence Dashboard & Discovery Feed with KPIs, multi-dimensional filters, search, and feed scan launcher. |
| `/startups/[opportunityId]` | `src/app/(dashboard)/startups/[opportunityId]/page.tsx` | Deep detail workbench with 4 tabs: Observation Ledger, AI Summary & Strategy, Technographics, and Corroboration Ledger. |
| `/startups/[opportunityId]/pitch` | `src/app/(dashboard)/startups/[opportunityId]/pitch/page.tsx` | Pitch Draft Editor grounded in candidate skills, featuring the 5-point explicit assumptions checklist and strict draft-only policy. |
| `/startups/saved` | `src/app/(dashboard)/startups/saved/page.tsx` | Bookmarked startup opportunities with personal candidate notes and quick links. |

---

## 2. Visual Walkthrough & Tab Layout

### Opportunity Detail Tabs:
- **Tab 1: Observation Ledger**: Displays verbatim quotes from original posts, source URLs, publishers, and independent UTC timestamps.
- **Tab 2: AI Summary & Strategy**: Renders machine-generated root causes, strategic roadmaps, and explicit non-endorsement disclaimers.
- **Tab 3: Technographics**: Shows observed technical products, frameworks, finding types (`AUDIT_DETECTED` vs `KEYWORD_MENTION`), and confidence percentages.
- **Tab 4: Corroboration**: Audits whether independent platforms corroborate the observation or if it is a syndicated copy.

### Pitch Editor Guardrails:
- Displays candidate skills extracted from confirmed profile/resume.
- Shows the 5 mandatory assumptions as warning checklist items.
- Character counter and tone selector (`casual`, `formal`, `short`).
- **NO SEND BUTTON**: Explicit policy preventing mass unsolicited messaging.

