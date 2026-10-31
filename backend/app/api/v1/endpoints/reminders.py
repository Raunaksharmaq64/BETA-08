"""
RIGHT FIT Core — Reminders, Calendar & Conflict Tracking Endpoints
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import User
from app.services.reminder_service import ReminderService, ensure_utc
from contracts.applications.schemas import (
    CalendarEventResponse,
    ReminderCreateRequest,
    ReminderResponse,
    ScheduleConflictCheck,
)
from contracts.common.envelope import ResponseMeta, StandardResponse

router = APIRouter(tags=["Reminders & Calendar"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id)


@router.post("/reminders", response_model=StandardResponse[ReminderResponse], status_code=status.HTTP_201_CREATED)
async def create_reminder(
    req: ReminderCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ReminderResponse]:
    """Schedules a new reminder with candidate IANA timezone metadata."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_create(session: Session) -> ReminderResponse:
        try:
            return ReminderService.create_reminder(session=session, user_id=current_user.id, req=req)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    res = await db.run_sync(_sync_create)
    return StandardResponse(data=res, meta=make_meta(req_id))


@router.get("/reminders", response_model=StandardResponse[List[ReminderResponse]])
async def list_reminders(
    request: Request,
    is_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[ReminderResponse]]:
    """Lists candidate reminders."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[ReminderResponse]:
        return ReminderService.list_reminders(session=session, user_id=current_user.id, is_completed=is_completed)

    items = await db.run_sync(_sync_list)
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.patch("/reminders/{reminder_id}/complete", response_model=StandardResponse[ReminderResponse])
async def complete_reminder(
    reminder_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ReminderResponse]:
    """Marks a reminder as completed."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_complete(session: Session) -> Optional[ReminderResponse]:
        return ReminderService.complete_reminder(session=session, reminder_id=reminder_id, user_id=current_user.id)

    res = await db.run_sync(_sync_complete)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")

    return StandardResponse(data=res, meta=make_meta(req_id))


@router.delete("/reminders/{reminder_id}", response_model=StandardResponse[Dict[str, Any]])
async def delete_reminder(
    reminder_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Deletes a reminder."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_del(session: Session) -> bool:
        return ReminderService.delete_reminder(session=session, reminder_id=reminder_id, user_id=current_user.id)

    deleted = await db.run_sync(_sync_del)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")

    return StandardResponse(data={"success": True, "message": "Reminder deleted."}, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Calendar Events & Conflict Checking
# ------------------------------------------------------------------------------

@router.get("/calendar/events", response_model=StandardResponse[List[CalendarEventResponse]])
async def get_calendar_events(
    request: Request,
    start: Optional[datetime] = Query(None, description="Start date in UTC"),
    end: Optional[datetime] = Query(None, description="End date in UTC"),
    tz: str = Query("UTC", description="Candidate IANA timezone, e.g. Asia/Kolkata"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[CalendarEventResponse]]:
    """Aggregates scheduled reminders and interview rounds."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_events(session: Session) -> List[CalendarEventResponse]:
        return ReminderService.get_calendar_events(
            session=session,
            user_id=current_user.id,
            start_utc=start,
            end_utc=end,
            candidate_timezone=tz,
        )

    events = await db.run_sync(_sync_events)
    return StandardResponse(data=events, meta=make_meta(req_id))


@router.get("/calendar/conflicts", response_model=StandardResponse[ScheduleConflictCheck])
async def check_schedule_conflicts(
    time: datetime = Query(..., description="Target scheduled time in UTC"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Estimated duration in minutes"),
    request: Request = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ScheduleConflictCheck]:
    """Detects schedule conflicts against candidate existing reminders and interview rounds."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_conflict(session: Session) -> ScheduleConflictCheck:
        return ReminderService.check_schedule_conflicts(
            session=session,
            user_id=current_user.id,
            target_time_utc=time,
            duration_minutes=duration_minutes,
        )

    check = await db.run_sync(_sync_conflict)
    return StandardResponse(data=check, meta=make_meta(req_id))

