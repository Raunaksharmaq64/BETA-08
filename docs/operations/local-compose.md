# RIGHT FIT — Local Docker Compose Architecture
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Multi-Container Topography

RIGHT FIT uses Docker Compose (`docker-compose.yml`) to orchestrate local microservices and shared infrastructure across an isolated bridge network (`rightfit-network`):

```
                       [ rightfit-network ]
                                 │
     ┌───────────────────┬───────┴───────┬───────────────────┐
     ▼                   ▼               ▼                   ▼
[ postgres:16 ]    [ redis:7 ]     [ backend:8000 ]    [ frontend:3000 ]
  (Schemas)          (Queues)        (Core Engine)       (Next.js)
     ▲                   ▲               ▲
     │                   │               │
     └───────────────────┼───────────────┘
                         │
     ┌───────────────────┴───────────────────┐
     ▼                                       ▼
[ service-leadhunter:8001 ]    [ service-startup-intelligence:8002 ]
  (LeadHunter AI)                (Startup Intel)
```

---

## 2. Container Inventory & Health Checks

| Service | Port | Image / Context | Health Check | Depends On |
| :--- | :--- | :--- | :--- | :--- |
| `postgres` | 5432 | `postgres:16-alpine` | `pg_isready -U rightfit_admin` | None |
| `redis` | 6379 | `redis:7-alpine` | `redis-cli ping` | None |
| `backend` | 8000 | `./backend` | `curl -f http://localhost:8000/health/live` | `postgres`, `redis` (healthy) |
| `worker` | N/A | `./backend` | N/A (background Celery daemon) | `backend`, `redis` (healthy) |
| `frontend` | 3000 | `./frontend` | HTTP 200 on Next.js root | `backend` (healthy) |
| `service-leadhunter` | 8001 | `./services/leadhunter` | `curl -f http://localhost:8001/health/live` | `postgres`, `redis` (healthy) |
| `service-startup-intelligence` | 8002 | `./services/startup_intelligence` | `curl -f http://localhost:8002/health/live` | `redis` (healthy) |

---

## 3. Database Schema Ownership

To avoid monolithic database sprawl while simplifying local development, PostgreSQL 16 hosts a single cluster with strictly isolated schema ownership:

1. `career_core`: Owned exclusively by Core Career Engine.
2. `leadhunter_db`: Owned exclusively by LeadHunter AI.
3. `startup_intel_db`: Owned exclusively by Startup Intelligence.

The initialization script `./scripts/database/01-init-schemas.sql` runs on first container startup:

```sql
CREATE SCHEMA IF NOT EXISTS career_core;
CREATE SCHEMA IF NOT EXISTS leadhunter_db;
CREATE SCHEMA IF NOT EXISTS startup_intel_db;
```

> [!CAUTION]
> **No Cross-Schema SQL Joins:** Under no circumstances may one microservice query or join tables belonging to another schema. All inter-service data exchange must occur via versioned REST APIs and canonical OpportunityEnvelopes.

---

## 4. Volume Persistence

- `postgres_data`: Persists relational tables and migrations across container restarts.
- `redis_data`: Persists queue snapshots and background task states.

