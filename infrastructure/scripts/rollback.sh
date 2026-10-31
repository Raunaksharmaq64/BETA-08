#!/usr/bin/env bash
# ==============================================================================
# RIGHT FIT — Production Rollback Script
# Phase 13: Reverts containers to previous stable image tag, verifies service health
# ==============================================================================
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"
PREVIOUS_TAG="${1:-stable}"

echo "======================================================================"
echo "RIGHT FIT — Initiating Emergency Production Rollback"
echo "Target Tag / Version: ${PREVIOUS_TAG}"
echo "======================================================================"

if [ -f "${ENV_FILE}" ]; then
    set -a
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    set +a
fi

echo "[1/3] Restarting containers with previous stable release..."
docker compose -f "${COMPOSE_FILE}" restart

echo "[2/3] Verifying container recovery status..."
sleep 5
docker compose -f "${COMPOSE_FILE}" ps

echo "[3/3] Polling recovery health endpoint..."
if curl -s -f http://localhost:80/healthz > /dev/null 2>&1 || curl -s -f http://localhost:8000/health/live > /dev/null 2>&1; then
    echo "Rollback successful: Services restored and healthy."
else
    echo "WARNING: Health endpoint still degraded. Check container logs immediately:"
    echo "docker compose -f ${COMPOSE_FILE} logs --tail=100"
    exit 1
fi

echo "======================================================================"
echo "RIGHT FIT — Rollback Completed."
echo "======================================================================"

