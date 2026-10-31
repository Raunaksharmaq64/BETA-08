"""
RIGHT FIT Core — Central Notifications & Preferences Endpoints
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import User
from app.services.notification_service import NotificationService
from contracts.applications.schemas import (
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    NotificationResponse,
)
from contracts.common.envelope import ResponseMeta, StandardResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id)


@router.get("", response_model=StandardResponse[List[NotificationResponse]])
async def list_notifications(
    request: Request,
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[NotificationResponse]]:
    """Lists candidate in-app notifications."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[NotificationResponse]:
        return NotificationService.list_notifications(
            session=session,
            user_id=current_user.id,
            unread_only=unread_only,
            limit=limit,
        )

    items = await db.run_sync(_sync_list)
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.patch("/{notification_id}/read", response_model=StandardResponse[Dict[str, Any]])
async def mark_notification_read(
    notification_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Marks a single notification as read."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_read(session: Session) -> bool:
        return NotificationService.mark_as_read(session=session, notification_id=notification_id, user_id=current_user.id)

    updated = await db.run_sync(_sync_read)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    return StandardResponse(data={"success": True, "message": "Notification marked as read."}, meta=make_meta(req_id))


@router.post("/mark-all-read", response_model=StandardResponse[Dict[str, Any]])
async def mark_all_notifications_read(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Marks all unread candidate notifications as read."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_all(session: Session) -> int:
        return NotificationService.mark_all_as_read(session=session, user_id=current_user.id)

    count = await db.run_sync(_sync_all)
    return StandardResponse(data={"success": True, "updated_count": count}, meta=make_meta(req_id))


@router.get("/preferences", response_model=StandardResponse[NotificationPreferencesResponse])
async def get_notification_preferences(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[NotificationPreferencesResponse]:
    """Retrieves candidate notification delivery preferences."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_pref(session: Session) -> NotificationPreferencesResponse:
        return NotificationService.get_preferences(session=session, user_id=current_user.id)

    pref = await db.run_sync(_sync_pref)
    return StandardResponse(data=pref, meta=make_meta(req_id))


@router.patch("/preferences", response_model=StandardResponse[NotificationPreferencesResponse])
async def update_notification_preferences(
    req: NotificationPreferencesUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[NotificationPreferencesResponse]:
    """Updates candidate category-level notification settings."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_upd(session: Session) -> NotificationPreferencesResponse:
        return NotificationService.update_preferences(session=session, user_id=current_user.id, req=req)

    pref = await db.run_sync(_sync_upd)
    return StandardResponse(data=pref, meta=make_meta(req_id))

