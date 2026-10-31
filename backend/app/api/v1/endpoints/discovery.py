"""
RIGHT FIT Core — Continuous Discovery & Live Auto-Refresh REST API Router
Version: 1.0.0
Master Implementation: Discovery Status, Manual Trigger, Schedule Controls & Live SSE Stream
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_current_user
from app.db.models import (
    CanonicalOpportunityRecord,
    DiscoveryScheduleConfigRecord,
    DiscoveryTaskExecutionRecord,
    JobSourceRecord,
    StartupOpportunityRecord,
    User,
    utc_now,
)
from app.workers.tasks.discovery_tasks import _async_run_continuous_discovery
from app.workers.tasks.startup_tasks import _async_run_continuous_startup_discovery
from contracts.common.envelope import ResponseMeta, StandardResponse

logger = logging.getLogger("rightfit.discovery_api")
router = APIRouter(prefix="/discovery", tags=["Continuous Discovery & Auto-Refresh"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id, service="continuous_discovery_engine")


# ==============================================================================
# DTO Models
# ==============================================================================

class ScheduleConfigUpdate(BaseModel):
    interval_seconds: Optional[int] = Field(default=None, ge=60, le=86400)
    max_records_per_run: Optional[int] = Field(default=None, ge=5, le=500)
    rate_limit_per_minute: Optional[int] = Field(default=None, ge=1, le=300)
    is_paused: Optional[bool] = None


class ManualRefreshRequest(BaseModel):
    source_id: Optional[str] = None
    opportunity_type: str = "ALL"  # ALL, JOBS, STARTUPS


# In-memory cooldown tracking for manual refresh (per user/IP: max once per 30s)
_MANUAL_REFRESH_COOLDOWN: Dict[str, float] = {}


# ==============================================================================
# Endpoints
# ==============================================================================

@router.get("/status", summary="Discovery system operational status and schedule overview")
async def get_discovery_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> StandardResponse[Dict[str, Any]]:
    """Returns background discovery engine status, active schedules, and recent task executions."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 1. Fetch Schedule Configs
    configs_res = await db.execute(select(DiscoveryScheduleConfigRecord))
    configs = configs_res.scalars().all()

    # 2. Fetch Recent Executions
    execs_res = await db.execute(
        select(DiscoveryTaskExecutionRecord)
        .order_by(desc(DiscoveryTaskExecutionRecord.created_at))
        .limit(10)
    )
    executions = execs_res.scalars().all()

    # 3. Aggregate totals
    total_jobs_res = await db.execute(select(func.count(CanonicalOpportunityRecord.id)))
    total_jobs = total_jobs_res.scalar() or 0

    total_startups_res = await db.execute(select(func.count(StartupOpportunityRecord.id)))
    total_startups = total_startups_res.scalar() or 0

    all_paused = all(c.is_paused for c in configs) if configs else False

    payload = {
        "engine_state": "PAUSED" if all_paused else "ACTIVE",
        "total_active_sources": len([c for c in configs if not c.is_paused]),
        "total_sources_configured": len(configs),
        "total_opportunities_discovered": {
            "jobs": total_jobs,
            "startups": total_startups,
            "total": total_jobs + total_startups,
        },
        "schedules": [
            {
                "source_id": c.source_id,
                "source_name": c.source_name,
                "interval_seconds": c.interval_seconds,
                "is_paused": c.is_paused,
                "max_records": c.max_records_per_run,
                "last_run_at": c.last_run_at.isoformat() if c.last_run_at else None,
                "next_run_at": c.next_run_at.isoformat() if c.next_run_at else None,
            }
            for c in configs
        ],
        "recent_executions": [
            {
                "id": ex.id,
                "task_name": ex.task_name,
                "task_type": ex.task_type,
                "source_id": ex.source_id,
                "status": ex.status,
                "records_fetched": ex.records_fetched,
                "records_inserted": ex.records_inserted,
                "records_updated": ex.records_updated,
                "duration_ms": ex.execution_duration_ms,
                "started_at": ex.started_at.isoformat() if ex.started_at else None,
                "completed_at": ex.completed_at.isoformat() if ex.completed_at else None,
            }
            for ex in executions
        ],
        "server_time": utc_now().isoformat(),
    }

    return StandardResponse(data=payload, meta=make_meta(req_id))


@router.post("/refresh", summary="Trigger permitted manual discovery refresh")
async def trigger_manual_refresh(
    payload: ManualRefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[Dict[str, Any]]:
    """Triggers an on-demand discovery run with rate-limiting and quota controls (30s cooldown)."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_key = f"{current_user.id}:{payload.opportunity_type}"
    now_ts = time.time()

    # Rate limiting / cooldown check: 30 seconds
    last_time = _MANUAL_REFRESH_COOLDOWN.get(user_key, 0.0)
    cooldown_remaining = int(30.0 - (now_ts - last_time))
    if cooldown_remaining > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Manual refresh cooldown active. Please wait {cooldown_remaining} seconds.",
        )

    _MANUAL_REFRESH_COOLDOWN[user_key] = now_ts
    results: Dict[str, Any] = {"jobs_result": None, "startups_result": None}

    if payload.opportunity_type in ("ALL", "JOBS"):
        results["jobs_result"] = await _async_run_continuous_discovery(max_records_per_source=25)

    if payload.opportunity_type in ("ALL", "STARTUPS"):
        results["startups_result"] = await _async_run_continuous_startup_discovery()

    return StandardResponse(
        data={
            "status": "COMPLETED",
            "triggered_by": current_user.email,
            "opportunity_type": payload.opportunity_type,
            "results": results,
            "refreshed_at": utc_now().isoformat(),
        },
        meta=make_meta(req_id),
    )


@router.post("/pause", summary="Pause discovery runs globally or per source")
async def pause_discovery(
    source_id: Optional[str] = Query(default=None, description="Specific source to pause; omit for global pause"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[Dict[str, Any]]:
    """Pauses background discovery execution."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())

    if source_id:
        await db.execute(
            update(DiscoveryScheduleConfigRecord)
            .where(DiscoveryScheduleConfigRecord.source_id == source_id)
            .values(is_paused=True)
        )
        msg = f"Discovery for source '{source_id}' has been paused."
    else:
        await db.execute(
            update(DiscoveryScheduleConfigRecord).values(is_paused=True)
        )
        msg = "Discovery paused globally across all configured sources."

    await db.commit()
    return StandardResponse(data={"message": msg, "is_paused": True}, meta=make_meta(req_id))


@router.post("/resume", summary="Resume discovery runs globally or per source")
async def resume_discovery(
    source_id: Optional[str] = Query(default=None, description="Specific source to resume; omit for global resume"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[Dict[str, Any]]:
    """Resumes background discovery execution."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())

    if source_id:
        await db.execute(
            update(DiscoveryScheduleConfigRecord)
            .where(DiscoveryScheduleConfigRecord.source_id == source_id)
            .values(is_paused=False, next_run_at=utc_now())
        )
        msg = f"Discovery for source '{source_id}' resumed and scheduled for immediate execution."
    else:
        await db.execute(
            update(DiscoveryScheduleConfigRecord).values(is_paused=False, next_run_at=utc_now())
        )
        msg = "Discovery resumed globally across all sources."

    await db.commit()
    return StandardResponse(data={"message": msg, "is_paused": False}, meta=make_meta(req_id))


@router.get("/config", summary="List configurable refresh parameters per source")
async def list_discovery_configs(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> StandardResponse[List[Dict[str, Any]]]:
    """Lists per-source schedule configurations."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    res = await db.execute(select(DiscoveryScheduleConfigRecord))
    configs = res.scalars().all()

    data = [
        {
            "id": c.id,
            "source_id": c.source_id,
            "source_name": c.source_name,
            "interval_seconds": c.interval_seconds,
            "is_paused": c.is_paused,
            "max_records_per_run": c.max_records_per_run,
            "rate_limit_per_minute": c.rate_limit_per_minute,
            "last_run_at": c.last_run_at.isoformat() if c.last_run_at else None,
            "next_run_at": c.next_run_at.isoformat() if c.next_run_at else None,
        }
        for c in configs
    ]
    return StandardResponse(data=data, meta=make_meta(req_id))


@router.put("/config/{source_id}", summary="Update discovery configuration for a source")
async def update_discovery_config(
    source_id: str,
    payload: ScheduleConfigUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[Dict[str, Any]]:
    """Updates interval, rate limits, or pause state for a specific source."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    res = await db.execute(
        select(DiscoveryScheduleConfigRecord).where(
            DiscoveryScheduleConfigRecord.source_id == source_id
        )
    )
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail=f"Config for source '{source_id}' not found.")

    if payload.interval_seconds is not None:
        config.interval_seconds = payload.interval_seconds
    if payload.max_records_per_run is not None:
        config.max_records_per_run = payload.max_records_per_run
    if payload.rate_limit_per_minute is not None:
        config.rate_limit_per_minute = payload.rate_limit_per_minute
    if payload.is_paused is not None:
        config.is_paused = payload.is_paused

    config.updated_at = utc_now()
    await db.commit()
    await db.refresh(config)

    return StandardResponse(
        data={
            "source_id": config.source_id,
            "interval_seconds": config.interval_seconds,
            "is_paused": config.is_paused,
            "max_records_per_run": config.max_records_per_run,
            "message": f"Configuration for source '{source_id}' updated successfully.",
        },
        meta=make_meta(req_id),
    )


@router.get("/events", summary="Live Server-Sent Events (SSE) feed for auto-refresh")
async def discovery_events_stream(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Server-Sent Events (SSE) stream delivering real-time discovery notifications
    to the frontend without full browser reloads.
    """
    async def event_generator():
        try:
            # Send initial handshake event
            initial_data = {
                "event_type": "CONNECTED",
                "message": "Connected to RIGHT FIT Live Continuous Discovery Stream",
                "timestamp": utc_now().isoformat(),
            }
            yield f"data: {json.dumps(initial_data)}\n\n"

            last_job_id = None
            last_startup_id = None

            # Stream updates every 5 seconds
            while True:
                if await request.is_disconnected():
                    break

                # Query latest job ID
                latest_job = await db.execute(
                    select(CanonicalOpportunityRecord.id, CanonicalOpportunityRecord.title, CanonicalOpportunityRecord.company_name)
                    .order_by(desc(CanonicalOpportunityRecord.first_seen_at))
                    .limit(1)
                )
                job_row = latest_job.first()

                if job_row and job_row[0] != last_job_id:
                    if last_job_id is not None:
                        event_payload = {
                            "event_type": "NEW_JOB_DISCOVERED",
                            "job_id": job_row[0],
                            "title": job_row[1],
                            "company": job_row[2],
                            "timestamp": utc_now().isoformat(),
                        }
                        yield f"data: {json.dumps(event_payload)}\n\n"
                    last_job_id = job_row[0]

                # Query latest startup signal ID
                latest_st = await db.execute(
                    select(StartupOpportunityRecord.id, StartupOpportunityRecord.startup_name, StartupOpportunityRecord.detected_signal)
                    .order_by(desc(StartupOpportunityRecord.first_seen_at))
                    .limit(1)
                )
                st_row = latest_st.first()

                if st_row and st_row[0] != last_startup_id:
                    if last_startup_id is not None:
                        event_payload = {
                            "event_type": "NEW_STARTUP_SIGNAL",
                            "startup_id": st_row[0],
                            "startup_name": st_row[1],
                            "signal": st_row[2],
                            "timestamp": utc_now().isoformat(),
                        }
                        yield f"data: {json.dumps(event_payload)}\n\n"
                    last_startup_id = st_row[0]

                # Heartbeat keep-alive ping
                yield f": keep-alive {utc_now().isoformat()}\n\n"
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

