"""
RIGHT FIT Core — Verification, Deduplication & Data Quality Endpoints
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import (
    CanonicalOpportunityRecord,
    DuplicateCandidateRecord,
    MergeDecisionRecord,
    OpportunitySourceMappingRecord,
    User,
    UserListingFeedbackRecord,
    VerificationEvidenceRecord,
)
from app.services.deduplication_service import DeduplicationService
from app.services.feedback_service import FeedbackService
from app.services.quality_service import QualityService
from app.services.verification_service import VerificationService
from contracts.common.envelope import ResponseMeta, StandardResponse
from contracts.verification.schemas import (
    DuplicateCandidateResponse,
    FeedbackStatus,
    FeedbackType,
    FreshnessState,
    MatchTier,
    MergeActionRequest,
    MergeStatus,
    OpportunityVerificationDetailResponse,
    QualityMetricsResponse,
    SourceMappingResponse,
    UnmergeActionRequest,
    UserFeedbackCreateRequest,
    UserFeedbackResponse,
    VerificationEvidenceResponse,
    VerificationStatus,
    VerificationTriggerRequest,
)

router = APIRouter(tags=["Verification & Data Quality Intelligence"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id, service="core_career_engine")


def _to_evidence_response(ev: VerificationEvidenceRecord) -> VerificationEvidenceResponse:
    return VerificationEvidenceResponse(
        id=ev.id,
        opportunity_id=ev.opportunity_id,
        source_id=ev.source_id,
        check_id=ev.check_id,
        check_timestamp=ev.check_timestamp,
        check_method=ev.check_method,
        check_outcome=ev.check_outcome,
        http_status=ev.http_status,
        provider_status=ev.provider_status,
        evidence_category=ev.evidence_category,
        evidence_reference=ev.evidence_reference,
        safe_response_metadata=ev.safe_response_metadata_json or {},
        verification_rule_version=ev.verification_rule_version,
        confidence_category=ev.confidence_category,
        error_category=ev.error_category,
        next_eligible_check_at=ev.next_eligible_check_at,
    )


def _to_verification_detail(opp: CanonicalOpportunityRecord, evidence_history: List[VerificationEvidenceRecord]) -> OpportunityVerificationDetailResponse:
    user_friendly_status, user_explanation = VerificationService.get_user_explanation(opp)
    return OpportunityVerificationDetailResponse(
        opportunity_id=opp.id,
        verification_status=VerificationStatus(opp.verification_status),
        freshness_state=FreshnessState(opp.freshness_state),
        user_friendly_status=user_friendly_status,
        user_explanation=user_explanation,
        published_at=opp.source_published_at,
        source_updated_at=opp.source_updated_at,
        first_seen_at=opp.first_seen_at,
        last_seen_at=opp.last_seen_at,
        last_checked_at=opp.last_checked_at,
        last_successful_check_at=opp.last_successful_check_at,
        last_verified_at=opp.last_verified_at,
        status_changed_at=opp.status_changed_at,
        closed_at=opp.closed_at,
        expires_at=opp.expires_at,
        is_suppressed=opp.is_suppressed,
        evidence_history=[_to_evidence_response(e) for e in evidence_history],
    )


# ------------------------------------------------------------------------------
# Verification Endpoints
# ------------------------------------------------------------------------------

@router.get("/opportunities/{opportunity_id}/verification", response_model=StandardResponse[OpportunityVerificationDetailResponse])
async def get_opportunity_verification(
    opportunity_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[OpportunityVerificationDetailResponse]:
    """Retrieves full verification timeline, independent timestamps, and evidence trail for an opportunity."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_fetch(session: Session):
        opp = session.get(CanonicalOpportunityRecord, opportunity_id)
        if not opp:
            return None
        evidence = session.execute(
            select(VerificationEvidenceRecord)
            .where(VerificationEvidenceRecord.opportunity_id == opportunity_id)
            .order_by(VerificationEvidenceRecord.check_timestamp.desc())
        ).scalars().all()
        return _to_verification_detail(opp, list(evidence))

    detail = await db.run_sync(_sync_fetch)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Opportunity '{opportunity_id}' not found")

    return StandardResponse(data=detail, meta=make_meta(req_id))


@router.post("/opportunities/{opportunity_id}/verify", response_model=StandardResponse[OpportunityVerificationDetailResponse])
async def trigger_opportunity_verification(
    opportunity_id: str,
    payload: VerificationTriggerRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[OpportunityVerificationDetailResponse]:
    """Triggers an on-demand verification check for an opportunity with evidence logging."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_verify(session: Session):
        opp = VerificationService.verify_opportunity(
            db=session,
            opportunity_id=opportunity_id,
            force=payload.force,
            check_method=payload.check_method,
        )
        evidence = session.execute(
            select(VerificationEvidenceRecord)
            .where(VerificationEvidenceRecord.opportunity_id == opportunity_id)
            .order_by(VerificationEvidenceRecord.check_timestamp.desc())
        ).scalars().all()
        return _to_verification_detail(opp, list(evidence))

    try:
        detail = await db.run_sync(_sync_verify)
        return StandardResponse(data=detail, meta=make_meta(req_id))
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))


# ------------------------------------------------------------------------------
# Feedback Endpoints
# ------------------------------------------------------------------------------

@router.post("/opportunities/{opportunity_id}/feedback", response_model=StandardResponse[UserFeedbackResponse], status_code=status.HTTP_201_CREATED)
async def submit_opportunity_feedback(
    opportunity_id: str,
    payload: UserFeedbackCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[UserFeedbackResponse]:
    """Submits candidate or user feedback regarding listing inaccuracies, broken links, or closures."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    client_ip = request.client.host if request.client else "unknown"

    def _sync_feedback(session: Session):
        return FeedbackService.submit_feedback(
            db=session,
            opportunity_id=opportunity_id,
            feedback_type=payload.feedback_type,
            notes=payload.notes,
            user_id=None,
            client_ip=client_ip,
            auto_verify=True,
        )

    try:
        fb = await db.run_sync(_sync_feedback)
        resp = UserFeedbackResponse(
            id=fb.id,
            opportunity_id=fb.opportunity_id,
            user_id=fb.user_id,
            feedback_type=FeedbackType(fb.feedback_type),
            notes=fb.notes,
            status=FeedbackStatus(fb.status),
            created_at=fb.created_at,
        )
        return StandardResponse(data=resp, meta=make_meta(req_id))
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except PermissionError as perm_err:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(perm_err))


@router.get("/opportunities/{opportunity_id}/feedback", response_model=StandardResponse[List[UserFeedbackResponse]])
async def get_opportunity_feedbacks(
    opportunity_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[UserFeedbackResponse]]:
    """Retrieves all feedback records for an opportunity."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session):
        return FeedbackService.list_feedbacks_for_opportunity(session, opportunity_id)

    feedbacks = await db.run_sync(_sync_list)
    items = [
        UserFeedbackResponse(
            id=f.id,
            opportunity_id=f.opportunity_id,
            user_id=f.user_id,
            feedback_type=FeedbackType(f.feedback_type),
            notes=f.notes,
            status=FeedbackStatus(f.status),
            created_at=f.created_at,
        )
        for f in feedbacks
    ]
    return StandardResponse(data=items, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Source Mapping Endpoints
# ------------------------------------------------------------------------------

@router.get("/opportunities/{opportunity_id}/mappings", response_model=StandardResponse[List[SourceMappingResponse]])
async def get_opportunity_mappings(
    opportunity_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[SourceMappingResponse]]:
    """Retrieves all source mapping records connected to this canonical opportunity."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_mappings(session: Session):
        mappings = session.execute(
            select(OpportunitySourceMappingRecord)
            .options(joinedload(OpportunitySourceMappingRecord.source))
            .where(OpportunitySourceMappingRecord.canonical_opportunity_id == opportunity_id)
            .order_by(OpportunitySourceMappingRecord.first_seen_at.asc())
        ).scalars().all()
        return [
            SourceMappingResponse(
                id=m.id,
                canonical_opportunity_id=m.canonical_opportunity_id,
                source_id=m.source_id,
                source_key=m.source.source_key if m.source else "UNKNOWN",
                external_job_id=m.external_job_id,
                original_url=m.original_url,
                first_seen_at=m.first_seen_at,
                last_seen_at=m.last_seen_at,
                mapping_status=m.mapping_status,
                match_tier=MatchTier(m.match_tier),
                match_method=m.match_method,
                match_evidence=m.match_evidence_json or {},
                confidence_score=m.confidence_score,
                merge_decision_id=m.merge_decision_id,
            )
            for m in mappings
        ]

    items = await db.run_sync(_sync_mappings)
    return StandardResponse(data=items, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Deduplication Endpoints
# ------------------------------------------------------------------------------

@router.get("/duplicates", response_model=StandardResponse[List[DuplicateCandidateResponse]])
async def list_duplicate_candidates(
    request: Request,
    status: Optional[str] = Query("PROPOSED", description="PROPOSED, CONFIRMED, REJECTED, UNMERGED, or ALL"),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[DuplicateCandidateResponse]]:
    """Lists duplicate candidate pairs awaiting administrative review."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    filter_status = None if status == "ALL" else status

    def _sync_dups(session: Session):
        return DeduplicationService.get_duplicate_candidates(session, status=filter_status)

    candidates = await db.run_sync(_sync_dups)
    items: List[DuplicateCandidateResponse] = []
    for c in candidates:
        items.append(
            DuplicateCandidateResponse(
                id=c.id,
                primary_opportunity_id=c.primary_opportunity_id,
                primary_title=c.primary_opportunity.title if c.primary_opportunity else "Unknown",
                primary_company=c.primary_opportunity.company_name if c.primary_opportunity else "Unknown",
                primary_location=f"{c.primary_opportunity.city or ''}, {c.primary_opportunity.country or ''}" if c.primary_opportunity else None,
                duplicate_opportunity_id=c.duplicate_opportunity_id,
                duplicate_title=c.duplicate_opportunity.title if c.duplicate_opportunity else "Unknown",
                duplicate_company=c.duplicate_opportunity.company_name if c.duplicate_opportunity else "Unknown",
                duplicate_location=f"{c.duplicate_opportunity.city or ''}, {c.duplicate_opportunity.country or ''}" if c.duplicate_opportunity else None,
                match_tier=MatchTier(c.match_tier),
                match_method=c.match_method,
                confidence_score=c.confidence_score,
                match_evidence=c.match_evidence_json or {},
                status=MergeStatus(c.status),
                created_at=c.created_at,
            )
        )
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.post("/duplicates/detect", response_model=StandardResponse[Dict[str, Any]])
async def run_duplicate_detection(
    request: Request,
    lookback_days: int = Query(60, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Runs automated tiered duplicate detection routine over recent canonical listings."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_detect(session: Session):
        return DeduplicationService.detect_duplicate_candidates(session, lookback_days=lookback_days)

    detected = await db.run_sync(_sync_detect)
    return StandardResponse(
        data={"detected_count": len(detected), "lookback_days": lookback_days},
        meta=make_meta(req_id),
    )


@router.post("/duplicates/merge", response_model=StandardResponse[Dict[str, Any]])
async def merge_duplicate_opportunities(
    payload: MergeActionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Merges duplicate opportunities into a primary canonical opportunity with reversible audit trail."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_merge(session: Session):
        return DeduplicationService.merge_opportunities(
            db=session,
            primary_id=payload.primary_id,
            duplicate_ids=payload.duplicate_ids,
            actor_id=current_user.email,
            actor_type="ADMIN",
            reason=payload.reason,
        )

    try:
        decision = await db.run_sync(_sync_merge)
        return StandardResponse(
            data={
                "decision_id": decision.id,
                "status": decision.status,
                "primary_opportunity_id": decision.canonical_opportunity_id,
                "merged_duplicate_ids": decision.original_opportunity_ids_json,
                "message": "Opportunities successfully merged and duplicates suppressed.",
            },
            meta=make_meta(req_id),
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))


@router.post("/duplicates/{decision_id}/unmerge", response_model=StandardResponse[Dict[str, Any]])
async def unmerge_duplicate_opportunities(
    decision_id: str,
    payload: UnmergeActionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Reverses a prior merge decision, restoring unsuppressed status and original source mappings."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_unmerge(session: Session):
        return DeduplicationService.unmerge_opportunities(
            db=session,
            decision_id=decision_id,
            actor_id=current_user.email,
            reason=payload.reason,
        )

    try:
        decision = await db.run_sync(_sync_unmerge)
        return StandardResponse(
            data={
                "decision_id": decision.id,
                "status": decision.status,
                "unmerged_at": decision.unmerged_at,
                "unmerged_by": decision.unmerged_by,
                "message": "Merge decision successfully reversed and records unmerged.",
            },
            meta=make_meta(req_id),
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))


# ------------------------------------------------------------------------------
# Quality Dashboard Metrics Endpoint
# ------------------------------------------------------------------------------

@router.get("/quality/metrics", response_model=StandardResponse[QualityMetricsResponse])
async def get_quality_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[QualityMetricsResponse]:
    """Retrieves operational data quality and freshness KPIs for the Data Quality Dashboard."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_metrics(session: Session):
        return QualityService.get_quality_metrics(session)

    metrics = await db.run_sync(_sync_metrics)
    return StandardResponse(data=metrics, meta=make_meta(req_id))
