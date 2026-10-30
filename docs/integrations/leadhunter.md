# LeadHunter Integration Specification

- **Title:** LeadHunter Freelance Opportunity Integration
- **Purpose:** Specifies REST API integration and container orchestration between Core API and the LeadHunter service.
- **Status:** APPROVED
- **Owner:** Principal Architect / Integrations Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Scope & Legacy Source
- **Legacy Source:** Prototype codebase located at `../ai agents`.
- **Role in RIGHT FIT:** Independent satellite service (`services/leadhunter`) providing local business discovery, website availability audits, and freelance client leads.

## 2. Integration Architecture
- Core Career API communicates with LeadHunter exclusively over internal HTTP REST endpoints.
- Base URL configured via `LEADHUNTER_BASE_URL` (default: `http://service-leadhunter:8001`).
- Direct database writes between Core and LeadHunter are strictly prohibited.

## 3. Core Contract Endpoints
- `POST /api/v1/scans` — Initiates an asynchronous business audit scan for a target location and category.
- `GET  /api/v1/scans/{job_id}` — Returns progress percentage and newly discovered leads.
- `GET  /api/v1/leads/{id}/audit` — Returns technical audit findings (DNS, SSL, broken status, performance).
- `POST /api/v1/outreach/draft` — Returns AI-generated pitch proposal for the business lead.

## 4. Human-in-the-Loop & Outbound Policy
- Outreach emails must never be sent automatically. The user must review, edit, and approve all pitch emails before sending.

## 5. Open Questions & TBDs
- [TBD] WebSocket channel vs. polling for scan progress updates in Next.js dashboard.

