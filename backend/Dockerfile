# ==============================================================================
# RIGHT FIT — Core Career Engine Production Dockerfile
# Multi-stage, minimal attack surface, non-root user, reproducible build
# ==============================================================================

# Stage 1: Build & Dependencies Compiler
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONPATH="/app:${PYTHONPATH}"

# Install minimal runtime shared libraries (libpq for postgres) and curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Dedicated unprivileged system user and group
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --home /home/appuser appuser

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source code and contracts
COPY app ./app
COPY contracts ./contracts
COPY alembic ./alembic
COPY alembic.ini .

# Ensure appuser owns application directory
RUN chown -R appuser:appgroup /app /home/appuser

USER appuser

EXPOSE 8000

# Graceful termination handling
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Production WSGI/ASGI Runner: 4 Uvicorn workers managed by Gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
