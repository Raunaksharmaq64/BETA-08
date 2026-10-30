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
    skills: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_items: List[EvidenceDTO] = Field(default_factory=list)
    parsed_at: Optional[datetime] = None


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

