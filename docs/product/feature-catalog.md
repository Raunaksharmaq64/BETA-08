# Feature Catalog

- **Title:** RIGHT FIT Feature Inventory & Capability Matrix
- **Purpose:** Exhaustive catalog of all current and planned platform capabilities mapped to service modules.
- **Status:** DRAFT
- **Owner:** Product Management / Architecture (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Core Career Module
| Feature ID | Feature Name | Description | Module Owner | Status |
| :--- | :--- | :--- | :--- | :--- |
| FEAT-CC-01 | ATS Parser | Extracts skills, work history, and education from PDF/DOCX | `modules/resume` | PLANNED |
| FEAT-CC-02 | Deterministic Fit Engine | Computes fit scores with explicit matched/missing skill lists | `modules/matching` | PLANNED |
| FEAT-CC-03 | Multi-ATS Aggregator | Adapters for Ashby, Lever, Greenhouse, Workday, etc. | `modules/jobs` | PLANNED |
| FEAT-CC-04 | Application CRM | Visual Kanban tracking with state transitions and notes | `modules/applications` | PLANNED |
| FEAT-CC-05 | Compensation Estimator | Computes base salary, equity vest cliffs, and benefits | `modules/compensation` | PLANNED |
| FEAT-CC-06 | Interview Prep & STAR | Generates tailored behavioral STAR stories and questions | `modules/interviews` | PLANNED |
| FEAT-CC-07 | Job Legitimacy Guard | Scores job legitimacy and flags ghost listings | `modules/verification` | PLANNED |

## 2. Freelance Opportunity Module (LeadHunter Integration)
| Feature ID | Feature Name | Description | Module Owner | Status |
| :--- | :--- | :--- | :--- | :--- |
| FEAT-LH-01 | Google Maps Discovery | Identifies local businesses missing websites or digital footprints | `services/leadhunter` | SATELLITE (LEGACY) |
| FEAT-LH-02 | Broken Website Auditor | Audits DNS, SSL, 404/500 errors, and mobile performance | `services/leadhunter` | SATELLITE (LEGACY) |
| FEAT-LH-03 | Contact & Social Crawler | Scrapes Instagram, Facebook, and founder email contacts | `services/leadhunter` | SATELLITE (LEGACY) |
| FEAT-LH-04 | Pitch Draft Generator | Produces custom website redesign sales pitches | `services/leadhunter` | SATELLITE (LEGACY) |
| FEAT-LH-05 | Reply Tracker (IMAP) | Background monitoring for client email responses | `services/leadhunter` | SATELLITE (LEGACY) |

## 3. Startup Intelligence Module
| Feature ID | Feature Name | Description | Module Owner | Status |
| :--- | :--- | :--- | :--- | :--- |
| FEAT-SI-01 | Community Scanner | Monitors Reddit (/r/saas, /r/startups), HN, and GitHub | `services/startup_intelligence` | SATELLITE (LEGACY) |
| FEAT-SI-02 | Pain-Point Classifier | Flags slow load times, framework upgrades, and bug signals | `services/startup_intelligence` | SATELLITE (LEGACY) |
| FEAT-SI-03 | Tech Stack Detector | Detects React, Next.js, WordPress, Shopify, and cloud providers | `services/startup_intelligence` | SATELLITE (LEGACY) |
| FEAT-SI-04 | Founder Contact Lookup | Integrates Tomba/Hunter/Serper for founder outreach details | `services/startup_intelligence` | SATELLITE (LEGACY) |

## 4. Open Questions & TBDs
- [TBD] Final selection of vector database engine (pgvector vs Qdrant) for semantic resume matching.

