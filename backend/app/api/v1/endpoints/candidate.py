"""
RIGHT FIT Core — Candidate Profile & Preferences API Endpoints
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import User
from app.services.preferences_service import PreferencesService
from app.services.profile_service import ProfileService
from contracts.common.envelope import ResponseMeta, StandardResponse
from contracts.profile.schemas import (
    CandidatePreferencesResponse,
    CandidatePreferencesUpdate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    EducationCreate,
    EducationResponse,
    ExperienceCreate,
    ExperienceResponse,
    ProfileCompletenessResponse,
    SkillCreate,
    SkillResponse,
)

router = APIRouter(prefix="/candidate", tags=["Candidate Profile & Preferences"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id, service="core_career_engine")


@router.get("/profile", response_model=StandardResponse[CandidateProfileResponse])
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[CandidateProfileResponse]:
    """Retrieves authenticated candidate profile including education, experience, and skills."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    profile = await ProfileService.get_profile_response(db, current_user.id)
    return StandardResponse(data=profile, meta=make_meta(req_id))


@router.put("/profile", response_model=StandardResponse[CandidateProfileResponse])
async def update_profile(
    payload: CandidateProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[CandidateProfileResponse]:
    """Updates candidate headline, summary, and location."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    updated = await ProfileService.update_profile(db, current_user.id, payload)
    return StandardResponse(data=updated, meta=make_meta(req_id))


@router.get("/profile/completeness", response_model=StandardResponse[ProfileCompletenessResponse])
async def get_profile_completeness(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ProfileCompletenessResponse]:
    """Calculates profile completeness score and lists missing sections."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    score = await ProfileService.calculate_completeness(db, current_user.id)
    return StandardResponse(data=score, meta=make_meta(req_id))


@router.post("/education", response_model=StandardResponse[EducationResponse], status_code=status.HTTP_201_CREATED)
async def add_education(
    payload: EducationCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[EducationResponse]:
    """Adds an education credential with provenance."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    edu = await ProfileService.add_education(db, current_user.id, payload)
    return StandardResponse(data=edu, meta=make_meta(req_id))


@router.delete("/education/{edu_id}", response_model=StandardResponse[dict])
async def delete_education(
    edu_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Deletes an education entry with strict ownership check."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    await ProfileService.delete_education(db, current_user.id, edu_id)
    return StandardResponse(data={"message": "Education entry deleted."}, meta=make_meta(req_id))


@router.post("/experience", response_model=StandardResponse[ExperienceResponse], status_code=status.HTTP_201_CREATED)
async def add_experience(
    payload: ExperienceCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ExperienceResponse]:
    """Adds a professional experience record."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    exp = await ProfileService.add_experience(db, current_user.id, payload)
    return StandardResponse(data=exp, meta=make_meta(req_id))


@router.delete("/experience/{exp_id}", response_model=StandardResponse[dict])
async def delete_experience(
    exp_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Deletes an experience entry with strict ownership check."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    await ProfileService.delete_experience(db, current_user.id, exp_id)
    return StandardResponse(data={"message": "Experience entry deleted."}, meta=make_meta(req_id))


@router.post("/skills", response_model=StandardResponse[SkillResponse], status_code=status.HTTP_201_CREATED)
async def add_skill(
    payload: SkillCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[SkillResponse]:
    """Appends a skill to candidate profile."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    skill = await ProfileService.add_skill(db, current_user.id, payload)
    return StandardResponse(data=skill, meta=make_meta(req_id))


@router.delete("/skills/{skill_id}", response_model=StandardResponse[dict])
async def delete_skill(
    skill_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Deletes a skill entry with strict ownership check."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    await ProfileService.delete_skill(db, current_user.id, skill_id)
    return StandardResponse(data={"message": "Skill entry deleted."}, meta=make_meta(req_id))


@router.get("/preferences", response_model=StandardResponse[CandidatePreferencesResponse])
async def get_preferences(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[CandidatePreferencesResponse]:
    """Retrieves candidate employment and role preferences."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    prefs = await PreferencesService.get_preferences(db, current_user.id)
    return StandardResponse(data=prefs, meta=make_meta(req_id))


@router.put("/preferences", response_model=StandardResponse[CandidatePreferencesResponse])
async def update_preferences(
    payload: CandidatePreferencesUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[CandidatePreferencesResponse]:
    """Updates candidate employment and role preferences."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    prefs = await PreferencesService.update_preferences(db, current_user.id, payload)
    return StandardResponse(data=prefs, meta=make_meta(req_id))
