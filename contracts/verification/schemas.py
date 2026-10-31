"""
RIGHT FIT — Verification, Deduplication, Freshness & Quality Intelligence Contracts
Version: 1.0.0
Phase: 6 — Verification, Deduplication, Freshness & Data Quality Intelligence
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(StrEnum):
    """Formal verification state of an opportunity."""
    UNVERIFIED = "UNVERIFIED"
    OPEN_CONFIRMED = "OPEN_CONFIRMED"
    CLOSED_CONFIRMED = "CLOSED_CONFIRMED"
    EXPIRED_CONFIRMED = "EXPIRED_CONFIRMED"
    UNAVAILABLE = "UNAVAILABLE"
    CHECK_FAILED = "CHECK_FAILED"
    AMBIGUOUS = "AMBIGUOUS"
    STALE = "STALE"


class FreshnessState(StrEnum):
    """Categorization of listing freshness based on observation and verification timestamps."""
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    CHECK_OVERDUE = "CHECK_OVERDUE"
    LINK_UNAVAILABLE = "LINK_UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class FeedbackType(StrEnum):
    """User-reported issue or moderation concern with a listing."""
    BROKEN_LINK = "BROKEN_LINK"
    ALREADY_CLOSED = "ALREADY_CLOSED"
    INCORRECT_DETAILS = "INCORRECT_DETAILS"
    DUPLICATE_LISTING = "DUPLICATE_LISTING"
    SUSPICIOUS_JOB = "SUSPICIOUS_JOB"
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    MISLEADING_DESCRIPTION = "MISLEADING_DESCRIPTION"
    INCORRECT_LOCATION = "INCORRECT_LOCATION"
    INCORRECT_STATUS = "INCORRECT_STATUS"
    COMPANY_IMPERSONATION = "COMPANY_IMPERSONATION"
    OTHER = "OTHER"


class FeedbackStatus(StrEnum):
    """Processing lifecycle of user listing feedback."""
    RECEIVED = "RECEIVED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class MatchTier(StrEnum):
    """Tiered confidence for deduplication matching."""
    TIER_1_EXACT = "TIER_1_EXACT"
    TIER_2_STRONG = "TIER_2_STRONG"
    TIER_3_PROBABLE = "TIER_3_PROBABLE"
    TIER_4_DISTINCT = "TIER_4_DISTINCT"


class MergeStatus(StrEnum):
    """Status of deduplication candidate pairing or decision."""
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    UNMERGED = "UNMERGED"


# ------------------------------------------------------------------------------
# Request Schemas
# ------------------------------------------------------------------------------

class VerificationTriggerRequest(BaseModel):
    """Payload to trigger an on-demand verification check."""
    model_config = ConfigDict(extra="forbid")

    force: bool = Field(default=False, description="Bypass cooldown or cache")
    check_method: str = Field(default="DIRECT_API", description="Verification method: DIRECT_API, URL_PROBE, BOARD_FEED")


class UserFeedbackCreateRequest(BaseModel):
    """Payload submitted by a candidate/user reporting listing inaccuracy."""
    model_config = ConfigDict(extra="forbid")

    feedback_type: FeedbackType = Field(..., description="Category of reported issue")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Context or explanation")


class MergeActionRequest(BaseModel):
    """Payload to merge multiple duplicate opportunities into a primary canonical opportunity."""
    model_config = ConfigDict(extra="forbid")

    primary_id: str = Field(..., description="UUID of canonical opportunity to keep as primary")
    duplicate_ids: List[str] = Field(..., min_length=1, description="UUIDs of duplicate records to merge into primary")
    reason: str = Field(..., min_length=5, max_length=500, description="Auditable justification for merge")


class UnmergeActionRequest(BaseModel):
    """Payload to reverse a previous merge decision."""
    model_config = ConfigDict(extra="forbid")

    decision_id: str = Field(..., description="UUID of merge decision to reverse")
    reason: str = Field(..., min_length=5, max_length=500, description="Auditable justification for unmerge")


# ------------------------------------------------------------------------------
# Response Schemas
# ------------------------------------------------------------------------------

class VerificationEvidenceResponse(BaseModel):
    """Public representation of an immutable verification evidence event."""
    id: str
    opportunity_id: str
    source_id: str
    check_id: str
    check_timestamp: datetime
    check_method: str
    check_outcome: str
    http_status: Optional[int] = None
    provider_status: Optional[str] = None
    evidence_category: str
    evidence_reference: Optional[str] = None
    safe_response_metadata: Dict[str, Any] = Field(default_factory=dict)
    verification_rule_version: str
    confidence_category: str
    error_category: Optional[str] = None
    next_eligible_check_at: Optional[datetime] = None


class OpportunityVerificationDetailResponse(BaseModel):
    """Comprehensive verification timeline and independent timestamps for an opportunity."""
    opportunity_id: str
    verification_status: VerificationStatus
    freshness_state: FreshnessState
    user_friendly_status: str
    user_explanation: str
    published_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    first_seen_at: datetime
    last_seen_at: datetime
    last_checked_at: Optional[datetime] = None
    last_successful_check_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    status_changed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_suppressed: bool = False
    evidence_history: List[VerificationEvidenceResponse] = Field(default_factory=list)


class UserFeedbackResponse(BaseModel):
    """Representation of user listing feedback."""
    id: str
    opportunity_id: str
    user_id: Optional[str] = None
    feedback_type: FeedbackType
    notes: Optional[str] = None
    status: FeedbackStatus
    created_at: datetime


class DuplicateCandidateResponse(BaseModel):
    """Candidate duplicate pairing for administrative review."""
    id: str
    primary_opportunity_id: str
    primary_title: str
    primary_company: str
    primary_location: Optional[str] = None
    duplicate_opportunity_id: str
    duplicate_title: str
    duplicate_company: str
    duplicate_location: Optional[str] = None
    match_tier: MatchTier
    match_method: str
    confidence_score: float
    match_evidence: Dict[str, Any] = Field(default_factory=dict)
    status: MergeStatus
    created_at: datetime


class SourceMappingResponse(BaseModel):
    """Auditable mapping connecting source records to canonical opportunities."""
    id: str
    canonical_opportunity_id: str
    source_id: str
    source_key: str
    external_job_id: str
    original_url: str
    first_seen_at: datetime
    last_seen_at: datetime
    mapping_status: str
    match_tier: MatchTier
    match_method: str
    match_evidence: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float
    merge_decision_id: Optional[str] = None


class QualityMetricsResponse(BaseModel):
    """Aggregated operational metrics for the Data Quality Dashboard."""
    total_opportunities: int
    fresh_opportunities: int
    aging_opportunities: int
    stale_opportunities: int
    confirmed_open_count: int
    confirmed_closed_count: int
    unavailable_count: int
    ambiguous_count: int
    freshness_rate: float
    verification_coverage: float
    confirmed_open_rate: float
    link_unavailable_rate: float
    duplicate_candidates_count: int
    confirmed_merges_count: int
    user_feedback_count: int
    source_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime

