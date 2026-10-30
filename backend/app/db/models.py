"""
RIGHT FIT Core — SQLAlchemy Database Models
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    """Returns current datetime in UTC timezone."""
    return datetime.now(timezone.utc)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensures datetime is timezone-aware in UTC (compatible with SQLite naive datetimes)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_expired(expires_at: Optional[datetime]) -> bool:
    """Safely checks if an expiration timestamp has passed, handling naive SQLite datetimes."""
    if expires_at is None:
        return False
    target = ensure_utc(expires_at)
    return target < datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generates a UUID4 string."""
    return str(uuid.uuid4())


class User(Base):
    """Core platform user account entity."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="CANDIDATE", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    profile: Mapped[Optional["CandidateProfile"]] = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshTokenRecord"]] = relationship("RefreshTokenRecord", back_populates="user", cascade="all, delete-orphan")
    verification_tokens: Mapped[List["EmailVerificationTokenRecord"]] = relationship("EmailVerificationTokenRecord", back_populates="user", cascade="all, delete-orphan")
    reset_tokens: Mapped[List["PasswordResetTokenRecord"]] = relationship("PasswordResetTokenRecord", back_populates="user", cascade="all, delete-orphan")
    privacy_settings: Mapped[Optional["PrivacySettingsRecord"]] = relationship("PrivacySettingsRecord", back_populates="user", uselist=False, cascade="all, delete-orphan")
    consents: Mapped[List["ConsentRecord"]] = relationship("ConsentRecord", back_populates="user", cascade="all, delete-orphan")
    export_requests: Mapped[List["DataExportRequestRecord"]] = relationship("DataExportRequestRecord", back_populates="user", cascade="all, delete-orphan")
    deletion_requests: Mapped[List["AccountDeletionRequestRecord"]] = relationship("AccountDeletionRequestRecord", back_populates="user", cascade="all, delete-orphan")
    resumes: Mapped[List["ResumeRecord"]] = relationship("ResumeRecord", back_populates="user", cascade="all, delete-orphan")


class RefreshTokenRecord(Base):
    """Stored hash of rotating refresh tokens for session management and reuse detection."""
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    family_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class EmailVerificationTokenRecord(Base):
    """Single-use email verification tokens."""
    __tablename__ = "email_verification_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="verification_tokens")


class PasswordResetTokenRecord(Base):
    """Single-use password recovery tokens."""
    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reset_tokens")


class CandidateProfile(Base):
    """Central candidate profile entity owned by Core."""
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="profile")
    education: Mapped[List["EducationRecord"]] = relationship("EducationRecord", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    experience: Mapped[List["ExperienceRecord"]] = relationship("ExperienceRecord", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    skills: Mapped[List["CandidateSkillRecord"]] = relationship("CandidateSkillRecord", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    preferences: Mapped[Optional["CandidatePreferenceRecord"]] = relationship("CandidatePreferenceRecord", back_populates="profile", uselist=False, cascade="all, delete-orphan", lazy="selectin")


class EducationRecord(Base):
    __tablename__ = "educations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    institution: Mapped[str] = mapped_column(String(150), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provenance: Mapped[str] = mapped_column(String(30), default="USER_PROVIDED", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="education")


class ExperienceRecord(Base):
    __tablename__ = "experiences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    company: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time", nullable=False)
    start_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    provenance: Mapped[str] = mapped_column(String(30), default="USER_PROVIDED", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="experience")


class CandidateSkillRecord(Base):
    __tablename__ = "candidate_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_name: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Technical", nullable=False)
    proficiency: Mapped[str] = mapped_column(String(30), default="Intermediate", nullable=False)
    years_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    provenance: Mapped[str] = mapped_column(String(30), default="USER_PROVIDED", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="skills")


class CandidatePreferenceRecord(Base):
    __tablename__ = "candidate_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    preferred_roles_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_industries_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_locations_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    remote_preference: Mapped[str] = mapped_column(String(20), default="ANY", nullable=False)
    min_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    employment_types_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    job_notification_frequency: Mapped[str] = mapped_column(String(20), default="DAILY", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="preferences")


class PrivacySettingsRecord(Base):
    __tablename__ = "privacy_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    profile_visibility: Mapped[str] = mapped_column(String(20), default="PUBLIC", nullable=False)
    opportunity_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_processing_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_usage_research: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="privacy_settings")


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="consents")


class DataExportRequestRecord(Base):
    __tablename__ = "data_export_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    export_data_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="export_requests")


class AccountDeletionRequestRecord(Base):
    __tablename__ = "account_deletion_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    reasons: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    service_status_json: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
    scheduled_deletion_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="deletion_requests")


class SecurityAuditEventRecord(Base):
    __tablename__ = "security_audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # SUCCESS, FAILURE
    details_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# =============================================================================
# Phase 4: Resume Intelligence & Reviewed Candidate Evidence Models
# =============================================================================

class ResumeRecord(Base):
    """Candidate resume container grouping multiple versions."""
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), default="My Resume", nullable=False)
    active_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="resumes")
    versions: Mapped[List["ResumeVersionRecord"]] = relationship(
        "ResumeVersionRecord",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="desc(ResumeVersionRecord.version_number)"
    )


class ResumeVersionRecord(Base):
    """Specific uploaded file version and processing lifecycle state."""
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    version_label: Mapped[str] = mapped_column(String(100), default="v1", nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf, docx
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    parsing_status: Mapped[str] = mapped_column(String(30), default="UPLOADED", index=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resume: Mapped["ResumeRecord"] = relationship("ResumeRecord", back_populates="versions")
    extraction: Mapped[Optional["ResumeExtractionRecord"]] = relationship(
        "ResumeExtractionRecord",
        back_populates="resume_version",
        uselist=False,
        cascade="all, delete-orphan"
    )
    review: Mapped[Optional["ResumeReviewRecord"]] = relationship(
        "ResumeReviewRecord",
        back_populates="resume_version",
        uselist=False,
        cascade="all, delete-orphan"
    )
    ats_analyses: Mapped[List["ATSAnalysisRecord"]] = relationship(
        "ATSAnalysisRecord",
        back_populates="resume_version",
        cascade="all, delete-orphan"
    )


class ResumeExtractionRecord(Base):
    """Structured information and evidence extracted from a resume version."""
    __tablename__ = "resume_extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    sections_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    personal_info_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    education_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    experience_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    skills_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    projects_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    certifications_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    evidence_items_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="extraction")


class ResumeReviewRecord(Base):
    """Candidate review workbench state and synchronization tracking."""
    __tablename__ = "resume_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    review_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    field_reviews_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_synced_to_profile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="review")


class ATSAnalysisRecord(Base):
    """Grounded ATS keyword match and bullet impact analysis."""
    __tablename__ = "ats_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    target_job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    target_job_description: Mapped[str] = mapped_column(Text, nullable=False)
    coverage_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    matched_keywords_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_keywords_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    bullet_impact_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bullet_impact_analysis_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    actionable_suggestions_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    formatting_observations_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    methodology_and_limitations: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="ats_analyses")


# ==============================================================================
# Phase 5: Job Source Framework Models
# ==============================================================================

class JobSourceRecord(Base):
    """Job source configuration, governance policy, and resilience state."""
    __tablename__ = "job_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), default="ATS_JOB_BOARD", nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    integration_method: Mapped[str] = mapped_column(String(30), default="REST_API", nullable=False)
    auth_type: Mapped[str] = mapped_column(String(30), default="NONE_PUBLIC", nullable=False)
    credential_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    policy_decision_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=30.0, nullable=False)
    retry_max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    circuit_breaker_state: Mapped[str] = mapped_column(String(20), default="CLOSED", nullable=False)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cooldown_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    observations: Mapped[List["SourceObservationRecord"]] = relationship(
        "SourceObservationRecord",
        back_populates="source",
        cascade="all, delete-orphan"
    )
    opportunities: Mapped[List["CanonicalOpportunityRecord"]] = relationship(
        "CanonicalOpportunityRecord",
        back_populates="source",
        cascade="all, delete-orphan"
    )
    run_logs: Mapped[List["SourceRunLogRecord"]] = relationship(
        "SourceRunLogRecord",
        back_populates="source",
        cascade="all, delete-orphan"
    )


class SourceObservationRecord(Base):
    """Raw payload observation and provenance record."""
    __tablename__ = "source_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    listing_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    source_published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_payload_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    payload_hash_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    normalization_status: Mapped[str] = mapped_column(String(30), default="NORMALIZED", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord", back_populates="observations")


class CanonicalOpportunityRecord(Base):
    """Canonical, normalized career opportunity stored in Core platform."""
    __tablename__ = "canonical_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    dedup_key_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description_clean: Mapped[str] = mapped_column(Text, nullable=False)
    employment_type: Mapped[str] = mapped_column(String(30), default="FULL_TIME", nullable=False)
    workplace_type: Mapped[str] = mapped_column(String(30), default="UNKNOWN", nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    salary_period: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_salary_estimated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    required_skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    application_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_successful_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_derivation_notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), default="UNVERIFIED", index=True, nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(30), default="UNKNOWN", index=True, nullable=False)
    is_suppressed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    provenance_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord", back_populates="opportunities")
    verification_evidence: Mapped[List["VerificationEvidenceRecord"]] = relationship(
        "VerificationEvidenceRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    source_mappings: Mapped[List["OpportunitySourceMappingRecord"]] = relationship(
        "OpportunitySourceMappingRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    feedbacks: Mapped[List["UserListingFeedbackRecord"]] = relationship(
        "UserListingFeedbackRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )


class SourceRunLogRecord(Base):
    """Execution metrics and audit logs for source ingestion runs."""
    __tablename__ = "source_run_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(30), default="MANUAL", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="RUNNING", nullable=False)
    records_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_normalized: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicates_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    safe_error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord", back_populates="run_logs")


# ==============================================================================
# Phase 6: Verification, Deduplication, Freshness & Evidence Models
# ==============================================================================

class VerificationEvidenceRecord(Base):
    """Immutable audit trail of a verification check and its concrete evidentiary basis."""
    __tablename__ = "verification_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    check_id: Mapped[str] = mapped_column(String(36), default=generate_uuid, index=True, nullable=False)
    check_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    check_method: Mapped[str] = mapped_column(String(50), nullable=False)
    check_outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    provider_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_category: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    safe_response_metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_rule_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    confidence_category: Mapped[str] = mapped_column(String(30), default="HIGH", nullable=False)
    error_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    next_eligible_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="verification_evidence")
    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord")


class OpportunitySourceMappingRecord(Base):
    """Preserves distinct source observations mapped to a canonical opportunity record."""
    __tablename__ = "opportunity_source_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    canonical_opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    mapping_status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    match_tier: Mapped[str] = mapped_column(String(30), default="TIER_1_EXACT", nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), default="EXACT_SOURCE_ID", nullable=False)
    match_evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    merge_decision_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="source_mappings")
    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord")


class MergeDecisionRecord(Base):
    """Auditable record of a merge or unmerge decision across duplicate opportunities."""
    __tablename__ = "merge_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    canonical_opportunity_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    original_opportunity_ids_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    match_tier: Mapped[str] = mapped_column(String(30), nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), default="SYSTEM", nullable=False)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="CONFIRMED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    unmerged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unmerged_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    unmerge_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DuplicateCandidateRecord(Base):
    """Pairwise duplicate candidate awaiting automated or human administrative review."""
    __tablename__ = "duplicate_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    primary_opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    duplicate_opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    match_tier: Mapped[str] = mapped_column(String(30), default="TIER_3_PROBABLE", nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PROPOSED", nullable=False)
    decision_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    primary_opportunity: Mapped["CanonicalOpportunityRecord"] = relationship(
        "CanonicalOpportunityRecord",
        foreign_keys=[primary_opportunity_id]
    )
    duplicate_opportunity: Mapped["CanonicalOpportunityRecord"] = relationship(
        "CanonicalOpportunityRecord",
        foreign_keys=[duplicate_opportunity_id]
    )


class UserListingFeedbackRecord(Base):
    """User-reported feedback regarding listing inaccuracies, broken links, or closures."""
    __tablename__ = "user_listing_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    feedback_type: Mapped[str] = mapped_column(String(30), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="RECEIVED", nullable=False)
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="feedbacks")


