"""
RIGHT FIT — Core-to-Startup Hunter Service API Contract
Version: 1.0.0
Status: ACTIVE CONTRACT

Governs the versioned HTTP REST interface between Core Career Engine
and the independent Startup Intelligence satellite service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StartupScanStatus(StrEnum):
    """Lifecycle states of an asynchronous Startup Intelligence scan."""

    QUEUED = "QUEUED"
    SCANNING = "SCANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CommunitySource(StrEnum):
    """Permitted developer community channels."""

    REDDIT = "reddit"
    GITHUB = "github"
    HACKER_NEWS = "hackernews"
    PRODUCT_HUNT = "producthunt"
    DEV_TO = "devto"
    ALL = "all"


class StartupDiscoveryRequest(BaseModel):
    """Payload sent by Core Backend to trigger a startup pain-point scan."""

    sources: List[CommunitySource] = Field(default_factory=lambda: [CommunitySource.ALL], description="Communities to crawl.")
    keywords: List[str] = Field(default_factory=list, description="Target keywords (e.g. ['postgres', 'slow', 'react']).")
    categories: List[str] = Field(default_factory=list, description="Problem categories (e.g. ['Performance', 'Database', 'Mobile']).")
    max_signals: int = Field(default=20, ge=1, le=100, description="Maximum raw signals to parse and classify.")


class StartupProblemSummary(BaseModel):
    """Normalized startup technical bottleneck candidate."""

    signal_id: str = Field(..., description="Unique identifier for the detected problem signal.")
    startup_name: str = Field(..., description="Target startup name or author username.")
    category: str = Field(..., description="Problem category (e.g., 'Performance', 'SEO', 'Mobile', 'Database').")
    pain_point: str = Field(..., description="Detailed explanation of the technical bottleneck.")
    detected_signal: str = Field(..., description="Summary of the raw signal (e.g. hiring post, founder complaint).")
    community_source: str = Field(..., description="Originating community channel (e.g. 'Reddit r/saas').")
    source_url: str = Field(..., description="Permalink to original discussion or issue.")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies flagged in context.")
    urgency_score: int = Field(default=5, ge=1, le=10, description="Hiring or problem urgency score (1-10).")
    suggested_pitch: Optional[str] = Field(default=None, description="AI-generated outreach proposal.")
    published_at: Optional[datetime] = Field(default=None, description="Original post publication timestamp.")


class StartupDiscoveryStatus(BaseModel):
    """Status response for an ongoing or completed startup pain-point scan."""

    discovery_id: str = Field(..., description="Tracking UUID for the scan job.")
    status: StartupScanStatus = Field(..., description="Current scan lifecycle state.")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="Completion percentage (0-100).")
    total_signals_analyzed: int = Field(default=0, ge=0, description="Total raw posts parsed.")
    total_opportunities_found: int = Field(default=0, ge=0, description="Total actionable leads produced.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when scan was scheduled."
    )
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when scan completed.")


class StartupDiscoveryResult(BaseModel):
    """Collection response containing startup opportunities discovered by a scan."""

    discovery_id: str = Field(..., description="Tracking UUID for the scan job.")
    problems: List[StartupProblemSummary] = Field(default_factory=list, description="Actionable technical pain points.")
    total_count: int = Field(..., ge=0, description="Total count of items returned.")


class StartupProblemDetailResponse(BaseModel):
    """Comprehensive detail for a single startup problem opportunity."""

    problem: StartupProblemSummary = Field(..., description="Core problem details.")
    raw_excerpt: str = Field(..., description="Verbatim text of the original community post or GitHub issue.")
    founder_contact_info: Dict[str, Any] = Field(default_factory=dict, description="Enriched founder contacts (Twitter/X, LinkedIn, email).")


class ValidationState(StrEnum):
    """Evidence corroboration and validation state for startup problem signals."""
    OBSERVED_PROBLEM = "OBSERVED_PROBLEM"
    REPEATED_OBSERVATIONS = "REPEATED_OBSERVATIONS"
    INDEPENDENTLY_CORROBORATED = "INDEPENDENTLY_CORROBORATED"
    CUSTOMER_VALIDATION_REQUIRED = "CUSTOMER_VALIDATION_REQUIRED"


class StartupOpportunityWorkspaceUpdate(BaseModel):
    target_persona: Optional[str] = None
    hypotheses: Optional[List[str]] = None
    competitor_notes: Optional[str] = None
    interview_questions: Optional[List[str]] = None
    validation_checklist: Optional[List[Dict[str, Any]]] = None
    solution_architecture: Optional[str] = None
    candidate_notes: Optional[str] = None


class StartupOpportunityWorkspaceResponse(BaseModel):
    id: str
    opportunity_id: str
    user_id: str
    target_persona: Optional[str] = None
    hypotheses: List[str] = Field(default_factory=list)
    competitor_notes: Optional[str] = None
    interview_questions: List[str] = Field(default_factory=list)
    validation_checklist: List[Dict[str, Any]] = Field(default_factory=list)
    solution_architecture: Optional[str] = None
    candidate_notes: Optional[str] = None
    validation_state: ValidationState = ValidationState.OBSERVED_PROBLEM
    created_at: datetime
    updated_at: datetime


