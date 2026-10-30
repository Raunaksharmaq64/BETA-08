"""
RIGHT FIT — Privacy, Consent, Export & Deletion Schemas
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProfileVisibility(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    ANONYMIZED = "ANONYMIZED"


class ConsentPurpose(StrEnum):
    DATA_PROCESSING = "DATA_PROCESSING"
    AI_CAREER_MATCHING = "AI_CAREER_MATCHING"
    THIRD_PARTY_OUTREACH = "THIRD_PARTY_OUTREACH"
    MARKETING_ALERTS = "MARKETING_ALERTS"
    ANALYTICS_RESEARCH = "ANALYTICS_RESEARCH"


class DataExportStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DeletionStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ------------------------------------------------------------------------------
# Privacy Settings
# ------------------------------------------------------------------------------

class PrivacySettingsUpdate(BaseModel):
    profile_visibility: ProfileVisibility = Field(default=ProfileVisibility.PUBLIC)
    opportunity_alerts: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    ai_processing_enabled: bool = Field(default=True)
    data_usage_research: bool = Field(default=False)


class PrivacySettingsResponse(PrivacySettingsUpdate):
    id: str
    user_id: str
    updated_at: datetime


# ------------------------------------------------------------------------------
# Consents
# ------------------------------------------------------------------------------

class ConsentGrantRequest(BaseModel):
    purpose: ConsentPurpose
    policy_version: str = Field(default="1.0")


class ConsentRecordResponse(BaseModel):
    id: str
    user_id: str
    purpose: str
    granted: bool
    policy_version: str
    created_at: datetime
    withdrawn_at: Optional[datetime] = None


# ------------------------------------------------------------------------------
# Data Export
# ------------------------------------------------------------------------------

class DataExportResponse(BaseModel):
    export_id: str
    status: DataExportStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    download_url: Optional[str] = None


class DataExportDownloadResponse(BaseModel):
    export_id: str
    user_id: str
    generated_at: datetime
    metadata: Dict[str, Any]
    data: Dict[str, Any]


# ------------------------------------------------------------------------------
# Account Deletion
# ------------------------------------------------------------------------------

class AccountDeletionRequest(BaseModel):
    confirmation: str = Field(..., description="Must explicitly match 'DELETE MY ACCOUNT'")
    reason: Optional[str] = Field(default=None, max_length=500)


class AccountDeletionResponse(BaseModel):
    deletion_id: str
    status: DeletionStatus
    scheduled_deletion_at: datetime
    service_status: Dict[str, str] = Field(
        default_factory=dict,
        description="Tracks deletion acknowledgment across independent services (leadhunter, startup_intel)."
    )
    message: str
