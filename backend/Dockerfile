# ==============================================================================
# RIGHT FIT — Core Career Engine Backend Dockerfile (Python 3.11+)
# STATUS: TEMPLATE / ARCHITECTURE SETUP PHASE (NOT FINALIZED FOR RUNTIME EXECUTION)
# ==============================================================================

FROM python:3.11-slim AS base

WORKDIR /app

# Prevent Python from writing .pyc and buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install basic OS dependencies for PostgreSQL client and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Non-root user creation for security
RUN addgroup --system appgroup && adduser --system --group appuser

# Placeholder copy and install in implementation phase
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .

USER appuser

EXPOSE 8000

CMD ["echo", "[TEMPLATE] Backend Core API runner placeholder"]

