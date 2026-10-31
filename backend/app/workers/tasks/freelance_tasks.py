"""
RIGHT FIT Core — Celery Background Tasks for Freelance Intelligence
Queue: lead_tasks
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from app.core.database import async_session_maker
from app.workers.celery_app import celery_app

logger = logging.getLogger("rightfit.workers.freelance")


@celery_app.task(name="app.workers.tasks.freelance_tasks.run_background_freelance_search", bind=True)
def run_background_freelance_search(
    self,
    user_id: str,
    query: str,
    city: str,
    max_results: int = 20,
    include_with_website: bool = False,
    deep_scan: bool = False,
    zones: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Execute freelance business discovery asynchronously on lead_tasks queue."""
    from app.modules.freelance.services.discovery_service import FreelanceDiscoveryService

    async def _run():
        async with async_session_maker() as session:
            try:
                res = await FreelanceDiscoveryService.discover_leads(
                    session=session,
                    user_id=user_id,
                    query=query,
                    city=city,
                    max_results=max_results,
                    include_with_website=include_with_website,
                    deep_scan=deep_scan,
                    zones=zones,
                )
                await session.commit()
                return res
            except Exception as e:
                await session.rollback()
                logger.error(f"[FreelanceTask] Background search failed: {e}", exc_info=True)
                raise e

    return asyncio.run(_run())


@celery_app.task(name="app.workers.tasks.freelance_tasks.run_opportunity_audit_task", bind=True)
def run_opportunity_audit_task(self, opportunity_id: str) -> Dict[str, Any]:
    """Execute technical website audit asynchronously."""
    from app.modules.freelance.services.audit_service import FreelanceAuditService

    async def _run():
        async with async_session_maker() as session:
            try:
                res = await FreelanceAuditService.audit_opportunity(session, opportunity_id)
                await session.commit()
                return res
            except Exception as e:
                await session.rollback()
                logger.error(f"[FreelanceTask] Opportunity audit failed: {e}", exc_info=True)
                raise e

    return asyncio.run(_run())
