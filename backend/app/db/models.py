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
    saved_jobs: Mapped[List["SavedJobRecord"]] = relationship("SavedJobRecord", back_populates="user", cascade="all, delete-orphan")
    saved_searches: Mapped[List["SavedSearchRecord"]] = relationship("SavedSearchRecord", back_populates="user", cascade="all, delete-orphan")
    alert_logs: Mapped[List["AlertDeliveryLogRecord"]] = relationship("AlertDeliveryLogRecord", back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[List["ApplicationRecord"]] = relationship("ApplicationRecord", back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[List["ReminderRecord"]] = relationship("ReminderRecord", back_populates="user", cascade="all, delete-orphan")
    interview_plans: Mapped[List["InterviewPlanRecord"]] = relationship("InterviewPlanRecord", back_populates="user", cascade="all, delete-orphan")
    star_answers: Mapped[List["STARAnswerRecord"]] = relationship("STARAnswerRecord", back_populates="user", cascade="all, delete-orphan")
    mock_sessions: Mapped[List["MockInterviewSessionRecord"]] = relationship("MockInterviewSessionRecord", back_populates="user", cascade="all, delete-orphan")
    debriefs: Mapped[List["InterviewDebriefRecord"]] = relationship("InterviewDebriefRecord", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["NotificationRecord"]] = relationship("NotificationRecord", back_populates="user", cascade="all, delete-orphan")
    notification_preferences: Mapped[Optional["NotificationPreferencesRecord"]] = relationship("NotificationPreferencesRecord", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_freelance_opportunities: Mapped[List["SavedFreelanceOpportunityRecord"]] = relationship("SavedFreelanceOpportunityRecord", back_populates="user", cascade="all, delete-orphan")
    outreach_drafts: Mapped[List["OutreachDraftRecord"]] = relationship("OutreachDraftRecord", back_populates="user", cascade="all, delete-orphan")


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
    saved_by: Mapped[List["SavedJobRecord"]] = relationship(
        "SavedJobRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    applications: Mapped[List["ApplicationRecord"]] = relationship(
        "ApplicationRecord",
        back_populates="opportunity"
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


# ==============================================================================
# Phase 7: Job Search, Candidate Matching, Saved Jobs & Alerts
# ==============================================================================

class SavedJobRecord(Base):
    """Candidate-saved job listing with optional private notes."""
    __tablename__ = "saved_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_jobs")
    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="saved_by")


class SavedSearchRecord(Base):
    """Saved search query parameters and candidate alert notification subscription."""
    __tablename__ = "saved_searches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    query_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    filters_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alert_frequency: Mapped[str] = mapped_column(String(20), default="DAILY", nullable=False)
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_searches")
    delivery_logs: Mapped[List["AlertDeliveryLogRecord"]] = relationship(
        "AlertDeliveryLogRecord",
        back_populates="saved_search",
        cascade="all, delete-orphan"
    )


class AlertDeliveryLogRecord(Base):
    """Audit log of delivered job match alert notifications."""
    __tablename__ = "alert_delivery_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    saved_search_id: Mapped[str] = mapped_column(String(36), ForeignKey("saved_searches.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_ids_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(30), default="IN_APP", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DELIVERED", nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="alert_logs")
    saved_search: Mapped["SavedSearchRecord"] = relationship("SavedSearchRecord", back_populates="delivery_logs")


# ==============================================================================
# Phase 8: CRM, Reminders, Interview Intelligence & Notifications Models
# ==============================================================================

class ApplicationRecord(Base):
    """Candidate job application tracking and CRM entity."""
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="SET NULL"), nullable=True, index=True)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    application_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="SAVED", index=True, nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    apply_link_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_submission_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salary_offered: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD", nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="applications")
    opportunity: Mapped[Optional["CanonicalOpportunityRecord"]] = relationship("CanonicalOpportunityRecord", back_populates="applications")
    status_history: Mapped[List["ApplicationStatusHistoryRecord"]] = relationship(
        "ApplicationStatusHistoryRecord",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="desc(ApplicationStatusHistoryRecord.changed_at)"
    )
    notes: Mapped[List["ApplicationNoteRecord"]] = relationship(
        "ApplicationNoteRecord",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="desc(ApplicationNoteRecord.created_at)"
    )
    reminders: Mapped[List["ReminderRecord"]] = relationship(
        "ReminderRecord",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    interview_plans: Mapped[List["InterviewPlanRecord"]] = relationship(
        "InterviewPlanRecord",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    debriefs: Mapped[List["InterviewDebriefRecord"]] = relationship(
        "InterviewDebriefRecord",
        back_populates="application",
        cascade="all, delete-orphan"
    )


class ApplicationStatusHistoryRecord(Base):
    """Immutable audit trail of application state transitions."""
    __tablename__ = "application_status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(30), default="CANDIDATE", nullable=False)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="status_history")


class ApplicationNoteRecord(Base):
    """Candidate private notes attached to an application."""
    __tablename__ = "application_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    note_type: Mapped[str] = mapped_column(String(30), default="GENERAL", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="notes")


class ReminderRecord(Base):
    """Candidate scheduled follow-ups, interview reminders, and deadlines."""
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    application_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    reminder_type: Mapped[str] = mapped_column(String(30), default="FOLLOW_UP", nullable=False)
    due_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reminders")
    application: Mapped[Optional["ApplicationRecord"]] = relationship("ApplicationRecord", back_populates="reminders")


class InterviewPlanRecord(Base):
    """Interview preparation container linking a job role with rounds and study plans."""
    __tablename__ = "interview_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    job_description_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="interview_plans")
    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="interview_plans")
    rounds: Mapped[List["InterviewRoundRecord"]] = relationship(
        "InterviewRoundRecord",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="InterviewRoundRecord.round_number"
    )
    star_answers: Mapped[List["STARAnswerRecord"]] = relationship(
        "STARAnswerRecord",
        back_populates="plan",
        cascade="all, delete-orphan"
    )
    mock_sessions: Mapped[List["MockInterviewSessionRecord"]] = relationship(
        "MockInterviewSessionRecord",
        back_populates="plan"
    )


class InterviewRoundRecord(Base):
    """Specific scheduled round within an interview plan."""
    __tablename__ = "interview_rounds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    round_name: Mapped[str] = mapped_column(String(150), nullable=False)
    scheduled_at_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_format: Mapped[str] = mapped_column(String(30), default="VIDEO", nullable=False)
    interviewer_names: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    focus_areas_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED", nullable=False)

    plan: Mapped["InterviewPlanRecord"] = relationship("InterviewPlanRecord", back_populates="rounds")


class STARAnswerRecord(Base):
    """Structured STAR answer grounded in candidate verified resume and experience."""
    __tablename__ = "star_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("interview_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="TECHNICAL_CHALLENGE", nullable=False)
    situation: Mapped[str] = mapped_column(Text, nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    missing_information_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_candidate_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="star_answers")
    plan: Mapped[Optional["InterviewPlanRecord"]] = relationship("InterviewPlanRecord", back_populates="star_answers")


class MockInterviewSessionRecord(Base):
    """Interactive practice interview session."""
    __tablename__ = "mock_interview_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    plan_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("interview_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    session_type: Mapped[str] = mapped_column(String(30), default="BEHAVIORAL", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="IN_PROGRESS", nullable=False)
    average_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_feedback_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="mock_sessions")
    plan: Mapped[Optional["InterviewPlanRecord"]] = relationship("InterviewPlanRecord", back_populates="mock_sessions")
    questions: Mapped[List["MockInterviewQuestionRecord"]] = relationship(
        "MockInterviewQuestionRecord",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MockInterviewQuestionRecord.order_index"
    )


class MockInterviewQuestionRecord(Base):
    """Individual question and rubric evaluation within a mock interview session."""
    __tablename__ = "mock_interview_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    question_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    candidate_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    follow_up_question: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["MockInterviewSessionRecord"] = relationship("MockInterviewSessionRecord", back_populates="questions")


class InterviewDebriefRecord(Base):
    """Post-interview candidate reflections, questions asked, and follow-up tracking."""
    __tablename__ = "interview_debriefs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    round_name: Mapped[str] = mapped_column(String(150), nullable=False)
    interview_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    questions_asked_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    topics_discussed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_reflections: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    areas_to_improve: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recruiter_commitments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_response_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_step: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="debriefs")
    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="debriefs")


class NotificationRecord(Base):
    """In-app alerts and notifications delivered to candidate."""
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="SYSTEM", nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reference_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(30), default="IN_APP", nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(30), default="DELIVERED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class NotificationPreferencesRecord(Base):
    """Candidate notification settings and delivery channel controls."""
    __tablename__ = "notification_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    interview_reminders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    application_follow_ups: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    assessment_deadlines: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prep_milestones: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notification_preferences")


# ==============================================================================
# PHASE 9: FREELANCE OPPORTUNITIES, CONTACT EVIDENCE & OUTREACH
# ==============================================================================

class FreelanceOpportunityRecord(Base):
    """Canonical freelance and local business development opportunity imported from LeadHunter."""
    __tablename__ = "freelance_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    leadhunter_lead_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    place_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    opportunity_title: Mapped[str] = mapped_column(String(255), nullable=False)
    service_category: Mapped[str] = mapped_column(String(120), default="Web Development", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    is_broken_website: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    required_skills: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    suggested_service: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    suggested_pitch: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    classification_state: Mapped[str] = mapped_column(
        String(50), default="POTENTIAL_FREELANCE_OPPORTUNITY", index=True, nullable=False
    )
    classification_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    source: Mapped[str] = mapped_column(String(60), default="leadhunter_google_maps", nullable=False)
    original_source_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    contact_evidence: Mapped[List["ContactEvidenceRecord"]] = relationship(
        "ContactEvidenceRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    drafts: Mapped[List["OutreachDraftRecord"]] = relationship(
        "OutreachDraftRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    saved_by: Mapped[List["SavedFreelanceOpportunityRecord"]] = relationship(
        "SavedFreelanceOpportunityRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )


class ContactEvidenceRecord(Base):
    """Audit evidence ledger for contact points discovered for a freelance opportunity."""
    __tablename__ = "contact_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("freelance_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    contact_type: Mapped[str] = mapped_column(String(30), nullable=False)  # EMAIL, PHONE, WEBSITE, etc.
    contact_value: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(60), default="leadhunter", nullable=False)
    source_evidence_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    evidence_status: Mapped[str] = mapped_column(String(30), default="OBSERVED", nullable=False)
    verification_method: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["FreelanceOpportunityRecord"] = relationship(
        "FreelanceOpportunityRecord", back_populates="contact_evidence"
    )


class SavedFreelanceOpportunityRecord(Base):
    """Candidate-saved freelance opportunity bookmarks."""
    __tablename__ = "saved_freelance_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("freelance_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="SAVED", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_freelance_opportunities")
    opportunity: Mapped["FreelanceOpportunityRecord"] = relationship(
        "FreelanceOpportunityRecord", back_populates="saved_by"
    )


class OutreachDraftRecord(Base):
    """Outreach message draft requiring explicit candidate review and approval."""
    __tablename__ = "outreach_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("freelance_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel: Mapped[str] = mapped_column(String(30), default="EMAIL", nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    recipient_contact: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_service: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", index=True, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_recipient: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_body_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    candidate_edits_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="outreach_drafts")
    opportunity: Mapped["FreelanceOpportunityRecord"] = relationship(
        "FreelanceOpportunityRecord", back_populates="drafts"
    )
    delivery_logs: Mapped[List["OutreachDeliveryLogRecord"]] = relationship(
        "OutreachDeliveryLogRecord", back_populates="draft", cascade="all, delete-orphan"
    )


class OutreachDeliveryLogRecord(Base):
    """Audit delivery ledger for sent outreach messages."""
    __tablename__ = "outreach_delivery_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    draft_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outreach_drafts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), default="SMTP", nullable=False)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    provider_raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), default="SENT", nullable=False)
    webhook_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    draft: Mapped["OutreachDraftRecord"] = relationship(
        "OutreachDraftRecord", back_populates="delivery_logs"
    )


class OutreachSuppressionRecord(Base):
    """Do-not-contact and unsubscribed recipients suppression list."""
    __tablename__ = "outreach_suppression_list"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    recipient_value: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(50), default="UNSUBSCRIBED", nullable=False)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)





