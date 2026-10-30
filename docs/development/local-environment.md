# Local Environment Configuration

- **Title:** Local Development Environment Specification
- **Purpose:** Specifies port allocations, resource limits, and service virtualization configurations.
- **Status:** APPROVED
- **Owner:** DevOps Engineer (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Port Allocation Table
| Service | Container Name | Local Host Port | Internal Container Port |
| :--- | :--- | :--- | :--- |
| Next.js Frontend | `rightfit-frontend-dev` | `3000` | `3000` |
| Core FastAPI Backend | `rightfit-backend-dev` | `8000` | `8000` |
| LeadHunter Service | `rightfit-leadhunter-dev`| `8001` | `8001` |
| Startup Intelligence | `rightfit-startup-intel`| `8002` | `8002` |
| PostgreSQL Database | `rightfit-postgres-dev` | `5432` | `5432` |
| Redis In-Memory Cache| `rightfit-redis-dev` | `6379` | `6379` |

## 2. Hardware & Resource Allocations
- **Minimum Memory (RAM):** 8 GB (16 GB recommended for multi-container local stack).
- **Minimum Disk Space:** 10 GB free space for Docker images, dependencies, and local PostgreSQL data.
- **CPU Allocation:** Multi-core (4+ cores recommended) to support concurrent Celery workers and Next.js Turbopack compilation.

## 3. Database Credentials (Local Dev Defaults)
- User: `rightfit_admin`
- Password: `rightfit_dev_secret`
- Databases: `rightfit_core`, `rightfit_leadhunter`

## 4. Open Questions & TBDs
- [TBD] Windows WSL2 specific performance tuning flags for file system watches.

