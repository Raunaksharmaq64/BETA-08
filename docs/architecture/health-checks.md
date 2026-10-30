# RIGHT FIT — Health & Readiness Probe Architecture
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE GOVERNANCE  

---

## 1. Executive Summary

Container orchestration and reliable zero-downtime deployments require strict separation between **Liveness** and **Readiness** probes. Conflating these two checks leads to cascading container failure loops during transient database contention or upstream satellite latency.

RIGHT FIT establishes a platform-wide two-tier health probe contract across all backend services:
1. **Core Career Engine** (`:8000`)
2. **LeadHunter AI Service** (`:8001`)
3. **Startup Intelligence Service** (`:8002`)

---

## 2. Probe Specifications

### 2.1 Liveness Probe (`GET /health/live`)

- **Purpose:** Verifies whether the process event loop is alive and capable of responding to HTTP requests.
- **Dependency Isolation:** Strictly **NO** database, cache, or external network pings are performed.
- **Container Behavior on Failure:** Container orchestrator (Docker/Kubernetes/ECS) will restart the container.
- **Contract Schema:** `LivenessResponse`
- **HTTP Response Codes:**
  - `200 OK`: Process is healthy and responsive.
  - `500 Internal Server Error`: Event loop deadlocked or out of memory.

```json
{
  "status": "healthy",
  "service": "core_career_engine",
  "timestamp": "2026-10-31T00:44:00Z"
}
```

### 2.2 Readiness Probe (`GET /health/ready`)

- **Purpose:** Verifies whether the service can accept incoming user traffic and execute transactions.
- **Dependency Isolation:** Actively verifies connection pools to service-owned datastores (PostgreSQL, Redis) and downstream satellites.
- **Container Behavior on Failure:** Container orchestrator stops routing ingress traffic to this replica; **no restart** occurs, allowing dependencies to recover without thrashing.
- **Contract Schema:** `ReadinessResponse`
- **HTTP Response Codes:**
  - `200 OK`: All critical dependencies are available (`healthy`).
  - `503 Service Unavailable`: One or more critical dependencies failed (`unhealthy`).

```json
{
  "status": "healthy",
  "service": "core_career_engine",
  "dependencies": {
    "database": {
      "status": "healthy",
      "latency_ms": 1.82,
      "message": "Database connection pool operational"
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 0.80,
      "message": "Redis queue operational"
    }
  },
  "timestamp": "2026-10-31T00:44:00Z"
}
```

---

## 3. Degradation & Outage Policy

| Dependency State | Service Overall Status | HTTP Status | Ingress Traffic Route |
| :--- | :--- | :--- | :--- |
| Database Healthy, Redis Healthy | `healthy` | 200 OK | Enabled |
| Redis Latency Degraded (>50ms) | `degraded` | 200 OK | Enabled (throttled) |
| Database Connection Refused | `unhealthy` | 503 Unavailable | Disabled (standby) |
| Satellite Service Unavailable | `healthy` / `degraded` | 200 OK | Enabled (satellite routes circuit-broken) |

> [!IMPORTANT]
> Satellite services (LeadHunter AI, Startup Intelligence) must never cause Core's `/health/ready` probe to fail. Satellite unavailability degrades specific discovery features gracefully via circuit-breaking while keeping the Core authentication and job-matching platform operational.

---

## 4. Docker Compose Probe Wiring

In `docker-compose.yml`, health checks are configured using `curl`:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health/live || exit 1"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 15s
```
Dependent services employ the `condition: service_healthy` clause to enforce orderly startup.

