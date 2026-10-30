# ==============================================================================
# RIGHT FIT — Development & Architecture Management Makefile
# Status: ARCHITECTURE FOUNDATION PHASE (Commands are structural templates)
# ==============================================================================

.PHONY: help dev build test lint format clean docker-up docker-down docker-logs

help:
	@echo "RIGHT FIT — Available commands:"
	@echo "  make dev          Start local development containers"
	@echo "  make build        Build all container images"
	@echo "  make test         Run test suites across all services"
	@echo "  make lint         Run linting across frontend and backend"
	@echo "  make format       Auto-format codebases"
	@echo "  make docker-up    Start full stack in detached mode"
	@echo "  make docker-down  Stop all active containers"
	@echo "  make docker-logs  Follow container logs"
	@echo "  make clean        Clean build artifacts, pycache, and temp files"

dev:
	docker compose up --build

build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

lint:
	@echo "[RIGHT FIT] Running backend linting (Ruff)..."
	@echo "[RIGHT FIT] Running frontend linting (ESLint)..."

format:
	@echo "[RIGHT FIT] Formatting code (Ruff / Prettier)..."

test:
	@echo "[RIGHT FIT] Running backend tests (pytest)..."
	@echo "[RIGHT FIT] Running frontend tests..."

clean:
	@echo "[RIGHT FIT] Cleaning cache and build artifacts..."

