# RIGHT FIT — Continuous Discovery, Skill Taxonomy & Live Auto-Refresh Engine
**Document Version:** 1.0.0  
**Phase:** Master Implementation (Intelligent Career Discovery, Startup Pain-Point Intelligence & Auto-Refresh)  
**Status:** IMPLEMENTED, TESTED, AND PRODUCTION-VERIFIED  

---

## 1. Executive Summary

This specification documents the complete implementation of the **RIGHT FIT Continuous Discovery & Candidate Skill Intelligence Engine**, transforming RIGHT FIT into an evidence-backed career and market intelligence platform.

### Core Capabilities Implemented
1. **Candidate Skill Intelligence:** Evidence-backed skill taxonomy with confirmation lifecycle (`CONFIRMED`, `UNCONFIRMED`, `INFERRED`, `SUGGESTED`, `REJECTED`), extraction confidence scores, and profile versioning.
2. **Modular Connector Framework:** Extensible connector architecture (`BaseJobConnector`) powering Greenhouse ATS, Lever ATS, Ashby ATS, RemoteOK feed, and synthetic benchmarks with rate limiting and circuit breakers.
3. **Advanced Skill-Based Matching & Explainable Ranking:** Multi-dimensional ranking utilizing parent-child, transferable, and synonym taxonomy relationships ($0.75 \le W \le 0.95$) to match candidates across divergent job terminology without hallucination. Configurable formula:
   $$\text{Ranking Score} = 0.40 \cdot \text{Skill} + 0.20 \cdot \text{Role} + 0.15 \cdot \text{Experience} + 0.15 \cdot \text{Preference} + 0.10 \cdot \text{Freshness}$$
4. **Startup Pain-Point Intelligence:** Ingestion of public signals from Reddit, Hacker News, Product Hunt, and blogs. Independent multi-source corroboration updates canonical opportunities and evidence ledgers without artificial duplicates.
5. **Continuous Background Discovery:** Celery worker cluster (`celery_app.py`) with strict queue separation (`career_tasks`, `lead_tasks`, `startup_tasks`, `notification_tasks`), Celery Beat periodic schedules, and checkpointed state tracking.
6. **Live Frontend Auto-Refresh & Operations Console:** Background feed polling with floating "New Opportunities Available" banners preserving candidate scroll position, manual refresh controls with 30s rate-limit cooldowns, and a dedicated Operations Console at `/discovery/operations`.

---

## 2. Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Sources ["Permitted Public Ingestion"]
        GH["Greenhouse Public ATS"]
        LV["Lever Public Postings"]
        AB["Ashby Ingestion Engine"]
        RO["RemoteOK Feed"]
        SH["Startup Problems Satellite"]
    end

    subgraph Workers ["Celery Background Workers"]
        Beat["Celery Beat Scheduler"]
        QCareer["Queue: career_tasks"]
        QStartup["Queue: startup_tasks"]
        QLead["Queue: lead_tasks"]
        Beat --> QCareer
        Beat --> QStartup
        Beat --> QLead
    end

    subgraph CoreEngine ["Core Career Engine (FastAPI)"]
        Ingest["Ingestion & Deduplication Service"]
        Taxonomy["Taxonomy & Relationship Matrix"]
        Match["Evidence Matching & Ranking"]
        REST["Discovery REST & SSE Router"]
    end

    subgraph Database ["PostgreSQL Schema"]
        DBSched["discovery_schedule_configs"]
        DBExec["discovery_task_executions"]
        DBSkillRel["market_skill_relationships"]
        DBCandSkill["candidate_skills (Provenance & Confirmation)"]
        DBOpps["canonical_opportunities"]
        DBStartup["startup_opportunities & evidence"]
    end

    subgraph Frontend ["Next.js React Client"]
        LiveOpps["Opportunities Feed (Auto-Refresh)"]
        LiveStartups["Startup Signals Feed (Auto-Refresh)"]
        OpsDash["Discovery Operations Console"]
    end

    Sources --> Workers
    Workers --> Ingest
    Ingest --> Database
    Database --> Taxonomy
    Taxonomy --> Match
    Match --> REST
    REST --> LiveOpps
    REST --> LiveStartups
    REST --> OpsDash
```

---

## 3. Candidate Skill Intelligence & Taxonomy

### 3.1 Lifecycle States
- **`CONFIRMED`:** Explicitly reviewed and confirmed by the candidate; weighted at 1.0 in skill fit.
- **`UNCONFIRMED` / `INFERRED`:** AI-extracted from resume or parsed project text, pending explicit candidate confirmation; displayed with an amber tag and confirmation button.
- **`REJECTED`:** Explicitly rejected by the candidate; permanently excluded from active matching calculations.

### 3.2 Structured Taxonomy Relationships
Relationships are maintained in `market_skill_relationships` and cached in-memory for microsecond evaluation:

| Source Skill | Target Skill | Relationship Type | Transfer Strength ($W$) | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| `JavaScript` | `TypeScript` | `TRANSFERABLE` | 0.85 | Core JS concepts transfer directly to TypeScript |
| `TypeScript` | `JavaScript` | `TRANSFERABLE` | 0.95 | TS developers are proficient in raw JS |
| `React` | `Next.js` | `PARENT_CHILD` | 0.90 | Next.js builds on top of React architecture |
| `Next.js` | `React` | `TRANSFERABLE` | 0.95 | Next.js engineering translates to React components |
| `Python` | `FastAPI` | `PARENT_CHILD` | 0.85 | FastAPI is an async framework within Python |
| `FastAPI` | `Python` | `TRANSFERABLE` | 0.95 | FastAPI engineers possess Python expertise |
| `PostgreSQL` | `SQL` | `PARENT_CHILD` | 0.95 | Postgres represents advanced ANSI SQL |
| `Docker` | `Kubernetes` | `RELATED` | 0.80 | Containerization maps to orchestration |
| `Kubernetes` | `Docker` | `RELATED` | 0.85 | Orchestrators understand container runtimes |

---

## 4. REST API Contract Reference

### 4.1 Discovery Operations
- **`GET /api/v1/discovery/status`**  
  Returns engine state (`ACTIVE` / `PAUSED`), total active sources, total jobs/startups discovered, active schedules, and recent execution runs.
- **`POST /api/v1/discovery/refresh`**  
  Triggers immediate manual ingestion run. Subject to a strict 30-second per-user cooldown; returns HTTP 429 when throttled.
- **`POST /api/v1/discovery/pause` & `POST /api/v1/discovery/resume`**  
  Pauses or resumes discovery globally or for a specific `source_id`.
- **`GET /api/v1/discovery/config` & `PUT /api/v1/discovery/config/{source_id}`**  
  Allows updating polling interval (60s–86400s), batch records per run (5–500), and rate limits per minute.
- **`GET /api/v1/discovery/events`**  
  Server-Sent Events (SSE) stream broadcasting real-time heartbeat and discovery notification events.

### 4.2 Candidate Skill Lifecycle
- **`POST /api/v1/candidate/skills/{skill_id}/confirm`**  
  Promotes skill to `CONFIRMED` and timestamps confirmation.
- **`POST /api/v1/candidate/skills/{skill_id}/reject`**  
  Demotes skill to `REJECTED`, excluding it from opportunity ranking.
- **`POST /api/v1/candidate/skills/recompute`**  
  Recalculates candidate skill counts and increments profile versioning timestamp.

---

## 5. Startup Pain-Point Corroboration Engine

### Multi-Source Corroboration Logic
1. Observations from public sources (e.g. Reddit, Hacker News, Product Hunt) are matched against existing records by `service_record_id` or normalized `(domain + category)`.
2. When a corroborating signal is received:
   - The canonical `StartupOpportunityRecord` updates `last_checked_at` and `urgency_score = max(existing, new)`.
   - A new `StartupEvidenceRecord` is appended to the evidence ledger with the excerpt and limitations notes.
   - A `StartupCorroborationRecord` is created, and `corroboration_count` is incremented.
   - The platform never creates duplicate opportunities for the same startup problem.
3. Candidate pitch generation incorporates these corroborating citations and outputs explicit problem assumptions.

---

## 6. Verification & Test Evidence

| Test Suite | File | Tests Run | Result | Duration |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate Skill Intelligence** | `tests/unit/test_candidate_skill_intelligence.py` | 4 | **100% PASSED** | ~36s |
| **Continuous Discovery Integration** | `tests/integration/test_continuous_discovery_engine.py` | 4 | **100% PASSED** | ~19s |
| **Startup Clustering & Corroboration** | `tests/integration/test_startup_clustering_e2e.py` | 3 | **100% PASSED** | ~16s |
| **Connector Health & Quality Telemetry** | `tests/integration/test_connector_metrics_and_quality_api.py` | 3 | **100% PASSED** | ~15s |
| **Next.js Production Build** | `frontend/` (`npm run build`) | 48 routes | **100% PASSED (0 errors)** | ~43s |

---

## 7. Operational Runbook: Localhost Execution

### 1. Database & Migrations
```bash
cd c:\Users\Sahil\Desktop\manit\rightFIT\backend
python -m app.db.migrate_discovery
```

### 2. FastAPI Backend Server
```bash
cd c:\Users\Sahil\Desktop\manit\rightFIT\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API documentation available at `http://127.0.0.1:8000/docs`.

### 3. Celery Background Worker & Beat Scheduler
```bash
cd c:\Users\Sahil\Desktop\manit\rightFIT\backend
# Worker
celery -A app.workers.celery_app worker -Q career_tasks,lead_tasks,startup_tasks,notification_tasks --loglevel=info

# Beat Scheduler (separate terminal)
celery -A app.workers.celery_app beat --loglevel=info
```

### 4. Next.js Frontend Application
```bash
cd c:\Users\Sahil\Desktop\manit\rightFIT\frontend
npm run dev
```
Web application accessible at `http://localhost:3000`.
- Unified Opportunities: `http://localhost:3000/opportunities`
- Startup Pain Points: `http://localhost:3000/startups`
- Discovery Operations Console: `http://localhost:3000/discovery/operations`

