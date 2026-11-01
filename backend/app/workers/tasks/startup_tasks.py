"""
RIGHT FIT Core — Continuous Startup Intelligence Discovery & Clustering Tasks
Version: 1.0.0
Master Implementation: Background Signals & Pain-Point Corroboration
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.db.models import (
    DiscoveryTaskExecutionRecord,
    StartupCorroborationRecord,
    StartupEvidenceRecord,
    StartupOpportunityRecord,
    utc_now,
)
from app.services.startup_service import StartupService
from app.workers.celery_app import celery_app

logger = logging.getLogger("rightfit.startup_tasks")


async def _async_run_continuous_startup_discovery() -> Dict[str, Any]:
    """Async background task to ingest new startup pain-point observations."""
    start_time = time.time()
    exec_record = DiscoveryTaskExecutionRecord(
        task_name="Continuous Startup Discovery",
        task_type="STARTUP_DISCOVERY",
        source_id="startup-hunter-satellite",
        status="RUNNING",
        started_at=utc_now(),
    )

    async with AsyncSessionLocal() as session:
        session.add(exec_record)
        await session.commit()
        await session.refresh(exec_record)

        try:
            # Live internet discovery across Hacker News, Reddit, GitHub, Dev.to, Google News
            from app.modules.startup_intelligence.service import StartupDiscoveryService
            discovered_leads = await StartupDiscoveryService.discover_leads(limit=25)
            stats = await StartupService.import_startup_leads(discovered_leads, session)
            exec_record.status = "SUCCESS"
            exec_record.records_inserted = stats.get("imported_count", 0)
            exec_record.records_updated = stats.get("updated_count", 0)
            return {"status": "SUCCESS", "stats": stats}

        except Exception as e:
            logger.error(f"Startup continuous discovery failed: {e}")
            exec_record.status = "FAILED"
            exec_record.error_message = str(e)
            return {"status": "FAILED", "error": str(e)}

        finally:
            exec_record.completed_at = utc_now()
            exec_record.execution_duration_ms = int((time.time() - start_time) * 1000)
            await session.commit()


@celery_app.task(name="app.workers.tasks.startup_tasks.run_continuous_startup_discovery")
def run_continuous_startup_discovery() -> Dict[str, Any]:
    """Celery entrypoint for periodic startup pain point discovery."""
    return asyncio.run(_async_run_continuous_startup_discovery())


async def _async_run_pain_point_clustering() -> Dict[str, Any]:
    """Clusters startup opportunities by domain and category, updating corroboration counts."""
    async with AsyncSessionLocal() as session:
        # Fetch all open discovered opportunities
        opps_res = await session.execute(select(StartupOpportunityRecord))
        opps = opps_res.scalars().all()

        clusters_updated = 0
        for opp in opps:
            # Count corroborating evidence records
            ev_count_res = await session.execute(
                select(func.count(StartupEvidenceRecord.id)).where(
                    StartupEvidenceRecord.opportunity_id == opp.id
                )
            )
            count = ev_count_res.scalar() or 0
            if count > 0 and opp.corroboration_count != count:
                opp.corroboration_count = count
                clusters_updated += 1

        await session.commit()
        return {"status": "SUCCESS", "clusters_updated": clusters_updated}


@celery_app.task(name="app.workers.tasks.startup_tasks.run_pain_point_clustering")
def run_pain_point_clustering() -> Dict[str, Any]:
    """Celery entrypoint for pain point observation clustering."""
    return asyncio.run(_async_run_pain_point_clustering())

