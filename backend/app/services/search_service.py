"""
RIGHT FIT — Multi-Dimensional Job Search & Coverage Service
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery

Implements:
1. Multi-attribute filtered search with cursor/offset pagination
2. Non-suppression filtering (is_suppressed=False)
3. Source coverage & partial results transparency metadata
4. Candidate-personalized ranking and saved status enrichment
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    CanonicalOpportunityRecord,
    CandidateProfile,
    CandidateSkillRecord,
    CandidatePreferenceRecord,
    JobSourceRecord,
    SavedJobRecord,
)
from contracts.matching.schemas import (
    EligibilityStatus,
    JobSearchFilters,
    JobSearchResponse,
    JobSearchResultItem,
    SearchSortOption,
    SourceCoverageItem,
    SourceCoverageMetadata,
)
from app.services.matching_service import MatchingService


class SearchService:
    """Orchestrates candidate search queries, source coverage health, and personalized ranking."""

    @classmethod
    def get_source_coverage_metadata(cls, session: Session) -> SourceCoverageMetadata:
        """Inspects all configured sources to report platform coverage and partial result status."""
        sources = session.execute(select(JobSourceRecord)).scalars().all()
        total_sources = len(sources)
        healthy_count = 0
        degraded_count = 0
        coverage_items: List[SourceCoverageItem] = []

        for src in sources:
            is_circuit_open = (src.circuit_breaker_state or "").upper() == "OPEN"
            has_failures = (src.consecutive_failures or 0) > 0
            is_disabled = not src.enabled

            if is_disabled:
                status = "DISABLED"
            elif is_circuit_open:
                status = "OUTAGE"
                degraded_count += 1
            elif has_failures:
                status = "DEGRADED"
                degraded_count += 1
            else:
                status = "ACTIVE"
                healthy_count += 1

            # Count records
            opp_count = session.execute(
                select(func.count(CanonicalOpportunityRecord.id)).where(
                    CanonicalOpportunityRecord.source_id == src.id,
                    CanonicalOpportunityRecord.is_suppressed.is_(False),
                )
            ).scalar() or 0

            outage_reason = None
            if is_circuit_open:
                outage_reason = f"Upstream connector circuit breaker tripped after {src.consecutive_failures} failures."
            elif has_failures:
                outage_reason = f"Upstream connector experiencing intermittent connectivity ({src.consecutive_failures} consecutive errors)."

            coverage_items.append(
                SourceCoverageItem(
                    source_key=src.source_key,
                    display_name=src.display_name,
                    status=status,
                    last_run_status="OK" if status == "ACTIVE" else "ERROR",
                    records_count=opp_count,
                    outage_reason=outage_reason,
                )
            )

        is_partial = degraded_count > 0

        return SourceCoverageMetadata(
            total_configured_sources=total_sources,
            healthy_sources_count=healthy_count,
            degraded_sources_count=degraded_count,
            is_partial_results=is_partial,
            coverage_details=coverage_items,
        )

    @classmethod
    def search_jobs(
        cls,
        session: Session,
        filters: JobSearchFilters,
        page: int = 1,
        page_size: int = 20,
        current_user_id: Optional[str] = None,
    ) -> JobSearchResponse:
        """
        Executes multi-filter search against canonical opportunities,
        enriching results with coverage metadata and candidate matching.
        """
        page = max(1, page)
        page_size = min(100, max(1, page_size))

        # Base query: non-suppressed active opportunities
        query = select(CanonicalOpportunityRecord).options(
            joinedload(CanonicalOpportunityRecord.source)
        ).where(
            CanonicalOpportunityRecord.is_suppressed.is_(False),
            CanonicalOpportunityRecord.is_active.is_(True),
        )

        # 1. Fulltext / keyword query
        if filters.query:
            term = f"%{filters.query.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(CanonicalOpportunityRecord.title).ilike(term),
                    func.lower(CanonicalOpportunityRecord.company_name).ilike(term),
                    func.lower(CanonicalOpportunityRecord.description_clean).ilike(term),
                    func.lower(CanonicalOpportunityRecord.city).ilike(term),
                )
            )

        # 2. Role / Title
        if filters.role:
            query = query.where(func.lower(CanonicalOpportunityRecord.title).ilike(f"%{filters.role.strip().lower()}%"))

        # 3. Company
        if filters.company:
            query = query.where(func.lower(CanonicalOpportunityRecord.company_name).ilike(f"%{filters.company.strip().lower()}%"))

        # 4. Location
        if filters.city:
            query = query.where(func.lower(CanonicalOpportunityRecord.city).ilike(f"%{filters.city.strip().lower()}%"))
        if filters.state:
            query = query.where(func.lower(CanonicalOpportunityRecord.state).ilike(f"%{filters.state.strip().lower()}%"))
        if filters.country:
            query = query.where(func.lower(CanonicalOpportunityRecord.country).ilike(f"%{filters.country.strip().lower()}%"))

        # 5. Remote / Workplace
        if filters.is_remote is not None:
            query = query.where(CanonicalOpportunityRecord.is_remote == filters.is_remote)
        if filters.workplace_types:
            norm_types = [t.upper() for t in filters.workplace_types]
            query = query.where(CanonicalOpportunityRecord.workplace_type.in_(norm_types))

        # 6. Employment Types
        if filters.employment_types:
            norm_emp = [e.upper() for e in filters.employment_types]
            query = query.where(CanonicalOpportunityRecord.employment_type.in_(norm_emp))

        # 7. Salary
        if filters.min_salary is not None:
            query = query.where(
                or_(
                    CanonicalOpportunityRecord.min_salary >= filters.min_salary,
                    CanonicalOpportunityRecord.max_salary >= filters.min_salary,
                )
            )
        if filters.max_salary is not None:
            query = query.where(
                or_(
                    CanonicalOpportunityRecord.max_salary <= filters.max_salary,
                    CanonicalOpportunityRecord.min_salary <= filters.max_salary,
                )
            )
        if filters.currency:
            query = query.where(func.upper(CanonicalOpportunityRecord.currency) == filters.currency.upper())

        # 8. Sources
        if filters.sources:
            src_subq = select(JobSourceRecord.id).where(JobSourceRecord.source_key.in_(filters.sources))
            query = query.where(CanonicalOpportunityRecord.source_id.in_(src_subq))

        # 9. Verification & Freshness
        if filters.verification_statuses:
            norm_v = [v.upper() for v in filters.verification_statuses]
            query = query.where(CanonicalOpportunityRecord.verification_status.in_(norm_v))
        if filters.freshness_states:
            norm_f = [f.upper() for f in filters.freshness_states]
            query = query.where(CanonicalOpportunityRecord.freshness_state.in_(norm_f))

        # Count total matches
        count_query = select(func.count()).select_from(query.subquery())
        total_count = session.execute(count_query).scalar() or 0

        # Load candidate profile & saved jobs if user logged in
        candidate_profile_dict: Optional[Dict[str, Any]] = None
        candidate_skills: List[Dict[str, Any]] = []
        candidate_prefs: Optional[Dict[str, Any]] = None
        saved_jobs_map: Dict[str, str] = {}  # opp_id -> saved_job_id

        if current_user_id:
            # Saved jobs
            saved_records = session.execute(
                select(SavedJobRecord).where(SavedJobRecord.user_id == current_user_id)
            ).scalars().all()
            for sj in saved_records:
                saved_jobs_map[sj.opportunity_id] = sj.id

            # Profile & skills
            prof = session.execute(
                select(CandidateProfile).where(CandidateProfile.user_id == current_user_id)
            ).scalars().first()
            if prof:
                candidate_profile_dict = {
                    "city": prof.city,
                    "state": prof.state,
                    "country": prof.country,
                    "experience": [
                        {
                            "company": exp.company,
                            "role": exp.role,
                            "years_experience": 2.0,  # approximate if start/end dates
                        }
                        for exp in prof.experience
                    ],
                    "education": [
                        {
                            "institution": edu.institution,
                            "degree": edu.degree,
                            "field_of_study": edu.field_of_study,
                        }
                        for edu in prof.education
                    ],
                }

                # Skills
                candidate_skills = [
                    {
                        "skill_name": sk.skill_name,
                        "proficiency": sk.proficiency,
                        "years_experience": sk.years_experience,
                        "provenance": sk.provenance,
                        "is_confirmed": True,
                    }
                    for sk in prof.skills
                ]

                # Preferences
                if prof.preferences:
                    candidate_prefs = {
                        "remote_preference": prof.preferences.remote_preference,
                        "min_salary": prof.preferences.min_salary,
                        "max_salary": prof.preferences.max_salary,
                    }

        # Sorting
        if filters.sort_by == SearchSortOption.MOST_RECENT:
            query = query.order_by(CanonicalOpportunityRecord.first_seen_at.desc())
        elif filters.sort_by == SearchSortOption.HIGHEST_SALARY:
            query = query.order_by(
                func.coalesce(CanonicalOpportunityRecord.max_salary, CanonicalOpportunityRecord.min_salary).desc().nullslast()
            )
        else:
            # Default or BEST_FIT
            query = query.order_by(
                CanonicalOpportunityRecord.last_verified_at.desc().nullslast(),
                CanonicalOpportunityRecord.first_seen_at.desc(),
            )

        # Pagination
        offset = (page - 1) * page_size
        results = session.execute(query.offset(offset).limit(page_size)).scalars().all()

        items: List[JobSearchResultItem] = []
        for opp in results:
            is_saved = opp.id in saved_jobs_map
            saved_job_id = saved_jobs_map.get(opp.id)

            skill_fit_score: Optional[float] = None
            elig_status: Optional[EligibilityStatus] = None
            matched_preview: List[str] = []
            missing_preview: List[str] = []

            if current_user_id and candidate_skills:
                opp_dict = {
                    "workplace_type": opp.workplace_type,
                    "is_remote": opp.is_remote,
                    "city": opp.city,
                    "country": opp.country,
                    "title": opp.title,
                    "description_clean": opp.description_clean,
                    "required_skills_json": opp.required_skills_json or [],
                }
                fit_breakdown = MatchingService.compute_skill_fit(
                    candidate_skills=candidate_skills,
                    job_required_skills=opp.required_skills_json or [],
                )
                skill_fit_score = fit_breakdown.fit_score
                matched_preview = fit_breakdown.matched_required_skills[:4]
                missing_preview = fit_breakdown.missing_required_skills[:3]

                elig_breakdown = MatchingService.evaluate_eligibility(
                    candidate_profile=candidate_profile_dict,
                    opportunity=opp_dict,
                )
                elig_status = elig_breakdown.status

            items.append(
                JobSearchResultItem(
                    id=opp.id,
                    title=opp.title,
                    company_name=opp.company_name,
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
                    required_skills=opp.required_skills_json or [],
                    application_url=opp.application_url,
                    verification_status=opp.verification_status,
                    freshness_state=opp.freshness_state,
                    first_seen_at=opp.first_seen_at,
                    last_verified_at=opp.last_verified_at,
                    source_name=opp.source.display_name if opp.source else "Core Feed",
                    is_saved=is_saved,
                    saved_job_id=saved_job_id,
                    skill_fit_score=skill_fit_score,
                    eligibility_status=elig_status,
                    matched_skills_preview=matched_preview,
                    missing_skills_preview=missing_preview,
                )
            )

        # If candidate requested BEST_FIT sorting and has skills, re-sort items by skill fit & eligibility
        if filters.sort_by == SearchSortOption.BEST_FIT and current_user_id and candidate_skills:
            items.sort(
                key=lambda x: (
                    1 if x.eligibility_status == EligibilityStatus.MEETS_REQUIREMENTS else 0,
                    x.skill_fit_score or 0.0,
                ),
                reverse=True,
            )
        elif filters.sort_by == SearchSortOption.SKILL_MATCH and current_user_id and candidate_skills:
            items.sort(key=lambda x: x.skill_fit_score or 0.0, reverse=True)

        coverage = cls.get_source_coverage_metadata(session)
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        return JobSearchResponse(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            applied_filters=filters.model_dump(exclude_none=True),
            source_coverage=coverage,
        )

