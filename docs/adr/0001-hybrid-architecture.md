# ADR-0001: Adoption of Option A — Hybrid Modular Architecture

- **Document ID:** ADR-0001
- **Title:** Hybrid Modular Architecture (Core Engine + Independent Satellite Services)
- **Status:** ACCEPTED
- **Author:** Principal Software Architect
- **Date:** 2026-10-31

---

## 1. Context & Problem Statement
The RIGHT FIT product requires integrating three distinct domain capabilities:
1. Career discovery, ATS resume matching, and job CRM (`agentic-career-search`).
2. Local business freelance client acquisition and broken-website auditing (`ai agents` / LeadHunter).
3. Startup community technical problem mining and founder outreach (`Startups-problrms-hunter`).

Attempting to merge all three codebases into a single giant monolithic application would risk breaking working scraping pipelines, mixing disparate dependencies (Playwright, BeautifulSoup, Celery, SQLModel), and creating deployment fragility. Conversely, fragmenting the system into 10+ granular microservices would introduce excessive operational overhead, network latency, and distributed transaction complexity.

---

## 2. Decision
We adopt **Option A — Hybrid Modular Architecture**:
* **Core Career Engine (`backend/`):** Primary backend API and orchestrator. Owns user identity, candidate profiles, resume intelligence, ATS job matching, application tracking CRM, and service aggregation. Evolves from `agentic-career-search`.
* **LeadHunter AI Service (`services/leadhunter/`):** Autonomous satellite service executing Google Maps scraping, website DNS/SSL/HTTP availability audits, and deep social crawler tasks.
* **Startup Intelligence Service (`services/startup_intelligence/`):** Autonomous satellite service scanning Reddit, GitHub ("help wanted"), Hacker News, and RSS feeds, analyzing technical signals via Google Gemini.
* **Unified Presentation Layer (`frontend/`):** Single Next.js 16 Web Dashboard serving jobs, freelance leads, and startup opportunities to the end user.
* **Communication Interface:** Versioned HTTP/REST APIs (`/api/v1/*`) with standard JSON schemas. Frontend never directly connects to private satellite services.

---

## 3. Alternatives Considered

### Alternative 1: Pure Monolith (Full Rewrite into a Single Service)
* *Pros:* Single deployable artifact, direct in-memory calls.
* *Cons:* Requires rewriting hundreds of working scrapers and adapters, mixes conflicting scraping dependencies, increases deployment risk.

### Alternative 2: Pure Microservices Mesh
* *Pros:* Complete decoupling of every sub-feature into separate services.
* *Cons:* High DevOps overhead, requires distributed tracing, distributed transactions, and service discovery for a project that does not yet require multi-team scaling.

---

## 4. Consequences & Implications

### Positive Consequences:
* **Preserves Working Assets:** Proven ATS adapters (70+) and Google Maps scrapers continue functioning without risky rewrites.
* **Clear Domain Boundaries:** Each service has clear functional responsibilities and isolated data storage.
* **Independent Scalability:** Heavy scraping tasks run in isolated satellite containers without degrading Core API responsiveness.

### Negative / Trade-Off Consequences:
* **Inter-Service Latency:** Aggregating opportunities across services requires network calls over Docker bridge network.
* **Multi-Container Local Dev:** Requires Docker Compose orchestration for local development.

### Security & Deployment Implications:
* Satellite service ports (8001, 8002) are internal only and never exposed publicly.
* All service-to-service calls require pre-shared HMAC key validation (`X-Internal-Service-Key`).

