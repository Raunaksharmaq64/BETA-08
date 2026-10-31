"""
RIGHT FIT Core — Continuous Link Verification & Deduplication Tasks
Version: 1.0.0
Master Implementation: Quality Assurance & Cross-Source Deduplication
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.db.models import (
    CanonicalOpportunityRecord,
    DataQualityAuditRecord,
    DiscoveryTaskExecutionRecord,
    utc_now,
)
from app.services.deduplication_service import DeduplicationService
from app.services.url_checker import URLCheckerService
from app.workers.celery_app import celery_app

logger = logging.getLogger("rightfit.verification_tasks")


async def _async_run_periodic_verification() -> Dict[str, Any]:
    """Runs automated reachability and broken-link audits across active listings."""
    start_time = time.time()
    exec_record = DiscoveryTaskExecutionRecord(
        task_name="Periodic Link Verification",
        task_type="JOB_VERIFICATION",
        source_id="job-link-verifier",
        status="RUNNING",
        started_at=utc_now(),
    )

    async with AsyncSessionLocal() as session:
        session.add(exec_record)
        await session.commit()
        await session.refresh(exec_record)

        try:
            # Query sample of active listings requiring verification
            query = select(CanonicalOpportunityRecord).where(
                CanonicalOpportunityRecord.is_active == True
            ).limit(50)
            res = await session.execute(query)
            jobs = res.scalars().all()

            checked_count = len(jobs)
            broken_count = 0

            for job in jobs:
                if not job.application_url:
                    continue
                # Fast HEAD probe check
                is_valid = await URLCheckerService.check_url_reachable(job.application_url)
                if not is_valid:
                    job.verification_status = "UNAVAILABLE"
                    broken_count += 1
                else:
                    job.verification_status = "VERIFIED_OPEN"
                job.last_checked_at = utc_now()

            # Record audit snapshot
            audit = DataQualityAuditRecord(
                total_active_listings=checked_count,
                duplicate_detection_count=0,
                broken_link_count=broken_count,
                broken_link_rate_pct=round((broken_count / max(1, checked_count)) * 100.0, 2),
                closed_listing_detection_count=broken_count,
            )
            session.add(audit)

            exec_record.status = "SUCCESS"
            exec_record.records_fetched = checked_count
            exec_record.records_updated = checked_count
            return {
                "status": "SUCCESS",
                "checked_count": checked_count,
                "broken_count": broken_count,
            }

        except Exception as e:
            logger.error(f"Link verification task failed: {e}")
            exec_record.status = "FAILED"
            exec_record.error_message = str(e)
            return {"status": "FAILED", "error": str(e)}

        finally:
            exec_record.completed_at = utc_now()
            exec_record.execution_duration_ms = int((time.time() - start_time) * 1000)
            await session.commit()


@celery_app.task(name="app.workers.tasks.verification_tasks.run_periodic_verification")
def run_periodic_verification() -> Dict[str, Any]:
    """Celery entrypoint for periodic link verification."""
    return asyncio.run(_async_run_periodic_verification())


async def _async_run_periodic_deduplication() -> Dict[str, Any]:
    """Executes cross-source duplicate detection sweep."""
    async with AsyncSessionLocal() as session:
        try:
            dedup_res = await DeduplicationService.detect_duplicates(session=session)
            return {"status": "SUCCESS", "dedup_results": dedup_res}
        except Exception as e:
            logger.error(f"Deduplication sweep error: {e}")
            return {"status": "FAILED", "error": str(e)}


@celery_app.task(name="app.workers.tasks.verification_tasks.run_periodic_deduplication")
def run_periodic_deduplication() -> Dict[str, Any]:
    """Celery entrypoint for periodic deduplication sweep."""
    return asyncio.run(_async_run_periodic_deduplication())

