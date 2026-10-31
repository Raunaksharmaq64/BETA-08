"""
RIGHT FIT Core — Application CRM & Lifecycle REST Endpoints
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import User
from app.services.crm_service import CRMService
from contracts.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationNoteCreate,
    ApplicationNoteResponse,
    ApplicationResponse,
    ApplicationStatsResponse,
    ApplicationTransitionRequest,
    ApplicationUpdateRequest,
)
from contracts.common.envelope import ResponseMeta, StandardResponse

router = APIRouter(prefix="/applications", tags=["Application CRM"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id)


@router.post("", response_model=StandardResponse[ApplicationResponse], status_code=status.HTTP_201_CREATED)
async def create_application(
    req: ApplicationCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationResponse]:
    """Creates a new job application tracking record."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_create(session: Session) -> ApplicationResponse:
        return CRMService.create_application(session=session, user_id=current_user.id, req=req)

    result = await db.run_sync(_sync_create)
    return StandardResponse(data=result, meta=make_meta(req_id))


@router.get("", response_model=StandardResponse[List[ApplicationResponse]])
async def list_applications(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. SAVED, APPLIED)"),
    search: Optional[str] = Query(None, description="Search company or title"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[ApplicationResponse]]:
    """Lists candidate job applications."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[ApplicationResponse]:
        return CRMService.list_applications(
            session=session,
            user_id=current_user.id,
            status=status_filter,
            search=search,
        )

    results = await db.run_sync(_sync_list)
    return StandardResponse(data=results, meta=make_meta(req_id))


@router.get("/stats", response_model=StandardResponse[ApplicationStatsResponse])
async def get_crm_stats(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationStatsResponse]:
    """Retrieves pipeline statistics across candidate application stages."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_stats(session: Session) -> ApplicationStatsResponse:
        return CRMService.get_stats(session=session, user_id=current_user.id)

    stats_data = await db.run_sync(_sync_stats)
    return StandardResponse(data=stats_data, meta=make_meta(req_id))


@router.get("/{application_id}", response_model=StandardResponse[ApplicationResponse])
async def get_application(
    application_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationResponse]:
    """Retrieves an application with complete status history and recent notes."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_get(session: Session) -> Optional[ApplicationResponse]:
        return CRMService.get_application(
            session=session,
            application_id=application_id,
            user_id=current_user.id,
        )

    result = await db.run_sync(_sync_get)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    return StandardResponse(data=result, meta=make_meta(req_id))


@router.patch("/{application_id}", response_model=StandardResponse[ApplicationResponse])
async def update_application(
    application_id: str,
    req: ApplicationUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationResponse]:
    """Updates editable application fields."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_update(session: Session) -> Optional[ApplicationResponse]:
        return CRMService.update_application(
            session=session,
            application_id=application_id,
            user_id=current_user.id,
            req=req,
        )

    updated = await db.run_sync(_sync_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    return StandardResponse(data=updated, meta=make_meta(req_id))


@router.delete("/{application_id}", response_model=StandardResponse[Dict[str, Any]])
async def delete_application(
    application_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Deletes an application and cascades its notes, status history, and reminders."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_delete(session: Session) -> bool:
        return CRMService.delete_application(
            session=session,
            application_id=application_id,
            user_id=current_user.id,
        )

    deleted = await db.run_sync(_sync_delete)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    return StandardResponse(data={"success": True, "message": "Application deleted."}, meta=make_meta(req_id))


@router.post("/{application_id}/transition", response_model=StandardResponse[ApplicationResponse])
async def transition_application_status(
    application_id: str,
    req: ApplicationTransitionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationResponse]:
    """
    Executes an auditable application state machine transition.
    Enforces candidate confirmation before setting APPLIED.
    """
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_transition(session: Session) -> ApplicationResponse:
        try:
            return CRMService.transition_status(
                session=session,
                application_id=application_id,
                user_id=current_user.id,
                req=req,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    result = await db.run_sync(_sync_transition)
    return StandardResponse(data=result, meta=make_meta(req_id))


@router.post("/{application_id}/apply-link-opened", response_model=StandardResponse[ApplicationResponse])
async def record_apply_link_opened(
    application_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationResponse]:
    """
    Records that candidate clicked/opened the external employer application URL.
    Transitions SAVED to PLANNING_TO_APPLY, but never automatically marks as APPLIED.
    """
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_open(session: Session) -> ApplicationResponse:
        try:
            return CRMService.record_apply_link_opened(
                session=session,
                application_id=application_id,
                user_id=current_user.id,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    result = await db.run_sync(_sync_open)
    return StandardResponse(data=result, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Application Notes Endpoints
# ------------------------------------------------------------------------------

@router.post("/{application_id}/notes", response_model=StandardResponse[ApplicationNoteResponse], status_code=status.HTTP_201_CREATED)
async def add_application_note(
    application_id: str,
    req: ApplicationNoteCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ApplicationNoteResponse]:
    """Adds a private note to candidate application."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_note(session: Session) -> ApplicationNoteResponse:
        try:
            return CRMService.add_note(
                session=session,
                application_id=application_id,
                user_id=current_user.id,
                req=req,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    result = await db.run_sync(_sync_note)
    return StandardResponse(data=result, meta=make_meta(req_id))


@router.get("/{application_id}/notes", response_model=StandardResponse[List[ApplicationNoteResponse]])
async def list_application_notes(
    application_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[ApplicationNoteResponse]]:
    """Lists all private notes for candidate application."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list_notes(session: Session) -> List[ApplicationNoteResponse]:
        return CRMService.list_notes(
            session=session,
            application_id=application_id,
            user_id=current_user.id,
        )

    results = await db.run_sync(_sync_list_notes)
    return StandardResponse(data=results, meta=make_meta(req_id))


@router.delete("/notes/{note_id}", response_model=StandardResponse[Dict[str, Any]])
async def delete_application_note(
    note_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Deletes a private application note."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_del(session: Session) -> bool:
        return CRMService.delete_note(
            session=session,
            note_id=note_id,
            user_id=current_user.id,
        )

    deleted = await db.run_sync(_sync_del)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")

    return StandardResponse(data={"success": True, "message": "Note deleted."}, meta=make_meta(req_id))

