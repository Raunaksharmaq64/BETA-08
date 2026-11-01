"""
RIGHT FIT Core — Job Search, Candidate Matching & Personalized Discovery Endpoints
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_current_user
from app.db.models import (
    CandidateProfile,
    CanonicalOpportunityRecord,
    SavedJobRecord,
    SavedSearchRecord,
    User,
)
from app.services.matching_service import MatchingService
from app.services.saved_search_service import SavedSearchService
from app.services.search_service import SearchService
from contracts.common.envelope import ResponseMeta, StandardResponse
from contracts.matching.schemas import (
    AlertDeliveryLogResponse,
    JobDetailResponse,
    JobSearchFilters,
    JobSearchResponse,
    MatchExplanationResponse,
    SavedJobCreateRequest,
    SavedJobResponse,
    SavedJobUpdateRequest,
    SavedSearchCreateRequest,
    SavedSearchResponse,
    SavedSearchUpdateRequest,
    SearchSortOption,
)

router = APIRouter(tags=["Job Search & Candidate Matching"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id)


# ------------------------------------------------------------------------------
# Job Search & Discovery
# ------------------------------------------------------------------------------

@router.get("/search/jobs", response_model=StandardResponse[JobSearchResponse])
async def search_jobs(
    request: Request,
    q: Optional[str] = Query(None, description="Free text keyword search"),
    role: Optional[str] = Query(None, description="Role title filter"),
    company: Optional[str] = Query(None, description="Company name filter"),
    city: Optional[str] = Query(None, description="City location filter"),
    state: Optional[str] = Query(None, description="State/Province filter"),
    country: Optional[str] = Query(None, description="Country filter"),
    is_remote: Optional[bool] = Query(None, description="Remote work arrangement flag"),
    is_internship: Optional[bool] = Query(None, description="Internship flag"),
    is_fresher_friendly: Optional[bool] = Query(None, description="Fresher/Entry-level flag"),
    workplace_types: Optional[List[str]] = Query(None, description="Workplace modes (REMOTE, HYBRID, ON_SITE)"),
    employment_types: Optional[List[str]] = Query(None, description="Employment types (FULL_TIME, CONTRACT, etc.)"),
    skills: Optional[List[str]] = Query(None, description="Specific skills filter"),
    min_salary: Optional[float] = Query(None, description="Minimum compensation threshold"),
    max_salary: Optional[float] = Query(None, description="Maximum compensation filter"),
    currency: Optional[str] = Query(None, description="Salary ISO currency code"),
    sources: Optional[List[str]] = Query(None, description="Specific source keys"),
    verification_statuses: Optional[List[str]] = Query(None, description="Verification status filters"),
    freshness_states: Optional[List[str]] = Query(None, description="Freshness state filters"),
    sort_by: SearchSortOption = Query(SearchSortOption.BEST_FIT, description="Ranking sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[JobSearchResponse]:
    """
    Candidate search query across canonical career opportunities.
    Returns multi-attribute filtered listings, personalized match scores (if authenticated),
    and upstream source coverage health metadata.
    """
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    filters = JobSearchFilters(
        query=q,
        role=role,
        company=company,
        city=city,
        state=state,
        country=country,
        is_remote=is_remote,
        is_internship=is_internship,
        is_fresher_friendly=is_fresher_friendly,
        workplace_types=workplace_types,
        employment_types=employment_types,
        skills=skills,
        min_salary=min_salary,
        max_salary=max_salary,
        currency=currency,
        sources=sources,
        verification_statuses=verification_statuses,
        freshness_states=freshness_states,
        sort_by=sort_by,
    )

    user_id = current_user.id if current_user else None

    def _sync_search(session: Session) -> JobSearchResponse:
        return SearchService.search_jobs(
            session=session,
            filters=filters,
            page=page,
            page_size=page_size,
            current_user_id=user_id,
        )

    response_data = await db.run_sync(_sync_search)
    return StandardResponse(data=response_data, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Job Posting Details & Match Explanation
# ------------------------------------------------------------------------------

@router.get("/jobs/{job_id}", response_model=StandardResponse[JobDetailResponse])
async def get_job_detail(
    job_id: str,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[JobDetailResponse]:
    """Retrieves full job posting details with provenance, timestamps, and match breakdown."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    user_id = current_user.id if current_user else None

    def _sync_fetch(session: Session) -> Optional[JobDetailResponse]:
        opp = session.execute(
            select(CanonicalOpportunityRecord)
            .options(joinedload(CanonicalOpportunityRecord.source))
            .where(
                CanonicalOpportunityRecord.id == job_id,
                CanonicalOpportunityRecord.is_suppressed.is_(False),
            )
        ).scalars().first()

        if not opp:
            return None

        # Check saved status
        is_saved = False
        saved_job_id = None
        match_breakdown = None

        if user_id:
            saved_rec = session.execute(
                select(SavedJobRecord).where(
                    SavedJobRecord.user_id == user_id,
                    SavedJobRecord.opportunity_id == job_id,
                )
            ).scalars().first()
            if saved_rec:
                is_saved = True
                saved_job_id = saved_rec.id

            # Compute match breakdown
            prof = session.execute(
                select(CandidateProfile).where(CandidateProfile.user_id == user_id)
            ).scalars().first()
            if prof:
                profile_dict = {
                    "city": prof.city,
                    "state": prof.state,
                    "country": prof.country,
                    "experience": [
                        {"company": exp.company, "role": exp.role, "years_experience": 2.0}
                        for exp in prof.experience
                    ],
                    "education": [
                        {"institution": edu.institution, "degree": edu.degree, "field_of_study": edu.field_of_study}
                        for edu in prof.education
                    ],
                }
                cand_skills = [
                    {
                        "skill_name": sk.skill_name,
                        "proficiency": sk.proficiency,
                        "years_experience": sk.years_experience,
                        "provenance": sk.provenance,
                        "is_confirmed": True,
                    }
                    for sk in prof.skills
                ]
                cand_prefs = None
                if prof.preferences:
                    cand_prefs = {
                        "remote_preference": prof.preferences.remote_preference,
                        "min_salary": prof.preferences.min_salary,
                        "max_salary": prof.preferences.max_salary,
                    }

                opp_dict = {
                    "workplace_type": opp.workplace_type,
                    "is_remote": opp.is_remote,
                    "city": opp.city,
                    "country": opp.country,
                    "title": opp.title,
                    "description_clean": opp.description_clean,
                    "required_skills_json": opp.required_skills_json or [],
                    "verification_status": opp.verification_status,
                    "freshness_state": opp.freshness_state,
                    "max_salary": opp.max_salary,
                }

                match_breakdown = MatchingService.build_match_explanation(
                    opportunity_id=opp.id,
                    candidate_id=user_id,
                    opportunity=opp_dict,
                    candidate_profile=profile_dict,
                    candidate_skills=cand_skills,
                    candidate_preferences=cand_prefs,
                )

        return JobDetailResponse(
            id=opp.id,
            external_job_id=opp.external_job_id,
            title=opp.title,
            company_name=opp.company_name,
            department=opp.department,
            description_clean=opp.description_clean,
            city=opp.city,
            state=opp.state,
            country=opp.country,
            workplace_type=opp.workplace_type,
            is_remote=opp.is_remote,
            employment_type=opp.employment_type,
            min_salary=opp.min_salary,
            max_salary=opp.max_salary,
            currency=opp.currency,
            salary_period=opp.salary_period,
            is_salary_estimated=opp.is_salary_estimated,
            required_skills=opp.required_skills_json or [],
            application_url=opp.application_url,
            source_name=opp.source.display_name if opp.source else "Core Feed",
            source_key=opp.source.source_key if opp.source else "core",
            source_published_at=opp.source_published_at,
            source_updated_at=opp.source_updated_at,
            first_seen_at=opp.first_seen_at,
            last_seen_at=opp.last_seen_at,
            last_verified_at=opp.last_verified_at,
            verification_status=opp.verification_status,
            freshness_state=opp.freshness_state,
            is_saved=is_saved,
            saved_job_id=saved_job_id,
            match_breakdown=match_breakdown,
            provenance_metadata=opp.provenance_json or {},
        )

    detail = await db.run_sync(_sync_fetch)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job posting '{job_id}' not found.")

    return StandardResponse(data=detail, meta=make_meta(req_id))


@router.get("/jobs/{job_id}/match", response_model=StandardResponse[MatchExplanationResponse])
async def get_job_match_explanation(
    job_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[MatchExplanationResponse]:
    """Retrieves evidence-based skill fit and mandatory eligibility breakdown for candidate."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_match(session: Session) -> MatchExplanationResponse:
        opp = session.get(CanonicalOpportunityRecord, job_id)
        if not opp or opp.is_suppressed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job posting '{job_id}' not found.")

        prof = session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
        ).scalars().first()

        profile_dict = None
        cand_skills = []
        cand_prefs = None

        if prof:
            profile_dict = {
                "city": prof.city,
                "state": prof.state,
                "country": prof.country,
                "experience": [
                    {"company": exp.company, "role": exp.role, "years_experience": 2.0}
                    for exp in prof.experience
                ],
                "education": [
                    {"institution": edu.institution, "degree": edu.degree, "field_of_study": edu.field_of_study}
                    for edu in prof.education
                ],
            }
            cand_skills = [
                {
                    "skill_name": sk.skill_name,
                    "proficiency": sk.proficiency,
                    "years_experience": sk.years_experience,
                    "provenance": sk.provenance,
                    "is_confirmed": True,
                }
                for sk in prof.skills
            ]
            if prof.preferences:
                cand_prefs = {
                    "remote_preference": prof.preferences.remote_preference,
                    "min_salary": prof.preferences.min_salary,
                    "max_salary": prof.preferences.max_salary,
                }

        opp_dict = {
            "workplace_type": opp.workplace_type,
            "is_remote": opp.is_remote,
            "city": opp.city,
            "country": opp.country,
            "title": opp.title,
            "description_clean": opp.description_clean,
            "required_skills_json": opp.required_skills_json or [],
            "verification_status": opp.verification_status,
            "freshness_state": opp.freshness_state,
            "max_salary": opp.max_salary,
        }

        return MatchingService.build_match_explanation(
            opportunity_id=opp.id,
            candidate_id=current_user.id,
            opportunity=opp_dict,
            candidate_profile=profile_dict,
            candidate_skills=cand_skills,
            candidate_preferences=cand_prefs,
        )

    match_expl = await db.run_sync(_sync_match)
    return StandardResponse(data=match_expl, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Candidate Saved Jobs
# ------------------------------------------------------------------------------

@router.post("/saved-jobs", response_model=StandardResponse[SavedJobResponse], status_code=status.HTTP_201_CREATED)
async def save_job(
    req: SavedJobCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SavedJobResponse]:
    """Bookmarks a job for candidate with optional private notes."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_save(session: Session) -> SavedJobResponse:
        try:
            return SavedSearchService.save_job(
                session=session,
                user_id=current_user.id,
                opportunity_id=req.opportunity_id,
                notes=req.notes,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    saved = await db.run_sync(_sync_save)
    return StandardResponse(data=saved, meta=make_meta(req_id))


@router.get("/saved-jobs", response_model=StandardResponse[List[SavedJobResponse]])
async def list_saved_jobs(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[SavedJobResponse]]:
    """Lists all saved jobs for current candidate."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[SavedJobResponse]:
        return SavedSearchService.list_saved_jobs(session=session, user_id=current_user.id)

    items = await db.run_sync(_sync_list)
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.delete("/saved-jobs/{identifier}", response_model=StandardResponse[Dict[str, Any]])
async def unsave_job(
    identifier: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Removes a saved job by either saved_job_id or opportunity_id."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_unsave(session: Session) -> bool:
        return SavedSearchService.unsave_job(session=session, user_id=current_user.id, identifier=identifier)

    deleted = await db.run_sync(_sync_unsave)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found.")

    return StandardResponse(data={"success": True, "message": "Job unsaved successfully."}, meta=make_meta(req_id))


@router.patch("/saved-jobs/{saved_job_id}", response_model=StandardResponse[SavedJobResponse])
async def update_saved_job_notes(
    saved_job_id: str,
    req: SavedJobUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SavedJobResponse]:
    """Updates candidate notes on a saved job."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_update(session: Session) -> Optional[SavedJobResponse]:
        return SavedSearchService.update_saved_job_notes(
            session=session,
            user_id=current_user.id,
            saved_job_id=saved_job_id,
            notes=req.notes,
        )

    updated = await db.run_sync(_sync_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found.")

    return StandardResponse(data=updated, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Candidate Saved Searches & Alert Subscriptions
# ------------------------------------------------------------------------------

@router.post("/saved-searches", response_model=StandardResponse[SavedSearchResponse], status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    req: SavedSearchCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SavedSearchResponse]:
    """Saves search filters and configures candidate job alert subscriptions."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_create(session: Session) -> SavedSearchResponse:
        return SavedSearchService.create_saved_search(session=session, user_id=current_user.id, req=req)

    saved = await db.run_sync(_sync_create)
    return StandardResponse(data=saved, meta=make_meta(req_id))


@router.get("/saved-searches", response_model=StandardResponse[List[SavedSearchResponse]])
async def list_saved_searches(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[SavedSearchResponse]]:
    """Lists all saved searches and alert cadences for current candidate."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[SavedSearchResponse]:
        return SavedSearchService.list_saved_searches(session=session, user_id=current_user.id)

    items = await db.run_sync(_sync_list)
    return StandardResponse(data=items, meta=make_meta(req_id))


@router.patch("/saved-searches/{search_id}", response_model=StandardResponse[SavedSearchResponse])
async def update_saved_search(
    search_id: str,
    req: SavedSearchUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SavedSearchResponse]:
    """Updates saved search filters, enabled status, or alert notification frequency."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_update(session: Session) -> Optional[SavedSearchResponse]:
        return SavedSearchService.update_saved_search(
            session=session,
            user_id=current_user.id,
            search_id=search_id,
            req=req,
        )

    updated = await db.run_sync(_sync_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found.")

    return StandardResponse(data=updated, meta=make_meta(req_id))


@router.delete("/saved-searches/{search_id}", response_model=StandardResponse[Dict[str, Any]])
async def delete_saved_search(
    search_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Deletes a saved search subscription."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_delete(session: Session) -> bool:
        return SavedSearchService.delete_saved_search(session=session, user_id=current_user.id, search_id=search_id)

    deleted = await db.run_sync(_sync_delete)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found.")

    return StandardResponse(data={"success": True, "message": "Saved search deleted successfully."}, meta=make_meta(req_id))


@router.post("/saved-searches/run-alerts", response_model=StandardResponse[List[AlertDeliveryLogResponse]])
async def run_alerts_worker(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[AlertDeliveryLogResponse]]:
    """Triggers idempotent alert evaluation for saved searches."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_run(session: Session) -> List[AlertDeliveryLogResponse]:
        return SavedSearchService.process_alerts(session=session)

    logs = await db.run_sync(_sync_run)
    return StandardResponse(data=logs, meta=make_meta(req_id))

