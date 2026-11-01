"""
RIGHT FIT API Contracts — Matching, Search & Discovery Schemas
Version: 1.0.0
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# Enumerations
# ==============================================================================

class EligibilityStatus(StrEnum):
    """Evaluation of hard legal, education, location, or experience criteria."""
    MEETS_REQUIREMENTS = "MEETS_REQUIREMENTS"
    DOES_NOT_MEET_REQUIREMENTS = "DOES_NOT_MEET_REQUIREMENTS"
    UNKNOWN = "UNKNOWN"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class CriterionEvaluationStatus(StrEnum):
    """Evaluation status for an individual eligibility rule."""
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class AlertFrequency(StrEnum):
    """Notification cadence for saved searches."""
    INSTANT = "INSTANT"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    NEVER = "NEVER"


class SearchSortOption(StrEnum):
    """Supported candidate-facing sorting methods."""
    RELEVANCE = "RELEVANCE"
    BEST_FIT = "BEST_FIT"
    MOST_RECENT = "MOST_RECENT"
    HIGHEST_SALARY = "HIGHEST_SALARY"
    SKILL_MATCH = "SKILL_MATCH"


# ==============================================================================
# Skill Fit & Evidence DTOs
# ==============================================================================

class MatchedSkillEvidence(BaseModel):
    """Evidence connecting a matched skill to candidate resume or profile."""
    skill: str
    source_type: str = Field(..., description="'RESUME_EXTRACTION', 'PROFILE_SKILL', or 'EXPERIENCE'")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_excerpt: Optional[str] = Field(default=None, description="Direct text snippet from resume or experience")
    years_experience: Optional[float] = None
    is_confirmed: bool = Field(default=True, description="True if confirmed by candidate review")
    recency_years: Optional[float] = Field(default=None, description="Years since skill was last verified or practiced")
    is_stale_warning: bool = Field(default=False, description="Flagged if skill has not been verified/demonstrated in > 3 years")
    recency_note: Optional[str] = Field(default=None, description="Recency guidance for interview preparation")


class SkillFitBreakdown(BaseModel):
    """Detailed evidence-based comparison between job requirements and candidate skills."""
    fit_score: float = Field(..., ge=0.0, le=100.0, description="Skill fit percentage [0 to 100].")
    total_required_skills: int
    matched_required_count: int
    matched_required_skills: List[str] = Field(default_factory=list)
    related_required_skills: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Skills satisfied via relationship taxonomy (e.g. parent-child, transferable) with relationship strength"
    )
    missing_required_skills: List[str] = Field(default_factory=list)
    total_preferred_skills: int = 0
    matched_preferred_count: int = 0
    matched_preferred_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    unconfirmed_skills: List[str] = Field(
        default_factory=list,
        description="Candidate skills extracted from resume but pending candidate review confirmation"
    )
    skill_evidence: List[MatchedSkillEvidence] = Field(default_factory=list)


# ==============================================================================
# Mandatory Eligibility DTOs
# ==============================================================================

class CriterionEvaluation(BaseModel):
    """Individual eligibility constraint evaluation."""
    criterion_name: str
    required_value: str
    candidate_value: Optional[str] = None
    status: CriterionEvaluationStatus
    explanation: str


class EligibilityBreakdown(BaseModel):
    """Overall mandatory eligibility verdict evaluated independently of skill fit."""
    status: EligibilityStatus
    summary: str
    criteria: List[CriterionEvaluation] = Field(default_factory=list)
    has_missing_candidate_data: bool = Field(
        default=False,
        description="True if evaluation contains UNKNOWN due to missing profile information"
    )


# ==============================================================================
# Multi-Dimensional Match & Explanation
# ==============================================================================

class MatchExplanationResponse(BaseModel):
    """Full transparent match breakdown across skill fit, eligibility, trust, and freshness."""
    opportunity_id: str
    candidate_id: str
    skill_fit: SkillFitBreakdown
    eligibility: EligibilityBreakdown
    verification_status: str
    verification_explanation: str
    freshness_state: str
    freshness_explanation: str
    preference_match: Dict[str, Any] = Field(
        default_factory=dict,
        description="Alignment with candidate location, remote, and salary preferences"
    )
    ranking_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Deterministic composite sort score combining all dimensions"
    )
    computed_at: datetime


# ==============================================================================
# Search & Discovery Envelopes
# ==============================================================================

class SourceCoverageItem(BaseModel):
    """Health and freshness signal for an individual job source."""
    source_key: str
    display_name: str
    status: str  # ACTIVE, DEGRADED, OUTAGE
    last_run_status: Optional[str] = None
    records_count: int = 0
    outage_reason: Optional[str] = None


class SourceCoverageMetadata(BaseModel):
    """Transparent indicator of upstream coverage and potential partial results."""
    total_configured_sources: int
    healthy_sources_count: int
    degraded_sources_count: int
    is_partial_results: bool = Field(
        default=False,
        description="True if one or more upstream job sources are unavailable, alerting candidates to potential missing listings"
    )
    coverage_details: List[SourceCoverageItem] = Field(default_factory=list)


class JobSearchFilters(BaseModel):
    """Candidate search query parameters."""
    query: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_remote: Optional[bool] = None
    is_internship: Optional[bool] = None
    is_fresher_friendly: Optional[bool] = None
    workplace_types: Optional[List[str]] = None  # REMOTE, HYBRID, ON_SITE
    employment_types: Optional[List[str]] = None  # FULL_TIME, CONTRACT, etc.
    skills: Optional[List[str]] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = "USD"
    sources: Optional[List[str]] = None
    verification_statuses: Optional[List[str]] = None
    freshness_states: Optional[List[str]] = None
    sort_by: SearchSortOption = SearchSortOption.BEST_FIT


class JobSearchResultItem(BaseModel):
    """Single career opportunity item in search result set."""
    id: str
    title: str
    company_name: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    workplace_type: str
    is_remote: bool
    employment_type: str
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = None
    salary_period: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    application_url: str
    verification_status: str
    freshness_state: str
    first_seen_at: datetime
    last_verified_at: Optional[datetime] = None
    source_name: str
    is_saved: bool = False
    saved_job_id: Optional[str] = None
    skill_fit_score: Optional[float] = None
    eligibility_status: Optional[EligibilityStatus] = None
    is_cold_start: bool = Field(default=False, description="True if recommended under cold-start criteria from education/goals without verified resume skills")
    cold_start_explanation: Optional[str] = None
    candidate_feedback_status: Optional[str] = Field(default=None, description="Previous candidate feedback on this opportunity: RELEVANT, NOT_RELEVANT, WRONG_SKILLS, etc.")
    relevance_score: Optional[float] = Field(default=None, description="Dynamic smart search relevance score matching query, skills, and role")
    matched_skills_preview: List[str] = Field(default_factory=list)
    missing_skills_preview: List[str] = Field(default_factory=list)


class JobSearchResponse(BaseModel):
    """Envelope for paginated job search results with transparency metadata."""
    items: List[JobSearchResultItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    source_coverage: SourceCoverageMetadata


# ==============================================================================
# Job Details Envelope
# ==============================================================================

class JobDetailResponse(BaseModel):
    """Comprehensive job posting details including provenance, verification, and candidate fit."""
    id: str
    external_job_id: str
    title: str
    company_name: str
    department: Optional[str] = None
    description_clean: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    workplace_type: str
    is_remote: bool
    employment_type: str
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = None
    salary_period: Optional[str] = None
    is_salary_estimated: bool = False
    required_skills: List[str] = Field(default_factory=list)
    application_url: str
    source_name: str
    source_key: str
    source_published_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    first_seen_at: datetime
    last_seen_at: datetime
    last_verified_at: Optional[datetime] = None
    verification_status: str
    freshness_state: str
    is_saved: bool = False
    saved_job_id: Optional[str] = None
    match_breakdown: Optional[MatchExplanationResponse] = None
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# Saved Jobs & Saved Searches Schemas
# ==============================================================================

class SavedJobCreateRequest(BaseModel):
    opportunity_id: str
    notes: Optional[str] = Field(default=None, max_length=1000)


class SavedJobUpdateRequest(BaseModel):
    notes: Optional[str] = Field(default=None, max_length=1000)


class SavedJobResponse(BaseModel):
    id: str
    user_id: str
    opportunity_id: str
    notes: Optional[str] = None
    created_at: datetime
    opportunity: Optional[JobSearchResultItem] = None


class SavedSearchCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    query: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    alert_enabled: bool = Field(default=False)
    alert_frequency: AlertFrequency = Field(default=AlertFrequency.DAILY)


class SavedSearchUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    alert_enabled: Optional[bool] = None
    alert_frequency: Optional[AlertFrequency] = None


class SavedSearchResponse(BaseModel):
    id: str
    user_id: str
    name: str
    query_json: Dict[str, Any] = Field(default_factory=dict)
    filters_json: Dict[str, Any] = Field(default_factory=dict)
    alert_enabled: bool
    alert_frequency: AlertFrequency
    last_notified_at: Optional[datetime] = None
    matching_jobs_count: int = 0
    created_at: datetime
    updated_at: datetime


class AlertDeliveryLogResponse(BaseModel):
    id: str
    saved_search_id: str
    user_id: str
    opportunity_ids: List[str] = Field(default_factory=list)
    delivered_at: datetime
    delivery_channel: str
    status: str

