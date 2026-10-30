# Product Delivery Roadmap

- **Title:** RIGHT FIT Phased Engineering & Product Roadmap
- **Purpose:** Outlines milestone schedules, technical dependencies, and feature deliverables across all phases.
- **Status:** DRAFT
- **Owner:** Engineering Leadership (TBD)
- **Last Updated:** 2026-10-30

---

## Phase 0: Architecture Setup & Legacy Audit (Current)
- Complete directory structure and engineering standards.
- Author AGENTS.md, root README, and all governance documents.
- Complete comprehensive technical audit of the three legacy repositories (`agentic-career-search`, `ai agents`, `Startups-problrms-hunter`).
- Finalize reuse vs. API integration boundaries.

## Phase 1: Core Foundation & Contracts
- Implement centralized PostgreSQL schema and Alembic migrations.
- Set up JWT authentication, user registration, and profile storage.
- Establish JSON Schema contracts for inter-service communication.
- Containerize satellite services (LeadHunter, Startup Intelligence) behind versioned HTTP endpoints.

## Phase 2: Resume Intelligence & ATS Job Matching
- Implement resume parsing engine (PDF/DOCX extraction).
- Port deterministic skills matching logic and ATS keyword analysis.
- Connect 50+ ATS adapters for automated job discovery.
- Deliver Application CRM stage tracker.

## Phase 3: Unified Dashboard & Satellite Integration
- Build Next.js 16 frontend with App Router, Tailwind CSS, and shadcn/ui.
- Integrate Freelance Leads (LeadHunter) and Startup Pain Points into the unified dashboard.
- Deliver Glassmorphic metrics dashboard and Kanban pipelines.

## Phase 4: Production Deployment & Cloud Hardening
- Configure production Docker Compose, Nginx reverse proxy, and Let's Encrypt SSL.
- Deploy to AWS EC2 with S3 encrypted storage and automated backups.
- Implement rate limiting, observability (Prometheus/Grafana), and security hardening.

## Open Questions & TBDs
- [TBD] Final timeline estimates following Phase 0 legacy audit completion.

