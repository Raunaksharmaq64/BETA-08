# Redis & Celery Background Processing Guide

## 1. Redis Broker Architecture
- **Engine**: Redis 7 Alpine containerized on private Docker bridge network (`rightfit-internal-net`).
- **Access Control**: Password authentication enforced (`--requirepass`), zero public port publishing (port 6379 accessible only from backend and worker containers).
- **Memory & Eviction**:
  - `maxmemory 512mb`
  - `maxmemory-policy noeviction` (Guarantees Celery tasks and notifications are never silently dropped due to memory pressure).
- **Persistence**: Append-Only File (AOF) enabled (`appendonly yes`, `appendfsync everysec`) ensuring message queue recovery across restarts.

## 2. Celery Worker Configuration
- **Task Queues**:
  - `celery` (Default asynchronous jobs, email notifications)
  - `market_snapshots` (Nightly demand aggregations and compensation percentiles)
  - `scrapers` (Job connectors and ATS scrapers)
- **Concurrency**: `--concurrency=2` per container worker instance.
- **Graceful Termination**: `STOPSIGNAL SIGTERM` allows in-flight jobs up to 60 seconds (`--time-limit=300`, `--soft-time-limit=240`) to complete before container shutdown.
- **Worker Health Probe**: Queries `redis.ping()` to verify broker connectivity.

