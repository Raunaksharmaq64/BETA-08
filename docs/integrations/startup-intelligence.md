# Startup Intelligence Integration Specification

- **Title:** Startup Opportunity Mining Integration
- **Purpose:** Specifies REST API integration between Core API and the Startup Intelligence service.
- **Status:** APPROVED
- **Owner:** Principal Architect / Integrations Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Scope & Legacy Source
- **Legacy Source:** Prototype codebase located at `../Startups-problrms-hunter`.
- **Role in RIGHT FIT:** Independent satellite service (`services/startup_intelligence`) scanning Reddit, GitHub, Hacker News, and launch feeds for startup technical bottlenecks.

## 2. Integration Architecture
- Core Career API brokers all frontend queries to Startup Intelligence.
- Base URL configured via `STARTUP_INTELLIGENCE_BASE_URL` (default: `http://service-startup-intelligence:8002`).
- Communication occurs via JSON contracts defined in `contracts/pain_points/`.

## 3. Core Contract Endpoints
- `GET  /api/v1/pain-points` — Query filtered startup pain points (by tech stack, community source, problem category).
- `GET  /api/v1/pain-points/{id}` — Retrieve full context, source snippet, and evidence links.
- `POST /api/v1/pain-points/{id}/pitch` — Generate custom technical solution pitch for founder outreach.

## 4. Open Questions & TBDs
- [TBD] Migrating legacy file-based JSON persistence (`data/leads.json`) to PostgreSQL `startup_intel` schema in Phase 1.

