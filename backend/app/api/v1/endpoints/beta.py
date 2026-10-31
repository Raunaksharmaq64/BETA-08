"""
RIGHT FIT Core — Phase 14: Beta Validation & Telemetry REST API Router
Version: 1.0.0
Exposes structured feedback intake, consent management, connector health,
data quality audits, source governance, and release documentation.
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
from app.services.beta_validation_service import BetaValidationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/beta", tags=["Beta Validation & Telemetry"])


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------

class FeedbackSubmitRequest(BaseModel):
    category: str = Field(..., description="Category of feedback (e.g. SEARCH_RELEVANCE, BROKEN_APPLICATION_LINK, PERFORMANCE)")
    description: str = Field(..., min_length=5, max_length=5000, description="Detailed user feedback description")
    related_feature: str = Field(default="GENERAL", description="Associated feature module")
    related_record_id: Optional[str] = Field(default=None, description="Optional ID of opportunity or record")
    severity: str = Field(default="MEDIUM", description="Severity: LOW, MEDIUM, HIGH, CRITICAL")


class FeedbackUpdateRequest(BaseModel):
    review_status: str = Field(..., description="Status: NEW, IN_REVIEW, TRIAGED, RESOLVED, WONT_FIX")
    resolution_notes: Optional[str] = Field(default=None, description="Triage or engineering resolution notes")
    responsible_owner: Optional[str] = Field(default=None, description="Assigned engineering owner")


class ConsentRecordRequest(BaseModel):
    consent_version: str = Field(default="v1.0-beta", description="Beta consent document version")
    has_consented_data_collection: bool = Field(default=True)
    has_consented_ai_processing: bool = Field(default=True)
    has_consented_anonymized_analytics: bool = Field(default=True)


# -----------------------------------------------------------------------------
# Feedback Endpoints
# -----------------------------------------------------------------------------

@router.post("/feedback", status_code=status.HTTP_201_CREATED, summary="Submit user feedback")
async def submit_feedback(
    payload: FeedbackSubmitRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submits structured feedback. Supports authenticated users or anonymous submissions without unnecessary PII."""
    user_id = current_user.id if current_user else None
    result = await BetaValidationService.submit_feedback(
        session=db,
        category=payload.category,
        description=payload.description,
        user_id=user_id,
        related_feature=payload.related_feature,
        related_record_id=payload.related_record_id,
        severity=payload.severity,
    )
    return {
        "success": True,
        "message": "Feedback recorded successfully. Thank you for helping improve RIGHT FIT.",
        "data": result,
    }


@router.get("/feedback", summary="List feedback items")
async def list_feedback(
    review_status: Optional[str] = Query(default=None, description="Filter by status (NEW, TRIAGED, RESOLVED)"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Returns submitted feedback items for quality analysis and triage."""
    result = await BetaValidationService.list_feedback(
        session=db,
        review_status=review_status,
        category=category,
        limit=limit,
        offset=offset,
    )
    return {
        "success": True,
        "data": result,
    }


@router.patch("/feedback/{feedback_id}", summary="Update feedback triage status")
async def update_feedback(
    feedback_id: str,
    payload: FeedbackUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates feedback review status and records resolution notes."""
    try:
        result = await BetaValidationService.update_feedback_status(
            session=db,
            feedback_id=feedback_id,
            review_status=payload.review_status,
            resolution_notes=payload.resolution_notes,
            responsible_owner=payload.responsible_owner or current_user.email,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------------------------------------------------------
# Consent Lifecycle Endpoints
# -----------------------------------------------------------------------------

@router.post("/consent", summary="Record beta consent")
async def record_consent(
    payload: ConsentRecordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Records explicit user consent for beta participation with 90-day retention horizon."""
    result = await BetaValidationService.record_consent(
        session=db,
        user_id=current_user.id,
        consent_version=payload.consent_version,
        has_consented_data_collection=payload.has_consented_data_collection,
        has_consented_ai_processing=payload.has_consented_ai_processing,
        has_consented_anonymized_analytics=payload.has_consented_anonymized_analytics,
    )
    return {
        "success": True,
        "data": result,
    }


@router.get("/consent", summary="Get user beta consent status")
async def get_consent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves current user's active consent record."""
    consent = await BetaValidationService.get_consent(session=db, user_id=current_user.id)
    return {
        "success": True,
        "data": consent,
    }


@router.post("/consent/withdraw", summary="Withdraw beta consent")
async def withdraw_consent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Withdraws user consent and initiates scheduled data minimization."""
    try:
        result = await BetaValidationService.withdraw_consent(session=db, user_id=current_user.id)
        return {
            "success": True,
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Connector Health & Data Quality Endpoints
# -----------------------------------------------------------------------------

@router.get("/connectors", summary="Get connector reliability and execution metrics")
async def get_connector_health(
    db: AsyncSession = Depends(get_db),
):
    """Provides empirical execution frequency, success rates, duration, and rejection counts."""
    metrics = await BetaValidationService.get_connector_health_metrics(session=db)
    return {
        "success": True,
        "data": metrics,
    }


@router.get("/quality", summary="Get data quality and deduplication metrics")
async def get_data_quality(
    db: AsyncSession = Depends(get_db),
):
    """Provides duplicate detection rates, confirmed duplicates, broken link rates, and closed listing counts."""
    metrics = await BetaValidationService.get_data_quality_metrics(session=db)
    return {
        "success": True,
        "data": metrics,
    }


@router.get("/source-governance", summary="Get source compliance and retirement report")
async def get_source_governance(
    db: AsyncSession = Depends(get_db),
):
    """Audits all registered ingestion sources against terms of service, rate limits, and compliance."""
    report = await BetaValidationService.get_source_governance_report(session=db)
    return {
        "success": True,
        "data": report,
    }


@router.get("/release-notes", summary="Get product release notes and known limitations")
async def get_release_notes():
    """Returns honest disclosure of verified capabilities, known limitations, and operational status."""
    notes = BetaValidationService.get_release_notes_and_limitations()
    return {
        "success": True,
        "data": notes,
    }

