"""
RIGHT FIT Core — Freelance Opportunity & Outreach REST API Router
Version: 1.0.0
Phase: 9 — LeadHunter Integration
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models import User
from app.integrations.leadhunter.adapter import (
    LeadHunterUnavailableError,
    leadhunter_adapter,
)
from app.services.freelance_service import freelance_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/freelance", tags=["Freelance Opportunity Finder"])


# -----------------------------------------------------------------------------
# Request & Response Schemas
# -----------------------------------------------------------------------------

class LeadSearchScanRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Target business category (e.g. 'Dentists', 'Lawyers')")
    city: str = Field(..., min_length=2, description="Target city/metro area (e.g. 'Austin, TX', 'Indore')")
    max_results: int = Field(default=20, ge=1, le=100)
    include_with_website: bool = Field(default=False)
    deep_scan: bool = Field(default=True)


class SaveOpportunityRequest(BaseModel):
    notes: Optional[str] = None


class UpdateDraftRequest(BaseModel):
    subject: Optional[str] = None
    message_body: Optional[str] = None
    recipient_contact: Optional[str] = None


class AddSuppressionRequest(BaseModel):
    recipient_contact: str = Field(..., min_length=3)
    reason: str = Field(default="UNSUBSCRIBED")


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.get("", summary="List canonical freelance opportunities")
async def list_freelance_opportunities(
    city: Optional[str] = None,
    category: Optional[str] = None,
    classification_state: Optional[str] = None,
    query: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * per_page
    items = await freelance_service.list_opportunities(
        session=db,
        city=city,
        category=category,
        classification_state=classification_state,
        query=query,
        limit=per_page,
        offset=offset,
    )
    return {
        "success": True,
        "data": items,
        "page": page,
        "per_page": per_page,
        "count": len(items),
    }


@router.post("/scan-leads", summary="Trigger LeadHunter search scan & import leads into Core")
async def scan_and_import_leads(
    req: LeadSearchScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invokes the LeadHunter service through the authenticated adapter.
    Imports discovered leads into Core-owned canonical opportunities with contact evidence.
    Gracefully handles LeadHunter unavailability (circuit breaker fallback).
    """
    try:
        discovery_result = await leadhunter_adapter.search_leads(
            query=req.query,
            city=req.city,
            max_results=req.max_results,
            include_with_website=req.include_with_website,
            deep_scan=req.deep_scan,
        )
        imported_opportunities = []
        for lead in discovery_result.leads:
            opp = await freelance_service.import_lead_as_opportunity(db, lead)
            imported_opportunities.append(opp)

        return {
            "success": True,
            "degraded": False,
            "message": f"Successfully imported {len(imported_opportunities)} leads from LeadHunter.",
            "data": imported_opportunities,
        }
    except LeadHunterUnavailableError as e:
        logger.warning(f"[FreelanceAPI] LeadHunter unavailable: {e}. Serving cached/local opportunities.")
        # Return fallback local opportunities
        local_items = await freelance_service.list_opportunities(session=db, city=req.city, query=req.query, limit=10)
        return {
            "success": True,
            "degraded": True,
            "message": "LeadHunter service is currently offline or unreachable. Displaying cached local opportunities.",
            "data": local_items,
        }


@router.get("/integration-status", summary="Check LeadHunter integration connectivity and circuit breaker state")
async def get_integration_status(
    current_user: User = Depends(get_current_user),
):
    cb = leadhunter_adapter.circuit_breaker
    return {
        "success": True,
        "circuit_state": cb.state.value,
        "failure_count": cb.failure_count,
        "base_url": leadhunter_adapter.base_url,
        "degraded_mode_active": cb.state != "CLOSED",
    }


@router.get("/saved/all", summary="List candidate saved freelance opportunities")
async def get_saved_opportunities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_records = await freelance_service.get_saved_opportunities(db, user_id=current_user.id)
    return {"success": True, "data": saved_records}


@router.get("/{opportunity_id}", summary="Get opportunity details with contact evidence and drafts")
async def get_opportunity_detail(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opp = await freelance_service.get_opportunity_detail(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Freelance opportunity not found")
    return {"success": True, "data": opp}


@router.post("/{opportunity_id}/save", summary="Bookmark a freelance opportunity")
async def save_opportunity(
    opportunity_id: str,
    req: SaveOpportunityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved = await freelance_service.save_opportunity(
        db, user_id=current_user.id, opportunity_id=opportunity_id, notes=req.notes
    )
    return {"success": True, "data": saved}


@router.post("/{opportunity_id}/draft", summary="Generate a grounded outreach draft")
async def generate_draft(
    opportunity_id: str,
    channel: str = Query(default="EMAIL"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = await freelance_service.generate_outreach_draft(
        session=db, user_id=current_user.id, opportunity_id=opportunity_id, channel=channel
    )
    return {"success": True, "data": draft}


@router.put("/drafts/{draft_id}", summary="Edit draft (invalidates approval if approved)")
async def update_draft(
    draft_id: str,
    req: UpdateDraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated = await freelance_service.update_outreach_draft(
            session=db,
            user_id=current_user.id,
            draft_id=draft_id,
            subject=req.subject,
            message_body=req.message_body,
            recipient_contact=req.recipient_contact,
        )
        return {"success": True, "data": updated}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/drafts/{draft_id}/approve", summary="Explicit candidate approval of outreach draft")
async def approve_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        approved = await freelance_service.approve_outreach_draft(
            session=db, user_id=current_user.id, draft_id=draft_id
        )
        return {"success": True, "data": approved}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/drafts/{draft_id}/send", summary="Send approved outreach message")
async def send_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        delivery_log = await freelance_service.send_outreach_message(
            session=db, user_id=current_user.id, draft_id=draft_id
        )
        return {
            "success": True,
            "message": "Outreach message dispatched successfully.",
            "data": delivery_log,
        }
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/suppression", summary="Add recipient to suppression list")
async def add_suppression(
    req: AddSuppressionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await freelance_service.add_suppression(
        session=db,
        recipient_contact=req.recipient_contact,
        reason=req.reason,
        user_id=current_user.id,
    )
    return {"success": True, "data": record}
