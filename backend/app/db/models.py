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
