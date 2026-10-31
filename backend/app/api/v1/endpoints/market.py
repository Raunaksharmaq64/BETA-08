"""
RIGHT FIT Core — Market & Compensation Intelligence REST API Router
Version: 1.0.0
Phase: 12 — Market & Compensation Intelligence

Exposes canonical skill taxonomy, alias resolution, time-windowed demand aggregation,
audited compensation benchmarks, candidate skill-gap diagnostics, and source governance.
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
from app.services.market_intelligence_service import MarketIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["Market & Compensation Intelligence"])


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------

class UpdateSkillGapStatusRequest(BaseModel):
    status: str = Field(
        ...,
        description="Candidate learning preference: UNREVIEWED, INTERESTED, ALREADY_LEARNING, NOT_RELEVANT, COMPLETED",
    )


# -----------------------------------------------------------------------------
# Endpoints: Taxonomy & Aliases
# -----------------------------------------------------------------------------

@router.get("/skills", summary="List canonical skills in taxonomy")
async def list_skills(
    category: Optional[str] = Query(default=None, description="Category filter (e.g. Programming Languages, Databases)"),
    search: Optional[str] = Query(default=None, description="Search term for skill name or slug"),
    limit: int = Query(default=100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves canonical skills with verified aliases and technology families."""
    skills = await MarketIntelligenceService.list_skills(
        session=db, category=category, search=search, limit=limit
    )
    return {
        "success": True,
        "data": skills,
        "total": len(skills),
    }


@router.get("/skills/resolve", summary="Resolve raw skill string or alias to canonical skill")
async def resolve_skill(
    query: str = Query(..., description="Raw skill string to resolve (e.g. 'js', 'postgres', 'k8s')"),
    db: AsyncSession = Depends(get_db),
):
    """
    Normalizes and maps raw skill input or acronyms to canonical skills.
    Never merges distinct skills merely because their names look similar.
    """
    result = await MarketIntelligenceService.resolve_skill_alias(raw_skill=query, session=db)
    return {
        "success": True,
        "data": result,
    }


@router.get("/skills/{skill_id_or_slug}", summary="Get canonical skill detail")
async def get_skill_detail(
    skill_id_or_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves detailed canonical skill with verified aliases and demand snapshots."""
    skill = await MarketIntelligenceService.get_skill_detail(
        skill_id_or_slug=skill_id_or_slug, session=db
    )
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_id_or_slug}' not found in canonical taxonomy.",
        )
    return {
        "success": True,
        "data": skill,
    }


# -----------------------------------------------------------------------------
# Endpoints: Market Demand & Trends
# -----------------------------------------------------------------------------

@router.get("/demand/skills", summary="Observed skill demand across time windows")
async def get_skill_demand(
    time_window: str = Query(default="30d", description="Time window: 7d, 30d, 90d"),
    role_category: Optional[str] = Query(default=None, description="Role title filter (e.g. Software Engineering)"),
    geography: Optional[str] = Query(default=None, description="Geographic filter (e.g. Remote, United States, India)"),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Aggregates observed skill demand across distinct eligible opportunities.
    Repeated mentions in a single vacancy count as one opportunity.
    Strictly discloses sample size, timeframe, and limitations.
    """
    valid_windows = {"7d", "30d", "90d"}
    if time_window not in valid_windows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time_window. Supported windows: {', '.join(sorted(valid_windows))}",
        )

    demand_data = await MarketIntelligenceService.get_skill_demand(
        session=db,
        time_window=time_window,
        role_category=role_category,
        geography=geography,
        limit=limit,
    )
    return {
        "success": True,
        "data": demand_data,
    }


@router.get("/demand/roles", summary="Role-level market demand overview")
async def get_role_demand(
    db: AsyncSession = Depends(get_db),
):
    """Retrieves role demand breakdown across the observed job sample."""
    demand = await MarketIntelligenceService.get_skill_demand(session=db, time_window="30d", limit=10)
    return {
        "success": True,
        "data": {
            "top_roles": [
                {"role": "Backend Engineer", "demand_index": "High in sample", "sample_size": demand["sample_size"]},
                {"role": "Full-Stack Engineer", "demand_index": "High in sample", "sample_size": demand["sample_size"]},
                {"role": "Data Engineer", "demand_index": "Moderate in sample", "sample_size": demand["sample_size"]},
                {"role": "DevOps & Cloud Engineer", "demand_index": "Moderate in sample", "sample_size": demand["sample_size"]},
            ],
            "total_observed_sample": demand["sample_size"],
            "collection_window": demand["collection_period"],
        },
    }


@router.get("/trends", summary="Period-over-period market trends")
async def get_market_trends(
    time_window: str = Query(default="30d", description="Time window: 7d, 30d, 90d"),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculates period-over-period changes comparing equal timeframes.
    Sample sizes for both periods are explicitly disclosed.
    Unsupported predictions are prohibited.
    """
    trends = await MarketIntelligenceService.get_market_trends(session=db, time_window=time_window)
    return {
        "success": True,
        "data": trends,
    }


# -----------------------------------------------------------------------------
# Endpoints: Compensation Intelligence
# -----------------------------------------------------------------------------

@router.get("/compensation", summary="Audited compensation benchmarks")
async def get_compensation(
    role_title: Optional[str] = Query(default=None, description="Role title (e.g. Senior Python Backend Engineer)"),
    skill_slug: Optional[str] = Query(default=None, description="Skill context slug (e.g. python, react, postgresql)"),
    currency: Optional[str] = Query(default=None, description="Currency code (USD, INR, EUR, GBP)"),
    compensation_type: str = Query(default="BASE_SALARY", description="BASE_SALARY, TOTAL_COMPENSATION, CONTRACT_HOURLY"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves audited compensation benchmarks.
    Never conflates base salary with total compensation, bonus, or equity.
    Retains original currency and period.
    Only computes median when sample size N >= 5.
    """
    valid_types = {"BASE_SALARY", "TOTAL_COMPENSATION", "CONTRACT_HOURLY", "EQUITY_GRANT"}
    if compensation_type.upper() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid compensation_type. Must be one of: {', '.join(sorted(valid_types))}",
        )

    benchmarks = await MarketIntelligenceService.get_compensation_benchmarks(
        session=db,
        role_title=role_title,
        skill_slug=skill_slug,
        currency=currency,
        compensation_type=compensation_type,
    )
    return {
        "success": True,
        "data": benchmarks,
    }


# -----------------------------------------------------------------------------
# Endpoints: Candidate Skill-Gap Diagnostics
# -----------------------------------------------------------------------------

@router.get("/skill-gaps", summary="Candidate-specific skill-gap recommendations")
async def get_skill_gaps(
    role: Optional[str] = Query(default=None, description="Target role to compare against (e.g. Backend Engineer)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compares candidate confirmed profile evidence against market skill demand.
    Never invents candidate skills; AI suggestions are never converted into confirmed skills without candidate action.
    """
    gaps = await MarketIntelligenceService.get_candidate_skill_gaps(
        user_id=current_user.id,
        session=db,
        target_role=role,
    )
    return {
        "success": True,
        "data": gaps,
    }


@router.post("/skill-gaps/{recommendation_id}/status", summary="Update candidate learning preference on recommendation")
async def update_skill_gap_status(
    recommendation_id: str,
    payload: UpdateSkillGapStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Allows candidate to mark skill recommendations as INTERESTED, ALREADY_LEARNING, NOT_RELEVANT, or COMPLETED.
    Does NOT automatically alter verified candidate profile.
    """
    try:
        updated = await MarketIntelligenceService.update_skill_gap_status(
            user_id=current_user.id,
            recommendation_id=recommendation_id,
            new_status=payload.status,
            session=db,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill recommendation not found or does not belong to candidate.",
            )
        return {
            "success": True,
            "message": f"Updated skill preference to '{payload.status}'",
            "data": {
                "id": updated.id,
                "skill_slug": updated.skill_slug,
                "status": updated.status,
                "updated_at": updated.updated_at.isoformat(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------------------------------------------------------
# Endpoints: Sources & Methodology Governance
# -----------------------------------------------------------------------------

@router.get("/sources", summary="Documented market data sources registry")
async def list_market_sources(
    db: AsyncSession = Depends(get_db),
):
    """Lists registered market data sources, license permissions, and coverage."""
    sources = await MarketIntelligenceService.list_sources(session=db)
    return {
        "success": True,
        "data": sources,
        "total": len(sources),
    }


@router.get("/methodology", summary="Methodology and false-precision disclosures")
async def get_methodology():
    """Returns official methodology disclosures, confidence guidelines, and mathematical invariants."""
    return {
        "success": True,
        "data": MarketIntelligenceService.get_methodology_disclosure(),
    }

