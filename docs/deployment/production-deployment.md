# Production Deployment Guide

- **Title:** Production Deployment Standards & Checklist
- **Purpose:** Mandates pre-deployment verification, container staging, SSL configuration, and zero-downtime execution.
- **Status:** APPROVED
- **Owner:** DevOps Engineer / SRE (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Production Architecture Overview
In production, all traffic enters via Nginx (port 80/443 with TLS termination). Nginx routes `/api/*` requests to the Core FastAPI backend and all other traffic to the Next.js frontend container. Satellite services (`service-leadhunter`, `service-startup-intelligence`) are isolated inside the internal Docker bridge network and are never exposed publicly.

## 2. Pre-Deployment Verification Checklist
- [ ] Production `.env` configured with high-entropy `JWT_SECRET` (min 32 chars).
- [ ] Database credentials rotated and managed via AWS Secrets Manager.
- [ ] Debug mode disabled across all services (`APP_DEBUG=false`, `NODE_ENV=production`).
- [ ] Database migrations tested on a staging replica prior to execution.
- [ ] Nginx TLS certificates valid and automated renewal scheduled.

## 3. Production Deployment Execution
```bash
# 1. Pull latest production images
docker compose -f docker-compose.prod.yml pull

# 2. Run database migrations
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 3. Spin up production containers
docker compose -f docker-compose.prod.yml up -d --remove-orphans

# 4. Verify system health
curl -f https://rightfit.example.com/api/v1/health/ready
```

## 4. Open Questions & TBDs
- [TBD] Blue/Green deployment strategy via AWS Application Load Balancer.

