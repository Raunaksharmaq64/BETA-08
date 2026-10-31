# Startup Intelligence & Pain Point Opportunity Integration
## Module Specification: Phase 10

- **Module ID:** `startup-intelligence`
- **Module Version:** `1.0.0`
- **Architecture:** Option A Hybrid Modular Architecture (Core + Independent Satellite Service)
- **Satellite Service:** `Startups-problrms-hunter` (Port 8002 / `STARTUP_INTELLIGENCE_BASE_URL`)
- **Status:** COMPLETED & VERIFIED
- **Last Updated:** 2026-10-31

---

## 1. Executive Summary

Phase 10 integrates the independent **Startup Intelligence** service (`Startups-problrms-hunter`) into the **RIGHT FIT Career Intelligence Platform**.

Unlike speculative outbound prospecting, Startup Intelligence systematically scans multi-source public feeds, developer communities, and launch platforms to detect **verifiable technical bottlenecks** (latency spikes, SEO tag omissions, database connection exhaustion, active developer hiring signals). It enables candidates to discover high-urgency pain points and formulate evidence-grounded, customized pitch drafts with **mandatory disclosure of unconfirmed assumptions**.

### Key Capabilities Delivered:
1. **Source Governance & Audit**: Forensic audit of all 12 discovery channels across Reddit, RSS, Hacker News, GitHub, Dev.to, Google News, IndieHackers, and Web Search with explicit limitations.
2. **Authenticated Core Adapter**: Resilient HTTP client featuring Circuit Breaker (`CLOSED`, `OPEN`, `HALF_OPEN`), jittered exponential backoff, and graceful fallback to cached Core records when the satellite service is offline.
3. **Canonical Opportunity & Evidence Schema**: Core-owned `startup_opportunities` with 1-to-N immutable `startup_evidence` ledgers, `startup_tech_findings`, and `startup_corroborations`.
4. **Strict Separation of Observation vs. AI Summary**: Verbatim source excerpts are visibly isolated from machine-generated interpretations (`gemini-2.0-flash` or template fallbacks).
5. **Technographic Stack Findings**: Traces observed frameworks, tools, and databases to exact audit signals and public context without speculative guessing.
6. **Candidate Pitch Drafts with Explicit Assumptions**: Generates tailored drafts grounded in confirmed candidate skills, accompanied by a 5-point unconfirmed assumptions checklist. **Strict policy: Draft only; no automatic sending.**
7. **JSON-to-PostgreSQL Migration Assessment & Dry Run**: Audited all 598 existing leads in `data/leads.json`. Completed a zero-data-loss dry run simulation while preserving original JSON storage.
8. **Candidate-Facing Next.js Dashboard**: 4 fully responsive screens (`/startups`, `/startups/[opportunityId]`, `/startups/[opportunityId]/pitch`, `/startups/saved`) with 0 compilation errors across 35 routes.

---

## 2. Documentation Catalog

| Document | Description |
|---|---|
| [1. Source-by-Source Audit](./source-by-source-audit.md) | Audit of 12 community & web channels with reliability, terms, rate limits, and failure behaviors. |
| [2. Versioned API Contract](./versioned-api-contract.md) | REST contract between Core (`:8000`) and Startup Intelligence (`:8002`). |
| [3. Core Adapter Architecture](./core-adapter-architecture.md) | Circuit Breaker state machine, retries, headers, and degraded resilience mode. |
| [4. Startup Problem Mapping](./startup-problem-mapping.md) | Normalization of raw leads to canonical opportunities without hallucinated fields. |
| [5. Evidence Provenance & Timestamps](./evidence-provenance-and-timestamps.md) | Separate UTC timestamps (`published_at`, `retrieved_at`, `first_seen_at`, `last_checked_at`). |
| [6. Observation vs AI Summary Policy](./observation-vs-ai-summary-policy.md) | Visible separation of verbatim text from machine-generated interpretation. |
| [7. Deduplication & Corroboration](./deduplication-and-corroboration.md) | Safe deduplication rules, independent source counting, and conflict flags. |
| [8. Technology Findings Specification](./technology-findings-specification.md) | Traceable technographic stack findings (`AUDIT_DETECTED` vs `KEYWORD_MENTION`). |
| [9. Pitch Drafts & Assumptions Policy](./pitch-drafts-and-assumptions.md) | Candidate skill grounding, explicit assumptions checklist, and strict no-send rule. |
| [10. JSON-to-PostgreSQL Migration Assessment](./json-to-postgresql-migration-assessment.md) | Assessment of 598 records in `leads.json`, schema mapping, and rollback plans. |
| [11. Migration Dry-Run Report](./migration-dry-run-report.md) | Dry-run verification test report confirming 0.0% data loss risk. |
| [12. Independent Deployment Guide](./independent-deployment-guide.md) | Independent runtime, environment variables, dependencies, and health checks. |
| [13. Downtime & Recovery Runbook](./downtime-and-recovery-runbook.md) | Resilience behavior when satellite service is offline, timeouts, and restart recovery. |
| [14. Startup Frontend User Guide](./startup-frontend-guide.md) | UI architecture, discovery feed, detail tabs, and pitch workbench. |
| [15. Security & Privacy Review](./security-and-privacy-review.md) | SSRF defense, prompt injection mitigation, access controls, and candidate privacy. |

