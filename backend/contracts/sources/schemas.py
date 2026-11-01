"""
RIGHT FIT — Job Source Framework Contracts & Data Schemas
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class SourceType(StrEnum):
    """Categorization of opportunity data source."""
    ATS_JOB_BOARD = "ATS_JOB_BOARD"
    OFFICIAL_API = "OFFICIAL_API"
    PERMITTED_FEED = "PERMITTED_FEED"


class IntegrationMethod(StrEnum):
    """Ingestion mechanism."""
    REST_API = "REST_API"
    PULL_FEED = "PULL_FEED"
    WEBHOOK = "WEBHOOK"


class AuthType(StrEnum):
    """Authentication requirement for the source."""
    NONE_PUBLIC = "NONE_PUBLIC"
    API_KEY = "API_KEY"
    BEARER_TOKEN = "BEARER_TOKEN"
    OAUTH2 = "OAUTH2"


class PolicyStatus(StrEnum):
    """Governance lifecycle status for sources."""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    BLOCKED = "BLOCKED"
    RETIRED = "RETIRED"


class CircuitBreakerState(StrEnum):
    """3-State Circuit Breaker operational condition."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class RunStatus(StrEnum):
    """Ingestion run execution outcome."""
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_FAILURE = "PARTIAL_FAILURE"
    FAILED = "FAILED"


class TriggerType(StrEnum):
    """Origin of the ingestion execution."""
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    SYSTEM = "SYSTEM"


class WorkplaceType(StrEnum):
    """Workplace location mode."""
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    UNKNOWN = "UNKNOWN"


class EmploymentType(StrEnum):
    """Employment arrangement classification."""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    OTHER = "OTHER"


class NormalizationStatus(StrEnum):
    """Status of raw payload normalization."""
    RAW = "RAW"
    NORMALIZED = "NORMALIZED"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"


# ------------------------------------------------------------------------------
# Request Schemas
# ------------------------------------------------------------------------------

class SourceCreateRequest(BaseModel):
    """Payload to register a new job source."""
    model_config = ConfigDict(extra="forbid")

    source_key: str = Field(..., min_length=2, max_length=100, description="Unique slug identifying source (e.g. 'greenhouse-stripe')")
    display_name: str = Field(..., min_length=2, max_length=150, description="Human readable name")
    source_type: SourceType = Field(default=SourceType.ATS_JOB_BOARD, description="Source classification")
    provider: str = Field(..., min_length=2, max_length=50, description="Provider/adapter name ('greenhouse', 'ashby', 'synthetic')")
    base_url: str = Field(..., description="Target board or API base URL")
    integration_method: IntegrationMethod = Field(default=IntegrationMethod.REST_API)
    auth_type: AuthType = Field(default=AuthType.NONE_PUBLIC)
    credential_reference: Optional[str] = Field(default=None, max_length=255, description="Secret manager or vault key reference")
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1200, description="Allowed requests per minute")
    timeout_seconds: float = Field(default=30.0, ge=1.0, le=120.0, description="HTTP request timeout in seconds")
    retry_max_attempts: int = Field(default=3, ge=0, le=10, description="Max retry attempts on transient errors")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Operational or compliance notes")

    @field_validator("source_key")
    @classmethod
    def validate_source_key_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not all(c.isalnum() or c in ("-", "_") for c in clean):
            raise ValueError("source_key may only contain alphanumeric characters, hyphens, and underscores")
        return clean


class SourceUpdateRequest(BaseModel):
    """Payload to update an existing job source configuration."""
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    base_url: Optional[str] = Field(default=None)
    enabled: Optional[bool] = Field(default=None)
    rate_limit_per_minute: Optional[int] = Field(default=None, ge=1, le=1200)
    timeout_seconds: Optional[float] = Field(default=None, ge=1.0, le=120.0)
    retry_max_attempts: Optional[int] = Field(default=None, ge=0, le=10)
    credential_reference: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=1000)


class SourcePolicyUpdateRequest(BaseModel):
    """Payload to update the governance policy status of a source."""
    model_config = ConfigDict(extra="forbid")

    policy_status: PolicyStatus = Field(..., description="Target governance status")
    review_notes: str = Field(..., min_length=3, max_length=1000, description="Audit rationale for decision")


class IngestionTriggerRequest(BaseModel):
    """Payload to trigger an ingestion run on demand."""
    model_config = ConfigDict(extra="forbid")

    max_records: int = Field(default=50, ge=1, le=500, description="Maximum listings to ingest in this run")
    force: bool = Field(default=False, description="Bypass cooldown if circuit is in HALF_OPEN")


# ------------------------------------------------------------------------------
# Response Schemas
# ------------------------------------------------------------------------------

class SourceResponse(BaseModel):
    """Public representation of a registered Job Source."""
    id: str
    source_key: str
    display_name: str
    source_type: SourceType
    provider: str
    base_url: str
    integration_method: IntegrationMethod
    auth_type: AuthType
    credential_reference: Optional[str] = None
    enabled: bool
    policy_status: PolicyStatus
    policy_decision_json: Dict[str, Any] = Field(default_factory=dict)
    rate_limit_per_minute: int
    timeout_seconds: float
    retry_max_attempts: int
    circuit_breaker_state: CircuitBreakerState
    consecutive_failures: int
    last_failure_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SourceObservationResponse(BaseModel):
    """Provenance and raw signal observation record."""
    id: str
    source_id: str
    external_job_id: str
    listing_url: str
    observed_at: datetime
    source_published_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    payload_hash_sha256: str
    normalization_status: NormalizationStatus
    error_message: Optional[str] = None
    first_seen_at: datetime
    last_seen_at: datetime


class CanonicalOpportunityResponse(BaseModel):
    """Canonical, normalized career opportunity."""
    id: str
    source_id: str
    external_job_id: str
    dedup_key_sha256: str
    title: str
    company_name: str
    description_clean: str
    employment_type: EmploymentType
    workplace_type: WorkplaceType
    department: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_remote: bool
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = None
    salary_period: Optional[str] = None
    is_salary_estimated: bool
    required_skills: List[str] = Field(default_factory=list)
    application_url: str
    source_published_at: Optional[datetime] = None
    first_seen_at: datetime
    last_seen_at: datetime
    is_active: bool
    verification_status: str = "UNVERIFIED"
    freshness_state: str = "UNKNOWN"
    is_suppressed: bool = False
    provenance: Dict[str, Any] = Field(default_factory=dict)


class SourceRunLogResponse(BaseModel):
    """Execution log and metrics for a source ingestion run."""
    id: str
    source_id: str
    trigger_type: TriggerType
    status: RunStatus
    records_fetched: int
    records_normalized: int
    records_inserted: int
    records_updated: int
    duplicates_skipped: int
    error_category: Optional[str] = None
    safe_error_summary: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class IngestionTriggerResponse(BaseModel):
    """Result of an ingestion run execution."""
    run_id: str
    source_id: str
    source_key: str
    status: RunStatus
    records_fetched: int
    records_inserted: int
    records_updated: int
    duplicates_skipped: int
    duration_seconds: float
    circuit_state: CircuitBreakerState
    message: str
