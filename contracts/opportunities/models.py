"""
RIGHT FIT — Canonical Opportunity Envelope & Typed Payloads Contract
Version: 1.0.0
Status: ACTIVE CONTRACT

Defines the normalized data representation for all career and business opportunities
ingested from Core ATS adapters, LeadHunter, and Startup Intelligence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class OpportunityType(StrEnum):
    """Supported broad opportunity classifications."""

    JOB = "JOB"
    FREELANCE = "FREELANCE"
    STARTUP_PROBLEM = "STARTUP_PROBLEM"


class RemoteType(StrEnum):
    """Workplace location mode."""

    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    UNKNOWN = "UNKNOWN"


class VerificationStatus(StrEnum):
    """Legitimacy and availability verification status."""

    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    DEPRECATED = "DEPRECATED"


class OrganizationInfo(BaseModel):
    """Entity offering or associated with the opportunity."""

    name: str = Field(..., description="Organization or business name.")
    website: Optional[str] = Field(default=None, description="Primary domain or website URL if known.")


class LocationInfo(BaseModel):
    """Geographic and remote distribution details."""

    city: Optional[str] = Field(default=None, description="City name.")
    state: Optional[str] = Field(default=None, description="State, province, or region.")
    country: Optional[str] = Field(default=None, description="Country name or ISO code.")
    remote_type: RemoteType = Field(default=RemoteType.UNKNOWN, description="Work location arrangement.")


class SourceProvenance(BaseModel):
    """Origin tracking and traceability metadata."""

    provider: str = Field(..., description="Source name (e.g., 'greenhouse', 'ashby', 'google_maps', 'reddit').")
    original_url: str = Field(..., description="Direct link or permalink to the original posting or post.")
    external_id: Optional[str] = Field(default=None, description="Source provider's native identifier.")
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO 8601 UTC timestamp when this signal was retrieved."
    )


class StatusInfo(BaseModel):
    """Current opportunity validation lifecycle."""

    value: VerificationStatus = Field(default=VerificationStatus.UNVERIFIED, description="Status code.")
    verified_at: Optional[datetime] = Field(default=None, description="Timestamp of most recent verification.")


class EvidenceItem(BaseModel):
    """Auditable excerpt or signal evidence."""

    source_url: str = Field(..., description="Permalink to original evidence post or listing.")
    excerpt: str = Field(..., description="Relevant text excerpt showing need or requirement.")
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when evidence was recorded."
    )


# ------------------------------------------------------------------------------
# Typed Payloads
# ------------------------------------------------------------------------------

class JobOpportunityPayload(BaseModel):
    """Typed details specific to full-time/contract ATS employment opportunities."""

    salary_min: Optional[float] = Field(default=None, ge=0, description="Minimum compensation in specified currency.")
    salary_max: Optional[float] = Field(default=None, ge=0, description="Maximum compensation in specified currency.")
    salary_currency: Optional[str] = Field(default="USD", max_length=3, description="ISO 4217 currency code.")
    fit_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Deterministic match score [0.0 to 1.0].")
    matched_skills: List[str] = Field(default_factory=list, description="Candidate skills found in job requirements.")
    missing_skills: List[str] = Field(default_factory=list, description="Required job skills missing from candidate profile.")
    ats_provider: str = Field(..., description="Adapter name (e.g. 'greenhouse', 'lever', 'ashby').")
    application_url: str = Field(..., description="Direct URL to official application submission page.")


class FreelanceOpportunityPayload(BaseModel):
    """Typed details specific to local business and website audit opportunities (LeadHunter)."""

    business_category: str = Field(..., description="Business category (e.g. 'Dental Clinic', 'Restaurant').")
    website_url: Optional[str] = Field(default=None, description="Target business website if existing.")
    is_broken_website: bool = Field(default=False, description="Whether website failed DNS, SSL, or HTTP checks.")
    audit_status: str = Field(default="COMPLETED", description="Status of the automated technical audit.")
    detected_issues: List[str] = Field(default_factory=list, description="Technical pain points (e.g. 'Missing SSL', '404 Bad Gateway').")
    suggested_pitch: Optional[str] = Field(default=None, description="AI-generated pitch or proposal text.")
    contact_email: Optional[str] = Field(default=None, description="Discovered contact email for decision maker.")
    contact_phone: Optional[str] = Field(default=None, description="Discovered business phone number.")
    fit_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Personalized candidate match score [0.0 to 1.0].")
    matched_skills: List[str] = Field(default_factory=list, description="Candidate skills matching freelance requirements.")
    missing_skills: List[str] = Field(default_factory=list, description="Skills missing for this freelance project.")


class StartupProblemPayload(BaseModel):
    """Typed details specific to startup technical issues and founder needs (Startup Intelligence)."""

    target_startup: str = Field(..., description="Name of the startup or founder username.")
    pain_point_summary: str = Field(..., description="Concise statement of the technical bottleneck.")
    problem_category: str = Field(..., description="Category (e.g. 'Performance', 'Database', 'SEO', 'Mobile', 'AI').")
    community_source: str = Field(..., description="Source community (e.g. 'Reddit r/saas', 'GitHub Issues', 'Hacker News').")
    author: Optional[str] = Field(default=None, description="Author or founder username.")
    tech_stack_detected: List[str] = Field(default_factory=list, description="Technologies detected (e.g. ['React', 'Next.js', 'PostgreSQL']).")
    urgency_score: int = Field(default=5, ge=1, le=10, description="Evaluated hiring or problem urgency (1-10).")
    recommended_solution: Optional[str] = Field(default=None, description="Proposed technical approach for outreach.")
    fit_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Personalized candidate match score [0.0 to 1.0].")
    matched_skills: List[str] = Field(default_factory=list, description="Candidate skills matching startup pain point.")
    missing_skills: List[str] = Field(default_factory=list, description="Skills or tools missing.")


# ------------------------------------------------------------------------------
# Canonical Envelope
# ------------------------------------------------------------------------------

class OpportunityEnvelope(BaseModel):
    """Canonical versioned envelope wrapping all opportunity types."""

    schema_version: str = Field(default="1.0", description="Envelope schema version.")
    opportunity_id: str = Field(..., description="Unique UUID identifying this normalized opportunity.")
    opportunity_type: OpportunityType = Field(..., description="Broad type of opportunity.")
    title: str = Field(..., min_length=2, description="Concise opportunity headline.")
    description: str = Field(..., description="Full text description or excerpt of the opportunity.")
    organization: OrganizationInfo = Field(..., description="Associated company or client details.")
    location: LocationInfo = Field(..., description="Geographic location and remote eligibility.")
    source: SourceProvenance = Field(..., description="Provenance and retrieval metadata.")
    status: StatusInfo = Field(default_factory=StatusInfo, description="Verification and freshness status.")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting proof and excerpts.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary extension attributes.")
    payload: Union[JobOpportunityPayload, FreelanceOpportunityPayload, StartupProblemPayload] = Field(
        ...,
        description="Type-specific details corresponding to opportunity_type."
    )

    @model_validator(mode="after")
    def validate_payload_matches_type(self) -> OpportunityEnvelope:
        """Enforces that opportunity_type strictly corresponds to payload model."""
        if self.opportunity_type == OpportunityType.JOB and not isinstance(self.payload, JobOpportunityPayload):
            raise ValueError(f"Payload must be of type JobOpportunityPayload when opportunity_type is {OpportunityType.JOB}")
        if self.opportunity_type == OpportunityType.FREELANCE and not isinstance(self.payload, FreelanceOpportunityPayload):
            raise ValueError(f"Payload must be of type FreelanceOpportunityPayload when opportunity_type is {OpportunityType.FREELANCE}")
        if self.opportunity_type == OpportunityType.STARTUP_PROBLEM and not isinstance(self.payload, StartupProblemPayload):
            raise ValueError(f"Payload must be of type StartupProblemPayload when opportunity_type is {OpportunityType.STARTUP_PROBLEM}")
        return self

