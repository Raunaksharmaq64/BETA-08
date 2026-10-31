"""
RIGHT FIT API Contracts — Resume Intelligence Schemas
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ParsingStatus(str, Enum):
    """Resume parsing task lifecycle states."""
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    PARSED = "PARSED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DELETION_PENDING = "DELETION_PENDING"
    DELETED = "DELETED"


class ConfidenceLevel(str, Enum):
    """Extraction confidence classification for candidate presentation."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"


class ReviewStatus(str, Enum):
    """Review status for individual fields and overall extraction."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"


class ReviewAction(str, Enum):
    """Candidate review actions on extracted candidate fields."""
    CONFIRM = "CONFIRM"
    EDIT_AND_CONFIRM = "EDIT_AND_CONFIRM"
    REJECT = "REJECT"
    MARK_INCORRECT = "MARK_INCORRECT"


class EvidenceDTO(BaseModel):
    """Supporting document evidence for an extracted field."""
    field_id: str = Field(description="Unique identifier for the evidenced field")
    field_name: str = Field(description="Semantic field path, e.g. 'personal_info.phone' or 'skills.languages'")
    extracted_value: Any = Field(description="Original value extracted from document")
    source_section: Optional[str] = Field(default=None, description="Document section containing evidence")
    excerpt: str = Field(description="Exact snippet or sentence from resume supporting this fact")
    page_number: Optional[int] = Field(default=None, description="Page number where excerpt was located")
    extraction_method: str = Field(default="STRUCTURED_PARSER", description="Method: REGEX, SECTION_PARSER, KEYWORD_MATCHER")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Raw algorithmic confidence score")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH)
    review_status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    user_correction: Optional[Any] = Field(default=None, description="Candidate-corrected value if edited")
    reviewed_at: Optional[datetime] = None


class ResumeUploadResponse(BaseModel):
    """Response returned upon successful resume file upload."""
    resume_id: str
    version_id: str
    version_number: int
    version_label: str
    filename: str
    file_type: str
    file_size_bytes: int
    parsing_status: ParsingStatus
    uploaded_at: datetime


class ResumeVersionResponse(BaseModel):
    """Metadata for a specific version of a candidate resume."""
    id: str
    resume_id: str
    version_number: int
    version_label: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    parsing_status: ParsingStatus
    error_message: Optional[str] = None
    is_active: bool
    uploaded_at: datetime
    parsed_at: Optional[datetime] = None


class ResumeSummaryResponse(BaseModel):
    """Summary of a candidate resume including its active version."""
    id: str
    title: str
    active_version_id: Optional[str] = None
    active_version: Optional[ResumeVersionResponse] = None
    version_count: int = 1
    created_at: datetime
    updated_at: datetime


class ResumeExtractionResponse(BaseModel):
    """Structured candidate information extracted from a resume version."""
    resume_id: str
    version_id: str
    parsing_status: ParsingStatus
    personal_info: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    education: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    internships: List[Dict[str, Any]] = Field(default_factory=list)
    skills: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Explicit categorized skills (backward compatible alias)"
    )
    explicit_skills: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Skills directly documented in the dedicated Skills section"
    )
    inferred_skills: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Skills inferred from experience narratives or project descriptions"
    )
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    publications: List[Dict[str, Any]] = Field(default_factory=list)
    languages: List[Dict[str, Any]] = Field(default_factory=list)
    awards: List[Dict[str, Any]] = Field(default_factory=list)
    is_scanned_pdf: bool = False
    is_mixed_content: bool = False
    ocr_required: bool = False
    low_text_pages: List[int] = Field(default_factory=list)
    extraction_notes: List[str] = Field(default_factory=list)
    evidence_items: List[EvidenceDTO] = Field(default_factory=list)
    parsed_at: Optional[datetime] = None


class AISuggestionDTO(BaseModel):
    """Actionable improvement suggestion with explicit candidate evidence requirements."""
    id: str = Field(description="Unique suggestion ID")
    category: str = Field(description="BULLET_REWRITE, IMPACT_METRICS, SUMMARY_POLISH, SECTION_ORDER, SKILL_GAP, PROJECT_DESCRIPTION, MISSING_CONTEXT, VAGUE_TECHNICAL_SPEC, ACHIEVEMENT_STRUCTURE")
    target_section: str
    current_issue: str
    why_it_matters: str
    current_text: Optional[str] = None
    recommended_text: str
    evidence_required_from_candidate: str
    status: str = Field(default="PENDING", description="PENDING, ACCEPTED, REJECTED, EDITED")
    # Grounded evidence & candidate approval workflow fields
    original_content: Optional[str] = None
    identified_issue: Optional[str] = None
    suggested_rewrite: Optional[str] = None
    information_required_from_candidate: Optional[str] = None
    evidence_supporting_suggestion: Optional[str] = None
    confidence_level: str = Field(default="HIGH", description="HIGH, MEDIUM, LOW")
    edited_content: Optional[str] = None
    original_preserved: bool = True


class SuggestionActionRequest(BaseModel):
    """Request to accept, reject, edit, or regenerate an AI suggestion."""
    suggestion_id: str
    action: str = Field(description="ACCEPT, REJECT, EDIT, REGENERATE")
    edited_text: Optional[str] = None
    regeneration_guidance: Optional[str] = None


class SuggestionActionResponse(BaseModel):
    """Result of candidate action on an AI suggestion."""
    success: bool
    suggestion: AISuggestionDTO
    message: str


class ResumeAISuggestionsResponse(BaseModel):
    """Structured AI suggestions comparing current resume text with best practices."""
    resume_id: str
    version_id: str
    suggestions: List[AISuggestionDTO] = Field(default_factory=list)
    provider_used: str = Field(default="DETERMINISTIC_HEURISTIC")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QualityDimensionEvaluation(BaseModel):
    """Detailed deterministic critique for an individual quality dimension."""
    dimension_name: str
    score: float = Field(ge=0.0, le=100.0)
    positive_observations: List[str] = Field(default_factory=list)
    negative_observations: List[str] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list)


class ResumeQualityReportResponse(BaseModel):
    """Transparent multi-metric evaluation of resume quality and structure."""
    resume_id: str
    version_id: str
    overall_quality_score: float = Field(ge=0.0, le=100.0)
    quality_band: str = Field(description="STRONG, MODERATE, NEEDS_IMPROVEMENT")
    section_scores: Dict[str, float] = Field(default_factory=dict)
    dimension_evaluations: Dict[str, QualityDimensionEvaluation] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)
    improvement_priorities: List[str] = Field(default_factory=list)
    methodology: str


class ResumeJobMatchRequest(BaseModel):
    """Request to match a resume against a specific job description."""
    target_job_title: str = Field(min_length=2, max_length=150)
    target_job_description: str = Field(min_length=10, max_length=30000)


class ResumeJobMatchResponse(BaseModel):
    """Detailed evidence-backed comparison of resume against target job description."""
    match_id: Optional[str] = None
    resume_id: str
    version_id: str
    target_job_title: str
    overall_match_score: float = Field(ge=0.0, le=100.0)
    keyword_coverage_score: float = Field(ge=0.0, le=1.0)
    required_skills_match: Dict[str, Any] = Field(
        description="Matched and missing hard-requirement skills"
    )
    preferred_skills_match: Dict[str, Any] = Field(
        description="Matched and missing preferred skills"
    )
    experience_level_match: Dict[str, Any] = Field(
        description="Detected experience years vs required experience"
    )
    project_theme_alignments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Portfolio/project bullet matches to JD themes via token overlap"
    )
    unverified_matches: List[str] = Field(
        default_factory=list,
        description="Skills mentioned in JD that are only inferred or partially supported"
    )
    job_specific_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ResumeVersionDiffResponse(BaseModel):
    """Semantic and textual difference between two resume versions."""
    resume_id: str
    version_id_1: str
    version_id_2: str
    version_label_1: str
    version_label_2: str
    character_count_diff: int
    word_count_diff: int
    added_skills: List[str] = Field(default_factory=list)
    removed_skills: List[str] = Field(default_factory=list)
    shared_skills: List[str] = Field(default_factory=list)
    section_changes: Dict[str, str] = Field(default_factory=dict)
    quality_score_diff: Optional[Dict[str, Any]] = None
    compared_at: datetime = Field(default_factory=datetime.utcnow)


class ResumeReviewFieldUpdate(BaseModel):
    """Payload to review or correct a specific extracted field."""
    field_id: str
    action: ReviewAction
    corrected_value: Optional[Any] = None
    notes: Optional[str] = None


class ResumeReviewResponse(BaseModel):
    """Review workbench state showing approvals, rejections, and profile conflicts."""
    resume_id: str
    version_id: str
    review_status: ReviewStatus
    is_synced_to_profile: bool
    synced_at: Optional[datetime] = None
    pending_fields_count: int
    confirmed_fields_count: int
    rejected_fields_count: int
    conflicts_with_profile: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of fields where extracted data differs from existing candidate profile"
    )
    evidence_items: List[EvidenceDTO] = Field(default_factory=list)


class ResumeConfirmSyncRequest(BaseModel):
    """Request to synchronize confirmed extracted fields into the canonical candidate profile."""
    approved_field_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific field_ids to sync. If omitted, all confirmed/edited fields are synced."
    )
    overwrite_conflicts: bool = Field(
        default=False,
        description="Whether to overwrite existing user-provided fields if conflicts exist. Requires explicit candidate consent."
    )


class ResumeConfirmSyncResponse(BaseModel):
    """Result of synchronizing approved resume fields to candidate profile."""
    synced: bool
    fields_synced_count: int
    conflicts_overwritten_count: int
    synced_at: datetime
    message: str


class ATSAnalysisRequest(BaseModel):
    """Request to score ATS keyword coverage and bullet strength against a target job."""
    target_job_title: str = Field(min_length=2, max_length=150)
    target_job_description: str = Field(min_length=10, max_length=25000)


class ATSAnalysisResponse(BaseModel):
    """Transparent ATS keyword coverage, bullet impact, and non-fabricating advice."""
    analysis_id: str
    resume_id: str
    version_id: str
    target_job_title: str
    coverage_score: float = Field(ge=0.0, le=1.0, description="Fraction of top JD keywords found in resume text")
    matched_keywords: List[str]
    missing_keywords: List[str]
    bullet_impact_score: float = Field(ge=0.0, le=100.0, description="Percentage of quantified/impactful bullets")
    bullet_impact_analysis: Dict[str, Any]
    actionable_suggestions: List[Dict[str, Any]] = Field(
        description="Suggestions strictly grounded in document evidence; never fabricates facts"
    )
    formatting_observations: List[str]
    methodology_and_limitations: str
    created_at: datetime
    # Phase 3 detailed ATS scoring & requirement segregation fields
    total_relevant_keywords: int = 0
    keyword_coverage_percentage: float = 0.0
    required_keywords: List[str] = Field(default_factory=list)
    required_matched: List[str] = Field(default_factory=list)
    required_missing: List[str] = Field(default_factory=list)
    preferred_keywords: List[str] = Field(default_factory=list)
    preferred_matched: List[str] = Field(default_factory=list)
    preferred_missing: List[str] = Field(default_factory=list)
    keyword_details: Optional[Dict[str, Any]] = None
    keyword_rankings: List[Dict[str, Any]] = Field(default_factory=list)


class SuggestedJobResponse(BaseModel):
    """Job suggestion scored against candidate's verified profile & resume evidence."""
    job_id: str
    title: str
    company_name: str
    location: str
    is_remote: bool
    employment_type: str
    salary_display: Optional[str] = None
    application_url: str
    match_score: float = Field(ge=0.0, le=100.0)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    description_snippet: str
    full_description: str
    verification_status: str = "OPEN_CONFIRMED"
    freshness_state: str = "FRESH"
    listing_age_days: float = 0.0
    last_verified_display: str = "Verified active today"



