# Containerization & Production Images Guide

## 1. Principles of Production Container Design
1. **Multi-Stage Builds**: Compilers, build tools, package managers, and development headers exist solely in the `builder` stage. The final runtime image contains only bare application assets and runtime libraries.
2. **Minimal Attack Surface**: Uses Debian `slim` and Alpine bases, stripping unnecessary OS utilities.
3. **Unprivileged Execution**: Every container executes as an explicitly created system user with fixed UID/GID:
   - Backend & Workers: `appuser` (UID: 1001, GID: 1001)
   - Frontend: `nextjs` (UID: 1001, GID: 1001)
4. **Reproducible Pinned Dependencies**: Python dependencies are locked in `requirements.txt`; Node dependencies in `package-lock.json`.
5. **Proper Signal Handling & Graceful Shutdown**: `STOPSIGNAL SIGTERM` enables Gunicorn, Uvicorn, and Next.js to complete in-flight HTTP requests and database transactions before process termination.
6. **Active Health Probes**: Containers define Docker `HEALTHCHECK` instructions querying `/health/live` or `/healthz`.

## 2. Service Image Matrix

| Container Service | Base Image | Multi-Stage Target | User | Health Check Command | Port |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `rightfit-nginx-prod` | `nginx:1.25-alpine` | `runtime` | `nginx` | `curl -f http://localhost:80/healthz` | 80, 443 |
| `rightfit-frontend-prod` | `node:20-alpine` | `runner` | `nextjs` | `wget -qO- http://localhost:3000/` | 3000 |
| `rightfit-backend-prod` | `python:3.11-slim` | `runtime` | `appuser` | `curl -f http://localhost:8000/health/live` | 8000 |
| `rightfit-worker-prod` | `python:3.11-slim` | `runtime` | `appuser` | `python -c "import redis; ... ping()"` | N/A |
| `rightfit-leadhunter-prod` | `python:3.11-slim` | `runtime` | `appuser` | `curl -f http://localhost:8001/health/live` | 8001 |
| `rightfit-startup-intel-prod` | `python:3.11-slim` | `runtime` | `appuser` | `curl -f http://localhost:8002/health/live` | 8002 |
| `rightfit-redis-prod` | `redis:7-alpine` | `runtime` | `redis` | `redis-cli -a $REDIS_PASSWORD ping` | 6379 |

## 3. `.dockerignore` Rules
To prevent leaking credentials, local caches, and test artifacts into images, `.dockerignore` strictly excludes:
```
.env
.env.*
*.dump
*.db
*.sqlite
.git
.github
tests/
__pycache__/
node_modules/
.next/
```

