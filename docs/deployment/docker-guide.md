# Docker Containerization Guide

- **Title:** Container Architecture & Local Orchestration Guide
- **Purpose:** Documents multi-stage Docker builds, development compose usage, and container lifecycle hygiene.
- **Status:** APPROVED
- **Owner:** DevOps Engineer (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Container Topology
RIGHT FIT defines independent, minimal Dockerfiles for each deployable tier:
- `frontend/Dockerfile`: Multi-stage build (deps ➔ builder ➔ non-root runner) for Next.js.
- `backend/Dockerfile`: Minimal Python 3.11-slim container with non-root user `appuser`.
- `services/leadhunter/Dockerfile`: Python container with dependencies for headless browser automation.
- `services/startup_intelligence/Dockerfile`: Python scraper runner.

## 2. Docker Compose Commands (Development)
```bash
# Build all images cleanly
docker compose build --no-cache

# Start full multi-service environment in background
docker compose up -d

# View live aggregate logs
docker compose logs -f

# Check container health status
docker compose ps

# Teardown containers and networks (preserving database volumes)
docker compose down

# Teardown containers AND delete persistent volumes (Destructive!)
docker compose down -v
```

## 3. Best Practices
- **Never Run as Root:** Production images must drop privileges and run as non-root service users (`nextjs`, `appuser`).
- **No Embedded Secrets:** Environment variables and API keys must be injected dynamically at container runtime.

## 4. Open Questions & TBDs
- [TBD] Dedicated container health check scripts in `infrastructure/docker/healthcheck.sh`.

