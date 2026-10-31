# Deployment Runbook

## 1. Production Release Workflow
Production deployments are executed via `infrastructure/scripts/deploy.sh` or through the approved CI/CD deployment pipeline:

```bash
bash infrastructure/scripts/deploy.sh v1.0.0
```

### Automated Execution Steps:
1. **Pre-flight Configuration**: Sources parameters from `.env.production` (generated from AWS SSM).
2. **Database Migration Gate**: Runs `alembic upgrade head`. Halts immediately if migrations fail.
3. **Container Image Build**: Builds production images using multi-stage Dockerfiles.
4. **Zero-Downtime Container Swap**: Executes `docker compose -f docker-compose.prod.yml up -d --remove-orphans`.
5. **Health Check Gate**: Polls `/health/live` and `/healthz` for 60 seconds.
6. **Automatic Rollback Trigger**: If health check does not confirm within 60s, automatically invokes `rollback.sh`.
7. **Post-Deployment Smoke Tests**: Executes `python infrastructure/scripts/smoke_test.py`.

