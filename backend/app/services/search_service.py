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
import re
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, case, cast, func, or_, select, String
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    CanonicalOpportunityRecord,
    CandidateOpportunityFeedbackRecord,
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


SMART_SEARCH_SYNONYMS: Dict[str, List[str]] = {
    # Web & Frontend Development
    "webdev": ["web developer", "web development", "frontend", "front-end", "full stack", "fullstack", "react", "javascript", "typescript", "html", "css", "node.js"],
    "web dev": ["web developer", "web development", "frontend", "front-end", "full stack", "fullstack", "react", "javascript", "typescript", "html", "css", "node.js"],
    "web development": ["web developer", "web development", "frontend", "front-end", "full stack", "fullstack", "react", "javascript", "typescript"],
    "web developer": ["web developer", "web development", "frontend", "full stack", "fullstack", "javascript", "typescript", "react"],
    "frontend": ["frontend", "front-end", "react", "vue", "angular", "javascript", "typescript", "ui engineer", "html", "css", "tailwind", "next.js"],
    "front end": ["frontend", "front-end", "react", "vue", "angular", "javascript", "typescript", "ui engineer", "next.js"],
    "react": ["react", "react.js", "reactjs", "react native", "next.js", "frontend"],
    "reactjs": ["react", "react.js", "react native", "frontend", "next.js"],
    "react.js": ["react", "react.js", "react native", "frontend", "next.js"],
    "vue": ["vue", "vue.js", "vuejs", "frontend", "javascript"],
    "angular": ["angular", "angularjs", "frontend", "typescript"],
    "next.js": ["next.js", "nextjs", "react", "frontend", "full stack"],
    "nextjs": ["next.js", "nextjs", "react", "frontend", "full stack"],
    "typescript": ["typescript", "ts", "javascript", "frontend", "full stack"],
    "javascript": ["javascript", "js", "typescript", "frontend", "web"],
    "tailwind": ["tailwind", "tailwind css", "frontend", "css"],
    "html": ["html", "css", "frontend", "web"],
    "css": ["css", "tailwind", "frontend", "web"],

    # Backend Development
    "backend": ["backend", "back-end", "node", "python", "java", "api", "golang", "go", "fastapi", "django", "postgresql", "microservices"],
    "back end": ["backend", "back-end", "node", "python", "java", "api", "golang", "go", "fastapi", "django"],
    "node": ["node", "node.js", "nodejs", "express", "backend", "nestjs"],
    "nodejs": ["node", "node.js", "express", "backend", "nestjs"],
    "node.js": ["node", "node.js", "express", "backend", "nestjs"],
    "python": ["python", "django", "fastapi", "flask", "backend", "data engineering", "pandas"],
    "fastapi": ["fastapi", "python", "backend", "api"],
    "django": ["django", "python", "backend", "api"],
    "golang": ["golang", "go", "backend", "distributed systems"],
    "go": ["golang", "go", "backend", "systems engineer"],
    "java": ["java", "spring boot", "backend", "microservices"],
    "sql": ["sql", "postgresql", "mysql", "database", "data"],
    "postgresql": ["postgresql", "postgres", "sql", "database"],

    # Full Stack
    "fullstack": ["fullstack", "full-stack", "full stack", "mern", "software engineer"],
    "full stack": ["fullstack", "full-stack", "full stack", "mern", "software engineer"],
    "software engineer": ["software engineer", "developer", "full stack", "backend", "frontend", "software development"],
    "developer": ["software engineer", "developer", "programmer", "full stack", "coder"],

    # AI, ML & Data
    "ai": ["artificial intelligence", "machine learning", "ml", "llm", "deep learning", "nlp", "pytorch"],
    "ml": ["machine learning", "deep learning", "ai", "artificial intelligence", "nlp", "pytorch", "tensorflow"],
    "machine learning": ["machine learning", "ml", "ai", "deep learning", "pytorch", "tensorflow", "model training"],
    "data science": ["data science", "data scientist", "analytics", "python", "machine learning", "sql"],
    "datascience": ["data science", "data scientist", "analytics", "python", "machine learning", "sql"],
    "data analyst": ["data analyst", "analytics", "sql", "tableau", "power bi", "bi"],
    "data engineer": ["data engineer", "etl", "pipeline", "sql", "spark", "kafka", "python"],

    # Cloud & DevOps
    "devops": ["devops", "cloud", "aws", "docker", "kubernetes", "k8s", "ci/cd", "sre", "terraform"],
    "cloud": ["cloud", "aws", "azure", "gcp", "devops", "kubernetes"],
    "sre": ["site reliability", "sre", "devops", "infrastructure", "kubernetes"],
    "kubernetes": ["kubernetes", "k8s", "docker", "devops", "cloud"],
    "aws": ["aws", "cloud", "amazon web services", "devops"],
    "docker": ["docker", "containers", "kubernetes", "devops"],

    # Mobile
    "mobile": ["mobile", "android", "ios", "react native", "flutter", "swift", "kotlin"],
    "android": ["android", "kotlin", "mobile"],
    "ios": ["ios", "swift", "mobile"],
    "flutter": ["flutter", "dart", "mobile"],
    "react native": ["react native", "react", "mobile"],

    # Design
    "ui/ux": ["ui/ux", "product designer", "figma", "user experience", "user interface", "design systems"],
    "design": ["product designer", "ui/ux", "figma", "graphic design", "visual designer"],
    "figma": ["figma", "ui/ux", "product design", "prototyping"],

    # Marketing & Growth
    "marketing": ["marketing", "growth marketing", "seo", "sem", "content marketing", "social media", "campaign"],
    "growth": ["growth marketing", "growth", "performance marketing", "seo", "user acquisition"],
    "seo": ["seo", "content marketing", "search engine optimization", "organic growth"],

    # Sales & Business Development
    "sales": ["sales", "b2b sales", "business development", "bdr", "sdr", "account executive", "deal closing"],
    "b2b sales": ["b2b sales", "sales", "account executive", "deal closing", "enterprise sales"],
    "bdr": ["business development representative", "bdr", "sdr", "sales", "outreach"],
    "sdr": ["sales development representative", "sdr", "bdr", "sales", "lead generation"],
    "account executive": ["account executive", "b2b sales", "pipeline management", "deal closing", "enterprise sales"],

    # Finance, Accounting & Legal
    "finance": ["finance", "accounting", "financial analyst", "financial modeling", "audit", "p&l"],
    "accounting": ["accounting", "finance", "quickbooks", "audit", "bookkeeping", "cpa"],
    "legal": ["legal", "corporate law", "commercial contracts", "compliance", "counsel", "regulatory"],
    "compliance": ["compliance", "regulatory compliance", "risk management", "audit", "internal controls"],
    "contracts": ["commercial contracts", "contracts", "legal review", "contract negotiation"],

    # Product, HR & Operations
    "product": ["product manager", "pm", "product strategy", "roadmapping", "agile", "scrum"],
    "pm": ["product manager", "product management", "technical product manager"],
    "hr": ["human resources", "talent acquisition", "recruiter", "people ops", "onboarding"],
    "recruiter": ["recruiter", "talent acquisition", "technical recruiter", "sourcing", "hr"],
    "operations": ["operations", "supply chain", "logistics", "procurement", "vendor management"],
    "customer success": ["customer success", "client onboarding", "account support", "csm", "retention"],
    "support": ["customer support", "technical support", "help desk", "client support"],
}


def expand_search_terms(raw_query: str) -> List[str]:
    """Expands user search query using semantic tech & role synonyms."""
    clean = raw_query.strip().lower()
    terms: Set[str] = {clean}

    # Direct synonym expansion
    if clean in SMART_SEARCH_SYNONYMS:
        terms.update(SMART_SEARCH_SYNONYMS[clean])

    # Word-level expansion for multi-word queries
    words = [w for w in re.split(r"[\s,\-/]+", clean) if len(w) > 1 and w not in {"in", "for", "with", "and", "a", "the", "to", "of", "or"}]
    for w in words:
        terms.add(w)
        if w in SMART_SEARCH_SYNONYMS:
            terms.update(SMART_SEARCH_SYNONYMS[w])

    return list(terms)


# In-memory high-speed cache for job search queries and source coverage
_JOB_SEARCH_CACHE: Dict[str, Tuple[float, JobSearchResponse]] = {}
_JOB_CACHE_TTL = 30.0

_COVERAGE_CACHE: Optional[Tuple[float, SourceCoverageMetadata]] = None
_COVERAGE_CACHE_TTL = 60.0


class SearchService:
    """Orchestrates candidate search queries, source coverage health, and personalized ranking."""

    @classmethod
    def get_source_coverage_metadata(cls, session: Session) -> SourceCoverageMetadata:
        """Inspects all configured sources to report platform coverage and partial result status (cached for 60s)."""
        global _COVERAGE_CACHE
        if _COVERAGE_CACHE:
            ts, cached_cov = _COVERAGE_CACHE
            if time.time() - ts < _COVERAGE_CACHE_TTL:
                return cached_cov

        sources = session.execute(select(JobSourceRecord)).scalars().all()
        total_sources = len(sources)
        healthy_count = 0
        degraded_count = 0
        coverage_items: List[SourceCoverageItem] = []

        # Single aggregated query to count active opportunities per source
        counts_map = dict(
            session.execute(
                select(
                    CanonicalOpportunityRecord.source_id,
                    func.count(CanonicalOpportunityRecord.id)
                )
                .where(CanonicalOpportunityRecord.is_suppressed.is_(False))
                .group_by(CanonicalOpportunityRecord.source_id)
            ).all()
        )

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

            opp_count = counts_map.get(src.id, 0)
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

        cov_meta = SourceCoverageMetadata(
            total_configured_sources=total_sources,
            healthy_sources_count=healthy_count,
            degraded_sources_count=degraded_count,
            is_partial_results=is_partial,
            coverage_details=coverage_items,
        )
        _COVERAGE_CACHE = (time.time(), cov_meta)
        return cov_meta

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

        cache_key = f"{current_user_id or ''}:{page}:{page_size}:{filters.model_dump_json()}"
        if cache_key in _JOB_SEARCH_CACHE:
            ts, cached_res = _JOB_SEARCH_CACHE[cache_key]
            if time.time() - ts < _JOB_CACHE_TTL:
                return cached_res

        # Base query: non-suppressed active opportunities
        query = select(CanonicalOpportunityRecord).options(
            joinedload(CanonicalOpportunityRecord.source)
        ).where(
            CanonicalOpportunityRecord.is_suppressed.is_(False),
            CanonicalOpportunityRecord.is_active.is_(True),
        )

        # 1. Fulltext / Smart Keyword Query
        expanded = []
        if filters.query:
            expanded = expand_search_terms(filters.query)
            query_clauses = []
            for t in expanded:
                if len(t) <= 3:
                    # Guard short terms from matching loose substrings inside description words
                    query_clauses.extend([
                        func.lower(CanonicalOpportunityRecord.title).ilike(f"%{t}%"),
                        cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f'%"{t}"%'),
                    ])
                else:
                    term = f"%{t}%"
                    query_clauses.extend([
                        func.lower(CanonicalOpportunityRecord.title).ilike(term),
                        func.lower(CanonicalOpportunityRecord.company_name).ilike(term),
                        func.lower(CanonicalOpportunityRecord.description_clean).ilike(term),
                        func.lower(CanonicalOpportunityRecord.city).ilike(term),
                        cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(term),
                    ])
            if query_clauses:
                query = query.where(or_(*query_clauses))

        # 1b. Specific Skills filter (Multi-filter support across required skills and title)
        if filters.skills:
            skill_clauses = []
            for sk in filters.skills:
                clean_sk = sk.strip().lower()
                if clean_sk:
                    expanded_sk = expand_search_terms(clean_sk)
                    for st in expanded_sk:
                        if len(st) <= 3:
                            skill_clauses.extend([
                                cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f'%"{st}"%'),
                                func.lower(CanonicalOpportunityRecord.title).ilike(f"%{st}%"),
                            ])
                        else:
                            st_term = f"%{st}%"
                            skill_clauses.extend([
                                cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(st_term),
                                func.lower(CanonicalOpportunityRecord.title).ilike(st_term),
                            ])
            if skill_clauses:
                query = query.where(or_(*skill_clauses))

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

        # 6. Employment Types & Fresher/Internship Detection
        if filters.is_internship is not None and filters.is_internship:
            query = query.where(
                or_(
                    CanonicalOpportunityRecord.employment_type == "INTERNSHIP",
                    func.lower(CanonicalOpportunityRecord.title).ilike("%intern%"),
                )
            )
        if filters.is_fresher_friendly is not None and filters.is_fresher_friendly:
            query = query.where(
                or_(
                    CanonicalOpportunityRecord.employment_type == "INTERNSHIP",
                    func.lower(CanonicalOpportunityRecord.title).ilike("%fresher%"),
                    func.lower(CanonicalOpportunityRecord.title).ilike("%entry level%"),
                    func.lower(CanonicalOpportunityRecord.title).ilike("%graduate%"),
                    func.lower(CanonicalOpportunityRecord.title).ilike("%junior%"),
                    func.lower(CanonicalOpportunityRecord.title).ilike("%trainee%"),
                    func.lower(CanonicalOpportunityRecord.description_clean).ilike("%0-1 year%"),
                )
            )
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

        # Load candidate profile, saved jobs, and feedback if user logged in
        candidate_profile_dict: Optional[Dict[str, Any]] = None
        candidate_skills: List[Dict[str, Any]] = []
        candidate_prefs: Optional[Dict[str, Any]] = None
        saved_jobs_map: Dict[str, str] = {}  # opp_id -> saved_job_id
        candidate_feedback_map: Dict[str, str] = {}  # opp_id -> feedback_category

        if current_user_id:
            # 1. Saved jobs
            saved_records = session.execute(
                select(SavedJobRecord).where(SavedJobRecord.user_id == current_user_id)
            ).scalars().all()
            for sj in saved_records:
                saved_jobs_map[sj.opportunity_id] = sj.id

            # 2. Candidate Opportunity Feedback (Personalized Recommendation Tuning)
            fb_records = session.execute(
                select(CandidateOpportunityFeedbackRecord).where(
                    CandidateOpportunityFeedbackRecord.user_id == current_user_id
                )
            ).scalars().all()
            for fb in fb_records:
                candidate_feedback_map[fb.opportunity_id] = fb.feedback_category

            # 3. Profile & skills
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

        # Build SQL relevance ranking expression
        score_parts = []
        if filters.query:
            clean_q = filters.query.strip().lower()
            score_parts.extend([
                case((func.lower(CanonicalOpportunityRecord.title) == clean_q, 250), else_=0),
                case((func.lower(CanonicalOpportunityRecord.title).ilike(f"%{clean_q}%"), 150), else_=0),
                case((cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f'%"{clean_q}"%'), 120), else_=0),
                case((cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f"%{clean_q}%"), 70), else_=0),
                case((func.lower(CanonicalOpportunityRecord.company_name).ilike(f"%{clean_q}%"), 40), else_=0),
            ])
            for syn in expanded[:8]:
                if syn != clean_q and len(syn) > 2:
                    score_parts.append(
                        case((func.lower(CanonicalOpportunityRecord.title).ilike(f"%{syn}%"), 60), else_=0)
                    )
                    score_parts.append(
                        case((cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f"%{syn}%"), 45), else_=0)
                    )

        if filters.skills:
            for sk in filters.skills:
                c_sk = sk.strip().lower()
                if c_sk:
                    score_parts.extend([
                        case((cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f'%"{c_sk}"%'), 120), else_=0),
                        case((cast(CanonicalOpportunityRecord.required_skills_json, String).ilike(f"%{c_sk}%"), 70), else_=0),
                        case((func.lower(CanonicalOpportunityRecord.title).ilike(f"%{c_sk}%"), 80), else_=0),
                    ])

        if filters.role:
            c_role = filters.role.strip().lower()
            if c_role:
                score_parts.extend([
                    case((func.lower(CanonicalOpportunityRecord.title) == c_role, 200), else_=0),
                    case((func.lower(CanonicalOpportunityRecord.title).ilike(f"%{c_role}%"), 120), else_=0),
                ])

        sql_relevance = sum(score_parts) if score_parts else None

        # Sorting
        if filters.sort_by == SearchSortOption.MOST_RECENT:
            query = query.order_by(CanonicalOpportunityRecord.first_seen_at.desc())
        elif filters.sort_by == SearchSortOption.HIGHEST_SALARY:
            query = query.order_by(
                func.coalesce(CanonicalOpportunityRecord.max_salary, CanonicalOpportunityRecord.min_salary).desc().nullslast()
            )
        elif filters.sort_by in (SearchSortOption.RELEVANCE, SearchSortOption.BEST_FIT):
            if sql_relevance is not None:
                query = query.order_by(
                    sql_relevance.desc(),
                    CanonicalOpportunityRecord.last_verified_at.desc().nullslast(),
                    CanonicalOpportunityRecord.first_seen_at.desc(),
                )
            else:
                query = query.order_by(
                    CanonicalOpportunityRecord.last_verified_at.desc().nullslast(),
                    CanonicalOpportunityRecord.first_seen_at.desc(),
                )
        else:
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
            fb_status = candidate_feedback_map.get(opp.id)

            skill_fit_score: Optional[float] = None
            elig_status: Optional[EligibilityStatus] = None
            matched_preview: List[str] = []
            missing_preview: List[str] = []
            is_cold_start: bool = False
            cold_start_explanation: Optional[str] = None

            # Calculate item dynamic relevance score
            item_rel = 0.0
            t_low = (opp.title or "").lower()
            c_low = (opp.company_name or "").lower()
            s_low = [s.lower() for s in (opp.required_skills_json or [])]

            if filters.query:
                clean_q = filters.query.strip().lower()
                if clean_q in t_low:
                    item_rel += 150.0
                tokens = [w for w in re.split(r"[\s,\-/]+", clean_q) if len(w) > 1]
                for tk in tokens:
                    if tk in t_low:
                        item_rel += 40.0
                for sk in s_low:
                    if clean_q == sk:
                        item_rel += 120.0
                    elif clean_q in sk:
                        item_rel += 70.0
                    for tk in tokens:
                        if tk == sk:
                            item_rel += 80.0
                        elif tk in sk:
                            item_rel += 35.0
                for syn in (expanded or []):
                    if syn in t_low:
                        item_rel += 35.0
                    for sk in s_low:
                        if syn in sk:
                            item_rel += 30.0

            if filters.skills:
                for sk in filters.skills:
                    c_sk = sk.strip().lower()
                    if any(c_sk == s for s in s_low):
                        item_rel += 100.0
                    elif any(c_sk in s for s in s_low):
                        item_rel += 60.0
                    if c_sk in t_low:
                        item_rel += 70.0

            if filters.role:
                c_role = filters.role.strip().lower()
                if c_role in t_low:
                    item_rel += 120.0

            opp_dict = {
                "workplace_type": opp.workplace_type,
                "is_remote": opp.is_remote,
                "city": opp.city,
                "country": opp.country,
                "title": opp.title,
                "description_clean": opp.description_clean,
                "required_skills_json": opp.required_skills_json or [],
            }

            if current_user_id:
                if candidate_skills and len(candidate_skills) >= 1:
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
                else:
                    # Module B: Cold-Start Recommendation Engine
                    # Synthesize match from preferred roles, education fields, and location
                    target_roles = (candidate_prefs.get("preferred_roles") if candidate_prefs else []) or []
                    if prof and prof.headline and prof.headline not in target_roles:
                        target_roles.append(prof.headline)

                    role_overlap = any(r.lower() in opp.title.lower() for r in target_roles) if target_roles else False
                    edu_fields = [e.get("field_of_study", "").lower() for e in (candidate_profile_dict.get("education") or [])]
                    edu_overlap = any(ef in opp.description_clean.lower() for ef in edu_fields if ef)

                    if role_overlap or edu_overlap:
                        is_cold_start = True
                        base_score = 60.0
                        if role_overlap:
                            base_score += 15.0
                        if edu_overlap:
                            base_score += 10.0
                        skill_fit_score = min(base_score, 85.0)
                        elig_status = EligibilityStatus.MEETS_REQUIREMENTS
                        cold_start_explanation = (
                            "Recommended from your target roles and educational background. "
                            "Upload or confirm resume skills to unlock precision 100% evidence matching."
                        )

                # Module E: Candidate Recommendation Feedback Tuning
                if fb_status and skill_fit_score is not None:
                    if fb_status == "WRONG_SKILLS":
                        skill_fit_score = round(skill_fit_score * 0.50, 1)
                    elif fb_status == "LOCATION_UNSUITABLE":
                        skill_fit_score = round(skill_fit_score * 0.60, 1)
                    elif fb_status == "RELEVANT":
                        skill_fit_score = min(100.0, round(skill_fit_score * 1.10, 1))
                    elif fb_status in ("NOT_RELEVANT", "ALREADY_APPLIED", "JOB_CLOSED"):
                        skill_fit_score = round(skill_fit_score * 0.20, 1)

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
                    application_url=(
                        opp.application_url
                        if opp.application_url and "jooble.org" not in opp.application_url.lower()
                        else f"https://www.google.com/search?q={urllib.parse.quote_plus(f'{opp.company_name} {opp.title} job apply')}"
                    ),
                    verification_status=opp.verification_status,
                    freshness_state=opp.freshness_state,
                    first_seen_at=opp.first_seen_at,
                    last_verified_at=opp.last_verified_at,
                    source_name=opp.source.display_name if opp.source else "Core Feed",
                    is_saved=is_saved,
                    saved_job_id=saved_job_id,
                    skill_fit_score=skill_fit_score,
                    eligibility_status=elig_status,
                    is_cold_start=is_cold_start,
                    cold_start_explanation=cold_start_explanation,
                    candidate_feedback_status=fb_status,
                    relevance_score=round(item_rel, 1) if (filters.query or filters.skills or filters.role) else None,
                    matched_skills_preview=matched_preview,
                    missing_skills_preview=missing_preview,
                )
            )

        # Multi-factor candidate and relevance re-ranking
        if filters.sort_by == SearchSortOption.RELEVANCE:
            items.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)
        elif filters.sort_by == SearchSortOption.BEST_FIT:
            if current_user_id and candidate_skills:
                items.sort(
                    key=lambda x: (
                        1 if x.eligibility_status == EligibilityStatus.MEETS_REQUIREMENTS else 0,
                        (x.skill_fit_score or 0.0) * 0.6 + min(100.0, (x.relevance_score or 0.0) / 3.0) * 0.4,
                    ),
                    reverse=True,
                )
            elif filters.query or filters.skills or filters.role:
                items.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)
        elif filters.sort_by == SearchSortOption.SKILL_MATCH and current_user_id and candidate_skills:
            items.sort(key=lambda x: x.skill_fit_score or 0.0, reverse=True)
            items.sort(key=lambda x: x.skill_fit_score or 0.0, reverse=True)

        coverage = cls.get_source_coverage_metadata(session)
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        response_obj = JobSearchResponse(
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
        _JOB_SEARCH_CACHE[cache_key] = (time.time(), response_obj)
        return response_obj

