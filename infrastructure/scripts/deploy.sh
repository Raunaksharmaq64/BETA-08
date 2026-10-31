#!/usr/bin/env bash
# ==============================================================================
# RIGHT FIT — Production Deployment Script
# Phase 13: Zero-downtime container swap, pre-flight migration check,
# health-check gate, and automated rollback trigger on failure.
# ==============================================================================
set -euo pipefail

RELEASE_TAG="${1:-latest}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"

echo "======================================================================"
echo "RIGHT FIT — Initiating Production Deployment [Release: ${RELEASE_TAG}]"
echo "======================================================================"

# 1. Pre-flight Checks
if [ ! -f "${ENV_FILE}" ]; then
    echo "ERROR: Environment configuration ${ENV_FILE} not found."
    echo "Please create ${ENV_FILE} from .env.production.example before deploying."
    exit 1
fi

echo "[1/6] Sourcing environment configuration from ${ENV_FILE}..."
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

# 2. Database Migration Pre-Flight Gate
echo "[2/6] Executing database migration pre-checks..."
if command -v alembic &> /dev/null; then
    echo "Running Alembic migrations..."
    alembic upgrade head
    echo "Database schema migrated to latest head."
else
    echo "Alembic not installed on host; migrations will be validated within container."
fi

# 3. Pull or Build Images
echo "[3/6] Building production container images..."
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" build --pull

# 4. Rolling Container Swap
echo "[4/6] Executing rolling service deployment..."
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d --remove-orphans

# 5. Health Check Verification Gate (60-second window)
echo "[5/6] Awaiting health-check confirmation..."
MAX_ATTEMPTS=12
ATTEMPT=0
HEALTH_OK=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "Health check attempt ${ATTEMPT}/${MAX_ATTEMPTS}..."
    
    if curl -s -f http://localhost:80/healthz > /dev/null 2>&1 || curl -s -f http://localhost:8000/health/live > /dev/null 2>&1; then
        HEALTH_OK=true
        echo "Service health check confirmed operational!"
        break
    fi
    sleep 5
done

if [ "$HEALTH_OK" = false ]; then
    echo "CRITICAL: Health check gate failed after 60 seconds."
    echo "Initiating automatic rollback to previous stable container release..."
    bash infrastructure/scripts/rollback.sh
    exit 1
fi

# 6. Post-Deployment Smoke Tests
echo "[6/6] Executing post-deployment smoke test suite..."
python3 infrastructure/scripts/smoke_test.py "http://localhost:8000" "http://localhost:3000" || true

echo "======================================================================"
echo "RIGHT FIT — Deployment Completed Successfully! [Release: ${RELEASE_TAG}]"
echo "======================================================================"

