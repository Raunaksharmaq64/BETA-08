"""
RIGHT FIT — Authentication & Identity Schemas
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(StrEnum):
    """User authorization roles."""
    CANDIDATE = "CANDIDATE"
    RECRUITER = "RECRUITER"
    ADMIN = "ADMIN"


class AccountStatus(StrEnum):
    """Lifecycle states of a user account."""
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETION_PENDING = "DELETION_PENDING"
    DELETED = "DELETED"


class RegisterRequest(BaseModel):
    """Candidate account registration payload."""
    email: EmailStr = Field(..., description="Unique email address.")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars, mixed complexity).")
    full_name: str = Field(..., min_length=2, max_length=120, description="Legal or professional full name.")
    role: UserRole = Field(default=UserRole.CANDIDATE, description="Account role.")


class LoginRequest(BaseModel):
    """Account login payload."""
    email: EmailStr = Field(..., description="Registered account email.")
    password: str = Field(..., description="Account password.")


class TokenResponse(BaseModel):
    """Standard authentication token response."""
    access_token: str = Field(..., description="Short-lived JWT access token.")
    token_type: str = Field(default="Bearer", description="Token schema type.")
    expires_in: int = Field(..., description="Access token expiration window in seconds.")
    refresh_token: Optional[str] = Field(default=None, description="Rotating refresh token for session renewal.")


class RefreshTokenRequest(BaseModel):
    """Session renewal payload."""
    refresh_token: str = Field(..., description="Rotating refresh token.")


class UserResponse(BaseModel):
    """Public user identity representation."""
    id: str = Field(..., description="Unique user UUID.")
    email: EmailStr = Field(..., description="User email address.")
    full_name: str = Field(..., description="User full name.")
    role: UserRole = Field(..., description="Assigned role.")
    status: AccountStatus = Field(..., description="Account lifecycle state.")
    is_email_verified: bool = Field(..., description="Whether email has been verified.")
    created_at: datetime = Field(..., description="Account creation timestamp.")


class ChangePasswordRequest(BaseModel):
    """In-session password change payload."""
    current_password: str = Field(..., description="Current password for verification.")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password.")


class ForgotPasswordRequest(BaseModel):
    """Account recovery request."""
    email: EmailStr = Field(..., description="Account email to dispatch reset token to.")


class ResetPasswordRequest(BaseModel):
    """Password reset completion payload."""
    token: str = Field(..., description="Cryptographically secure reset token.")
    new_password: str = Field(..., min_length=8, max_length=128, description="New account password.")


class VerifyEmailRequest(BaseModel):
    """Email verification payload."""
    token: str = Field(..., description="Verification token dispatched to user email.")


class ResendVerificationRequest(BaseModel):
    """Resend email verification payload."""
    email: EmailStr = Field(..., description="Account email.")

