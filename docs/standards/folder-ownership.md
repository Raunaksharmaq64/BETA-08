# Folder & Module Ownership Matrix

- **Title:** Repository Folder Ownership & Responsibilities
- **Purpose:** Clarifies functional ownership, permissible contents, and architectural custodians for every directory.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Directory Ownership Breakdown

| Directory | Primary Domain | Lead Owner | Permissible Contents |
| :--- | :--- | :--- | :--- |
| `frontend/` | Web Presentation Layer | Frontend Architect | Next.js App Router, React components, Tailwind styling, UI tests |
| `backend/` | Core Career Engine | Backend Architect | FastAPI routers, domain modules, SQLAlchemy models, Alembic migrations |
| `services/leadhunter/` | Freelance Opportunity Service | Data / Lead Lead | Dockerfile, service configuration, and integration glue for LeadHunter |
| `services/startup_intelligence/` | Startup Discovery Service | Data / Discovery Lead | Dockerfile, service configuration, and integration glue for Startup Intel |
| `contracts/` | Cross-Service Data Schemas | Principal Architect | Shared JSON Schemas and Pydantic DTO contracts |
| `infrastructure/` | Container & Cloud DevOps | DevOps Engineer | Dockerfiles, Nginx configurations, AWS templates, monitoring configs |
| `docs/` | System Documentation | Documentation Lead | Architectural specs, PRDs, API guides, ADRs, security policies |
| `scripts/` | Developer Automation Tooling | Engineering Team | Shell, PowerShell, and Python scripts for dev setup, db, and maintenance |
| `.github/` | CI/CD Pipeline Automation | DevOps Engineer | GitHub Actions workflow definitions |

## 2. Directory Governance Directives
1. **No Rogue Files:** Do not create ad-hoc root folders outside this specification.
2. **Boundary Protection:** Frontend code must never exist inside `backend/`; Core database logic must never exist inside `frontend/`.
3. **Legacy Preservation:** The three original projects (`../agentic-career-search`, `../ai agents`, `../Startups-problrms-hunter`) reside outside this repository and must never be committed inside `rightFIT`.

## 3. Open Questions & TBDs
- [TBD] Team CODEOWNERS mapping file for automated PR reviewer assignment.

