"""
RIGHT FIT Core — Celery Application & Background Worker Configuration
Version: 1.0.0
Master Implementation: Continuous Background Discovery & Auto-Refresh

Queue Architecture:
- career_tasks: Job discovery, ATS ingestion, candidate matching, deduplication
- lead_tasks: LeadHunter freelance extraction and satellite synchronizations
- startup_tasks: Startup problems hunter signals, observation clustering
- notification_tasks: Email, alerts, and calendar reminders
"""

from __future__ import annotations

import os
import logging
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from app.core.config import settings

logger = logging.getLogger("rightfit.workers")

redis_broker = settings.REDIS_URL or "redis://localhost:6379/0"

celery_app = Celery(
    "rightfit_workers",
    broker=redis_broker,
    backend=redis_broker,
    include=[
        "app.workers.tasks.discovery_tasks",
        "app.workers.tasks.startup_tasks",
        "app.workers.tasks.verification_tasks",
        "app.workers.tasks.freelance_tasks",
    ],
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 min hard limit
    task_soft_time_limit=240,  # 4 min soft limit
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
    # Defined Queue Architecture
    task_queues=[
        Queue("career_tasks", routing_key="career.#"),
        Queue("lead_tasks", routing_key="lead.#"),
        Queue("startup_tasks", routing_key="startup.#"),
        Queue("notification_tasks", routing_key="notification.#"),
    ],
    task_default_queue="career_tasks",
    # Task Routing Matrix
    task_routes={
        "app.workers.tasks.discovery_tasks.run_continuous_job_discovery": {"queue": "career_tasks"},
        "app.workers.tasks.discovery_tasks.run_incremental_source_update": {"queue": "career_tasks"},
        "app.workers.tasks.discovery_tasks.check_all_connector_health": {"queue": "career_tasks"},
        "app.workers.tasks.verification_tasks.run_periodic_verification": {"queue": "career_tasks"},
        "app.workers.tasks.verification_tasks.run_periodic_deduplication": {"queue": "career_tasks"},
        "app.workers.tasks.startup_tasks.run_continuous_startup_discovery": {"queue": "startup_tasks"},
        "app.workers.tasks.startup_tasks.run_pain_point_clustering": {"queue": "startup_tasks"},
        "app.workers.tasks.freelance_tasks.run_background_freelance_search": {"queue": "lead_tasks"},
        "app.workers.tasks.freelance_tasks.run_opportunity_audit_task": {"queue": "lead_tasks"},
    },
    # Celery Beat Scheduled Auto-Refresh
    beat_schedule={
        "continuous-job-discovery-30m": {
            "task": "app.workers.tasks.discovery_tasks.run_continuous_job_discovery",
            "schedule": 1800.0,  # 30 minutes
            "options": {"queue": "career_tasks"},
        },
        "continuous-startup-discovery-2h": {
            "task": "app.workers.tasks.startup_tasks.run_continuous_startup_discovery",
            "schedule": 7200.0,  # 2 hours
            "options": {"queue": "startup_tasks"},
        },
        "continuous-link-verification-1h": {
            "task": "app.workers.tasks.verification_tasks.run_periodic_verification",
            "schedule": 3600.0,  # 1 hour
            "options": {"queue": "career_tasks"},
        },
        "continuous-deduplication-sweeper-2h": {
            "task": "app.workers.tasks.verification_tasks.run_periodic_deduplication",
            "schedule": 7200.0,  # 2 hours
            "options": {"queue": "career_tasks"},
        },
        "connector-health-observability-15m": {
            "task": "app.workers.tasks.discovery_tasks.check_all_connector_health",
            "schedule": 900.0,  # 15 minutes
            "options": {"queue": "career_tasks"},
        },
    },
)

if __name__ == "__main__":
    celery_app.start()

