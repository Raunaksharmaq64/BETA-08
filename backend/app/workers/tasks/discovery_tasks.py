"""
RIGHT FIT Core — Continuous Job Discovery Tasks
Version: 1.0.0
Master Implementation: Background Ingestion & Connector Probes
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.db.models import (
    DiscoveryScheduleConfigRecord,
    DiscoveryTaskExecutionRecord,
    JobSourceRecord,
    ConnectorHealthSnapshotRecord,
    utc_now,
)
from app.services.ingestion_service import IngestionService
from app.services.connectors import get_connector, list_supported_providers
from app.workers.celery_app import celery_app

logger = logging.getLogger("rightfit.discovery_tasks")


async def _async_run_continuous_discovery(max_records_per_source: int = 50) -> Dict[str, Any]:
    """Async execution logic for background job discovery."""
    start_time = time.time()
    task_res: Dict[str, Any] = {
        "status": "SUCCESS",
        "sources_processed": 0,
        "records_inserted": 0,
        "records_updated": 0,
        "errors": [],
    }

    async with AsyncSessionLocal() as session:
        # 1. Fetch active schedule configs
        configs_query = select(DiscoveryScheduleConfigRecord).where(
            DiscoveryScheduleConfigRecord.is_paused == False
        )
        configs_res = await session.execute(configs_query)
        configs = configs_res.scalars().all()

        for cfg in configs:
            # Check if source exists in JobSourceRecord
            src_res = await session.execute(
                select(JobSourceRecord).where(JobSourceRecord.id == cfg.source_id)
            )
            source = src_res.scalar_one_or_none()

            # Record task execution start
            exec_record = DiscoveryTaskExecutionRecord(
                task_name="Continuous Job Discovery",
                task_type="JOB_DISCOVERY",
                source_id=cfg.source_id,
                status="RUNNING",
                started_at=utc_now(),
            )
            session.add(exec_record)
            await session.commit()
            await session.refresh(exec_record)

            try:
                if source and source.enabled:
                    limit = min(cfg.max_records_per_run, max_records_per_source)
                    trigger_res = await IngestionService.run_ingestion(
                        db=session,
                        source_id=source.id,
                        trigger_type="SCHEDULED_AUTO_REFRESH",
                        max_records=limit,
                    )
                    exec_record.status = "SUCCESS"
                    exec_record.records_fetched = trigger_res.records_fetched
                    exec_record.records_inserted = trigger_res.records_inserted
                    exec_record.records_updated = trigger_res.records_updated
                    task_res["records_inserted"] += trigger_res.records_inserted
                    task_res["records_updated"] += trigger_res.records_updated
                else:
                    exec_record.status = "SUCCESS"
                    exec_record.records_fetched = 0

                # Update next run timestamp
                cfg.last_run_at = utc_now()
                cfg.next_run_at = datetime.fromtimestamp(
                    time.time() + cfg.interval_seconds, tz=timezone.utc
                )
                task_res["sources_processed"] += 1

            except Exception as e:
                logger.error(f"Discovery error on source {cfg.source_id}: {e}")
                exec_record.status = "FAILED"
                exec_record.error_message = str(e)
                task_res["errors"].append({"source_id": cfg.source_id, "error": str(e)})

            finally:
                exec_record.completed_at = utc_now()
                exec_record.execution_duration_ms = int((time.time() - start_time) * 1000)
                await session.commit()

    return task_res


@celery_app.task(name="app.workers.tasks.discovery_tasks.run_continuous_job_discovery")
def run_continuous_job_discovery(max_records_per_source: int = 50) -> Dict[str, Any]:
    """Celery entrypoint for periodic continuous job discovery."""
    return asyncio.run(_async_run_continuous_discovery(max_records_per_source))


async def _async_check_connector_health() -> Dict[str, Any]:
    """Probes connector providers and persists health observability snapshots."""
    results = []
    async with AsyncSessionLocal() as session:
        sources_res = await session.execute(select(JobSourceRecord).where(JobSourceRecord.enabled == True))
        active_sources = sources_res.scalars().all()

        for src in active_sources:
            try:
                connector = get_connector(src.provider)
                health = await connector.check_health(src)
                status_str = "HEALTHY" if health.healthy else "DEGRADED"

                snapshot = ConnectorHealthSnapshotRecord(
                    connector_name=src.name,
                    provider_type=src.provider.upper(),
                    total_runs_count=1,
                    successful_runs_count=1 if health.healthy else 0,
                    failed_runs_count=0 if health.healthy else 1,
                    records_fetched_count=0,
                    records_inserted_count=0,
                    records_rejected_count=0,
                    rate_limit_events_count=0 if health.healthy else 1,
                    last_run_status="SUCCESS" if health.healthy else "FAILED",
                    last_run_at=utc_now(),
                    health_status=status_str,
                    degraded_reason=None if health.healthy else health.message,
                )
                session.add(snapshot)
                results.append({"connector": src.name, "healthy": health.healthy})
            except Exception as e:
                logger.warning(f"Health probe failed for {src.name}: {e}")

        await session.commit()
    return {"checked": len(results), "details": results}


@celery_app.task(name="app.workers.tasks.discovery_tasks.check_all_connector_health")
def check_all_connector_health() -> Dict[str, Any]:
    """Celery entrypoint for connector health observability."""
    return asyncio.run(_async_check_connector_health())

