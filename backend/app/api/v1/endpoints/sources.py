"""
RIGHT FIT Core — Job Source Framework & Opportunities Endpoints
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import (
    CanonicalOpportunityRecord,
    JobSourceRecord,
    SourceObservationRecord,
    SourceRunLogRecord,
    User,
)
from app.services.ingestion_service import IngestionService
from app.services.resilience import CircuitOpenException, RateLimitExceededException
from app.services.source_service import SourceService
from contracts.common.envelope import ResponseMeta, StandardResponse
from contracts.sources.schemas import (
    AuthType,
    CanonicalOpportunityResponse,
    CircuitBreakerState,
    EmploymentType,
    IngestionTriggerRequest,
    IngestionTriggerResponse,
    IntegrationMethod,
    NormalizationStatus,
    PolicyStatus,
    RunStatus,
    SourceCreateRequest,
    SourceObservationResponse,
    SourcePolicyUpdateRequest,
    SourceResponse,
    SourceRunLogResponse,
    SourceType,
    SourceUpdateRequest,
    TriggerType,
    WorkplaceType,
)

router = APIRouter(tags=["Job Sources & Opportunities"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id, service="core_career_engine")


def _to_source_response(s: JobSourceRecord) -> SourceResponse:
    return SourceResponse(
        id=s.id,
        source_key=s.source_key,
        display_name=s.display_name,
        source_type=SourceType(s.source_type),
        provider=s.provider,
        base_url=s.base_url,
        integration_method=IntegrationMethod(s.integration_method),
        auth_type=AuthType(s.auth_type),
        credential_reference=s.credential_reference,
        enabled=s.enabled,
        policy_status=PolicyStatus(s.policy_status),
        policy_decision_json=s.policy_decision_json or {},
        rate_limit_per_minute=s.rate_limit_per_minute,
        timeout_seconds=s.timeout_seconds,
        retry_max_attempts=s.retry_max_attempts,
        circuit_breaker_state=CircuitBreakerState(s.circuit_breaker_state),
        consecutive_failures=s.consecutive_failures,
        last_failure_at=s.last_failure_at,
        last_success_at=s.last_success_at,
        cooldown_until=s.cooldown_until,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _to_observation_response(o: SourceObservationRecord) -> SourceObservationResponse:
    return SourceObservationResponse(
        id=o.id,
        source_id=o.source_id,
        external_job_id=o.external_job_id,
        listing_url=o.listing_url,
        observed_at=o.observed_at,
        source_published_at=o.source_published_at,
        source_updated_at=o.source_updated_at,
        payload_hash_sha256=o.payload_hash_sha256,
        normalization_status=NormalizationStatus(o.normalization_status),
        error_message=o.error_message,
        first_seen_at=o.first_seen_at,
        last_seen_at=o.last_seen_at,
    )


def _to_canonical_response(c: CanonicalOpportunityRecord) -> CanonicalOpportunityResponse:
    return CanonicalOpportunityResponse(
        id=c.id,
        source_id=c.source_id,
        external_job_id=c.external_job_id,
        dedup_key_sha256=c.dedup_key_sha256,
        title=c.title,
        company_name=c.company_name,
        description_clean=c.description_clean,
        employment_type=EmploymentType(c.employment_type),
        workplace_type=WorkplaceType(c.workplace_type),
        department=c.department,
        city=c.city,
        state=c.state,
        country=c.country,
        is_remote=c.is_remote,
        min_salary=c.min_salary,
        max_salary=c.max_salary,
        currency=c.currency,
        salary_period=c.salary_period,
        is_salary_estimated=c.is_salary_estimated,
        required_skills=c.required_skills_json or [],
        application_url=c.application_url,
        source_published_at=c.source_published_at,
        first_seen_at=c.first_seen_at,
        last_seen_at=c.last_seen_at,
        is_active=c.is_active,
        verification_status=c.verification_status,
        freshness_state=c.freshness_state,
        is_suppressed=c.is_suppressed,
        provenance=c.provenance_json or {},
    )


def _to_run_log_response(r: SourceRunLogRecord) -> SourceRunLogResponse:
    return SourceRunLogResponse(
        id=r.id,
        source_id=r.source_id,
        trigger_type=TriggerType(r.trigger_type),
        status=RunStatus(r.status),
        records_fetched=r.records_fetched,
        records_normalized=r.records_normalized,
        records_inserted=r.records_inserted,
        records_updated=r.records_updated,
        duplicates_skipped=r.duplicates_skipped,
        error_category=r.error_category,
        safe_error_summary=r.safe_error_summary,
        started_at=r.started_at,
        completed_at=r.completed_at,
        duration_seconds=r.duration_seconds,
    )


# ------------------------------------------------------------------------------
# Source Administration Endpoints
# ------------------------------------------------------------------------------

@router.get("/sources", response_model=StandardResponse[List[SourceResponse]])
async def list_sources(
    request: Request,
    policy_status: Optional[str] = Query(None, description="Filter by policy status (e.g. ACTIVE, DRAFT)"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled state"),
    provider: Optional[str] = Query(None, description="Filter by provider (e.g. greenhouse, ashby)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[SourceResponse]]:
    """Lists registered job sources with filtering and pagination."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    records, total = await SourceService.list_sources(
        db, policy_status=policy_status, enabled=enabled, provider=provider, skip=skip, limit=limit
    )
    items = [_to_source_response(s) for s in records]
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.post("/sources", response_model=StandardResponse[SourceResponse], status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: SourceCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SourceResponse]:
    """Registers a new opportunity data source (default state: DRAFT)."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        source = await SourceService.create_source(db, payload)
        return StandardResponse(data=_to_source_response(source), meta=make_meta(req_id))
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))


@router.get("/sources/{source_id}", response_model=StandardResponse[SourceResponse])
async def get_source(
    source_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SourceResponse]:
    """Retrieves source configuration and operational status by UUID."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    source = await SourceService.get_source_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Source '{source_id}' not found")
    return StandardResponse(data=_to_source_response(source), meta=make_meta(req_id))


@router.patch("/sources/{source_id}", response_model=StandardResponse[SourceResponse])
async def update_source(
    source_id: str,
    payload: SourceUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SourceResponse]:
    """Updates runtime limits, display name, or URL of an existing source."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        updated = await SourceService.update_source(db, source_id, payload)
        return StandardResponse(data=_to_source_response(updated), meta=make_meta(req_id))
    except KeyError as key_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(key_err))
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))


@router.patch("/sources/{source_id}/policy", response_model=StandardResponse[SourceResponse])
async def update_source_policy(
    source_id: str,
    payload: SourcePolicyUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SourceResponse]:
    """Updates governance policy status (DRAFT, PENDING_REVIEW, APPROVED, ACTIVE, PAUSED, BLOCKED, RETIRED)."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        updated = await SourceService.update_policy_status(
            db, source_id=source_id, request=payload, reviewer_email=current_user.email
        )
        return StandardResponse(data=_to_source_response(updated), meta=make_meta(req_id))
    except KeyError as key_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(key_err))


@router.post("/sources/{source_id}/ingest", response_model=StandardResponse[IngestionTriggerResponse])
async def trigger_ingestion(
    source_id: str,
    payload: IngestionTriggerRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[IngestionTriggerResponse]:
    """Triggers an ingestion run for an active source with resilience guardrails."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        result = await IngestionService.run_ingestion(
            db,
            source_id=source_id,
            trigger_type=TriggerType.MANUAL.value,
            max_records=payload.max_records,
            force=payload.force,
        )
        return StandardResponse(data=result, meta=make_meta(req_id))
    except KeyError as key_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(key_err))
    except PermissionError as perm_err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(perm_err))
    except CircuitOpenException as circ_err:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(circ_err))
    except RateLimitExceededException as rate_err:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(rate_err))
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Ingestion failed: {str(exc)}")


@router.get("/sources/{source_id}/runs", response_model=StandardResponse[List[SourceRunLogResponse]])
async def get_source_runs(
    source_id: str,
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[SourceRunLogResponse]]:
    """Retrieves execution metrics and logs for a source."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    runs = await SourceService.get_source_run_logs(db, source_id, limit=limit)
    items = [_to_run_log_response(r) for r in runs]
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.get("/sources/{source_id}/observations", response_model=StandardResponse[List[SourceObservationResponse]])
async def get_source_observations(
    source_id: str,
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[SourceObservationResponse]]:
    """Retrieves raw observation payloads and provenance for a source."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    observations = await SourceService.get_source_observations(db, source_id, limit=limit)
    items = [_to_observation_response(o) for o in observations]
    return StandardResponse(data=items, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Canonical Opportunity Query Endpoints
# ------------------------------------------------------------------------------

@router.get("/opportunities", response_model=StandardResponse[List[CanonicalOpportunityResponse]])
async def search_opportunities(
    request: Request,
    search: Optional[str] = Query(None, description="Keyword search in title, company, description"),
    remote_only: Optional[bool] = Query(None, description="Filter for remote jobs"),
    employment_type: Optional[str] = Query(None, description="FULL_TIME, CONTRACT, INTERNSHIP"),
    department: Optional[str] = Query(None, description="Department name"),
    include_suppressed: bool = Query(False, description="Whether to include closed/merged suppressed listings"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[CanonicalOpportunityResponse]]:
    """Searches canonical career opportunities ingested from all active sources."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    query = select(CanonicalOpportunityRecord).where(CanonicalOpportunityRecord.is_active == True)
    if not include_suppressed:
        query = query.where(CanonicalOpportunityRecord.is_suppressed == False)

    if search:
        kw = f"%{search.strip()}%"
        query = query.where(
            or_(
                CanonicalOpportunityRecord.title.ilike(kw),
                CanonicalOpportunityRecord.company_name.ilike(kw),
                CanonicalOpportunityRecord.description_clean.ilike(kw),
            )
        )
    if remote_only is not None:
        query = query.where(CanonicalOpportunityRecord.is_remote == remote_only)
    if employment_type:
        query = query.where(CanonicalOpportunityRecord.employment_type == employment_type.upper())
    if department:
        query = query.where(CanonicalOpportunityRecord.department.ilike(f"%{department.strip()}%"))

    query = query.order_by(desc(CanonicalOpportunityRecord.last_seen_at)).offset(skip).limit(limit)
    res = await db.execute(query)
    records = list(res.scalars().all())

    items = [_to_canonical_response(c) for c in records]
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.get("/opportunities/{opportunity_id}", response_model=StandardResponse[CanonicalOpportunityResponse])
async def get_opportunity(
    opportunity_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[CanonicalOpportunityResponse]:
    """Retrieves a single canonical opportunity by UUID."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    res = await db.execute(
        select(CanonicalOpportunityRecord).where(CanonicalOpportunityRecord.id == opportunity_id)
    )
    opp = res.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Opportunity '{opportunity_id}' not found")
    return StandardResponse(data=_to_canonical_response(opp), meta=make_meta(req_id))
