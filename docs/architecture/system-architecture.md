# System Architecture Specification

- **Title:** RIGHT FIT System Architecture Blueprint
- **Purpose:** Comprehensive architectural specification describing system components, topological layouts, and integration boundaries.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Architectural Philosophy
RIGHT FIT adopts a **Hybrid Modular Architecture**. This design balances monolithic simplicity for core transactional workflows (authentication, user management, resume parsing, job CRM) with autonomous service independence for data scrapers and opportunity miners (LeadHunter, Startup Intelligence).

```
                                 [ Web Clients ]
                                        │
                                        ▼ HTTPS (443)
                         ┌─────────────────────────────┐
                         │      Nginx Reverse Proxy    │
                         └──────────────┬──────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼ /                                           ▼ /api/
     ┌────────────────────────┐                   ┌────────────────────────┐
     │  Frontend Application   │                   │    Core Career API     │
     │  (Next.js 16 App Router│                   │     (FastAPI Python)   │
     └────────────────────────┘                   └───────────┬────────────┘
                                                              │
                                    ┌─────────────────────────┴─────────────────────────┐
                                    ▼ HTTP (Internal)                                   ▼ HTTP (Internal)
                        ┌────────────────────────┐                          ┌────────────────────────┐
                        │   LeadHunter Service   │                          │  Startup Intelligence  │
                        │ (Freelance Lead Engine)│                          │(Startup Problem Engine)│
                        └───────────┬────────────┘                          └───────────┬────────────┘
                                    │                                                   │
    ────────────────────────────────┼───────────────────────────────────────────────────┼────────────────
    Data Tier                       ▼                                                   ▼
                         ┌──────────────────────────────────────────────────────────────────┐
                         │                    PostgreSQL 16 Engine                          │
                         │   - Schema: core (users, resumes, jobs, matches, crm)            │
                         │   - Schema: leadhunter (businesses, audits, leads, sequences)    │
                         │   - Schema: startup_intel (startups, pain_points, discoveries)   │
                         └──────────────────────────────────────────────────────────────────┘
```

## 2. Component Breakdown

### 2.1 Next.js 16 Frontend
- Server-Side Rendering (SSR) and React Server Components (RSC) for initial page loads.
- Client-side interactivity for Kanban pipelines, real-time filters, and dynamic match inspection.
- Purely communicates with Core Career API over `/api/v1/*`.

### 2.2 FastAPI Core Career Engine
- The master orchestrator for user identity, resume intelligence, job index, and CRM stages.
- Holds adapters for ATS platforms (Lever, Greenhouse, Ashby, Workday, etc.).
- Exposes versioned REST endpoints consumed by the frontend.
- Integrates with external satellite services over standardized contracts.

### 2.3 Independent Satellite Services
1. **LeadHunter Service (`services/leadhunter`):**
   - Headless scraping and auditing of local business websites.
   - Independent background queues for bulk scans.
2. **Startup Intelligence Service (`services/startup_intelligence`):**
   - Scheduled scraping of developer discussion communities.
   - Independent data storage for pain point feeds.

### 2.4 Data & Queue Infrastructure
- **PostgreSQL 16:** Single robust database instance partitioned by isolated database schemas (`core`, `leadhunter`, `startup_intel`).
- **Redis 7:** Broker for Celery asynchronous workers and distributed caching.

## 3. Scalability & Resilience
- **Stateless Containers:** Backend API and Frontend runners maintain no local state and scale horizontally.
- **Circuit Breakers & Timeouts:** Outbound calls to satellite services and third-party APIs have strict 5-second timeouts and fallback responses to prevent cascading failures.

## 4. Open Questions & TBDs
- [TBD] Dedicated read-replica configuration for heavy job query traffic.

