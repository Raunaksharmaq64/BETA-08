"""
RIGHT FIT Core — Startup Intelligence & Opportunities REST API Router
Version: 1.0.0
Phase: 10 — Startup Intelligence Integration
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.models import User
from app.integrations.startup_intelligence.adapter import (
    StartupIntelligenceAdapter,
    StartupIntelligenceUnavailableError,
)
from app.services.startup_service import StartupService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/startups", tags=["Startup Intelligence"])
startup_adapter = StartupIntelligenceAdapter()


# -----------------------------------------------------------------------------
# Request & Response Schemas
# -----------------------------------------------------------------------------

class StartupScanRequest(BaseModel):
    category: Optional[str] = Field(default=None, description="Category filter (e.g. 'Performance', 'Development', 'AI')")
    min_score: Optional[int] = Field(default=None, ge=1, le=10, description="Minimum urgency score")
    source: Optional[str] = Field(default=None, description="Source platform name")
    limit: Optional[int] = Field(default=50, ge=1, le=200, description="Max leads to fetch and import")


class SaveStartupRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Candidate's private notes")


class GeneratePitchRequest(BaseModel):
    tone: str = Field(default="casual", description="Pitch tone: 'casual', 'formal', or 'short'")


class UpdatePitchRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    tone: Optional[str] = None


class WorkspaceUpdateRequest(BaseModel):
    target_persona: Optional[str] = None
    hypotheses: Optional[List[str]] = None
    competitor_notes: Optional[str] = None
    interview_questions: Optional[List[str]] = None
    validation_checklist: Optional[List[Dict[str, Any]]] = None
    solution_architecture: Optional[str] = None
    candidate_notes: Optional[str] = None


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.get("", summary="List canonical startup opportunities")
async def list_startup_opportunities(
    category: Optional[str] = None,
    min_score: Optional[int] = None,
    source: Optional[str] = None,
    technology: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    items, total = await StartupService.list_startup_opportunities(
        session=db,
        category=category,
        min_score=min_score,
        source=source,
        technology=technology,
        search=search,
        page=page,
        limit=per_page,
    )

    formatted_items = [
        {
            "id": opp.id,
            "service_record_id": opp.service_record_id,
            "startup_name": opp.startup_name,
            "domain": opp.domain,
            "website_url": opp.website_url,
            "category": opp.category,
            "detected_signal": opp.detected_signal,
            "pain_point_description": opp.pain_point_description,
            "urgency_score": opp.urgency_score,
            "score_explanation": opp.score_explanation,
            "primary_source": opp.primary_source,
            "source_url": opp.source_url,
            "status": opp.status,
            "corroboration_count": opp.corroboration_count,
            "has_conflicting_evidence": opp.has_conflicting_evidence,
            "validation_state": (
                "CUSTOMER_VALIDATION_REQUIRED" if opp.has_conflicting_evidence
                else "INDEPENDENTLY_CORROBORATED" if opp.corroboration_count >= 3
                else "REPEATED_OBSERVATIONS" if opp.corroboration_count >= 2
                else "OBSERVED_PROBLEM"
            ),
            "published_at": opp.published_at.isoformat() if opp.published_at else "Publication date unavailable",
            "first_seen_at": opp.first_seen_at.isoformat() if opp.first_seen_at else None,
        }
        for opp in items
    ]

    return {
        "success": True,
        "data": formatted_items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "count": len(formatted_items),
    }


@router.post("/scan-leads", summary="Trigger Startup Intelligence scan & import leads into Core")
async def scan_and_import_startup_leads(
    req: StartupScanRequest = StartupScanRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Invokes the independent Startup Intelligence service through the authenticated adapter.
    Imports discovered problems into Core-owned canonical opportunities with evidence and tech findings.
    Gracefully handles service downtime (circuit breaker fallback).
    """
    try:
        leads = await startup_adapter.list_leads(
            category=req.category,
            min_score=req.min_score,
            source=req.source,
            limit=req.limit,
        )
        import_stats = await StartupService.import_startup_leads(leads, db)
        return {
            "success": True,
            "degraded": False,
            "message": f"Successfully imported {import_stats['imported_count']} new startup opportunities ({import_stats['updated_count']} updated).",
            "stats": import_stats,
        }
    except StartupIntelligenceUnavailableError as exc:
        logger.warning(f"Startup Intelligence unavailable during scan: {exc}")
        # Degraded mode fallback: Core serves already-stored canonical opportunities
        return {
            "success": True,
            "degraded": True,
            "message": "Startup Intelligence satellite service is currently offline or unreachable. Displaying cached Core opportunities.",
            "stats": {"imported_count": 0, "updated_count": 0, "skipped_count": 0, "total_processed": 0},
        }
    except Exception as exc:
        logger.error(f"Unexpected error during startup scan: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Startup scan failed: {str(exc)}",
        )


@router.get("/saved/all", summary="List candidate's bookmarked startup opportunities")
async def list_saved_startups(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    saved = await StartupService.list_saved_startup_opportunities(current_user.id, db)
    return {
        "success": True,
        "data": saved,
        "count": len(saved),
    }


@router.get("/integration-status", summary="Startup Intelligence service health and circuit status")
async def get_startup_integration_status(
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    health = await startup_adapter.get_health()
    return {
        "success": True,
        "circuit_breaker": {
            "state": startup_adapter.circuit_breaker.state.value,
            "failure_count": startup_adapter.circuit_breaker.failure_count,
            "failure_threshold": startup_adapter.circuit_breaker.failure_threshold,
        },
        "upstream_health": health,
    }


@router.get("/{opportunity_id}", summary="Get deep details for a startup opportunity")
async def get_startup_opportunity_detail(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    detail = await StartupService.get_startup_opportunity_detail(opportunity_id, db)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Startup opportunity {opportunity_id} not found",
        )
    return {
        "success": True,
        "data": detail,
    }


@router.post("/{opportunity_id}/save", summary="Bookmark a startup opportunity")
async def save_startup(
    opportunity_id: str,
    req: SaveStartupRequest = SaveStartupRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved = await StartupService.save_startup_opportunity(
        user_id=current_user.id,
        opportunity_id=opportunity_id,
        notes=req.notes,
        session=db,
    )
    return {
        "success": True,
        "message": "Startup opportunity bookmarked successfully",
        "data": {"id": saved.id, "opportunity_id": saved.opportunity_id, "notes": saved.notes},
    }


@router.delete("/{opportunity_id}/save", summary="Remove a bookmarked startup opportunity")
async def unsave_startup(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    removed = await StartupService.unsave_startup_opportunity(
        user_id=current_user.id,
        opportunity_id=opportunity_id,
        session=db,
    )
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return {
        "success": True,
        "message": "Bookmark removed successfully",
    }


@router.post("/{opportunity_id}/pitch", summary="Generate pitch draft with explicit assumptions")
async def generate_pitch_draft(
    opportunity_id: str,
    req: GeneratePitchRequest = GeneratePitchRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        draft = await StartupService.generate_startup_pitch_draft(
            user_id=current_user.id,
            opportunity_id=opportunity_id,
            tone=req.tone,
            session=db,
        )
        return {
            "success": True,
            "message": "Pitch draft generated successfully. Explicit assumptions must be reviewed before candidate action.",
            "data": {
                "id": draft.id,
                "opportunity_id": draft.opportunity_id,
                "subject": draft.subject,
                "body": draft.body,
                "tone": draft.tone,
                "candidate_grounded_skills": draft.candidate_grounded_skills,
                "explicit_assumptions": draft.explicit_assumptions,
                "candidate_edits_count": draft.candidate_edits_count,
                "created_at": draft.created_at.isoformat() if draft.created_at else None,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/pitches/{pitch_id}", summary="Update candidate pitch draft")
async def update_pitch_draft(
    pitch_id: str,
    req: UpdatePitchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        draft = await StartupService.update_startup_pitch_draft(
            draft_id=pitch_id,
            user_id=current_user.id,
            subject=req.subject,
            body=req.body,
            tone=req.tone,
            session=db,
        )
        return {
            "success": True,
            "message": "Pitch draft updated successfully",
            "data": {
                "id": draft.id,
                "subject": draft.subject,
                "body": draft.body,
                "tone": draft.tone,
                "candidate_edits_count": draft.candidate_edits_count,
                "updated_at": draft.updated_at.isoformat() if draft.updated_at else None,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{opportunity_id}/workspace", summary="Get or initialize candidate's Opportunity Workspace canvas")
async def get_opportunity_workspace(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ws = await StartupService.get_or_create_workspace(
            opportunity_id=opportunity_id,
            user_id=current_user.id,
            session=db,
        )
        return {"success": True, "data": ws}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/{opportunity_id}/workspace", summary="Update candidate's Opportunity Workspace canvas")
async def update_opportunity_workspace(
    opportunity_id: str,
    req: WorkspaceUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        update_data = {k: v for k, v in req.model_dump().items() if v is not None}
        ws = await StartupService.update_workspace(
            opportunity_id=opportunity_id,
            user_id=current_user.id,
            update_data=update_data,
            session=db,
        )
        return {"success": True, "data": ws, "message": "Workspace canvas updated successfully"}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

