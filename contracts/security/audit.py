"""
RIGHT FIT — Security Audit Event Contract
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AuditEventType(StrEnum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST"
    PASSWORD_RESET_COMPLETE = "PASSWORD_RESET_COMPLETE"
    EMAIL_VERIFIED = "EMAIL_VERIFIED"
    SESSION_REVOKED = "SESSION_REVOKED"
    ACCOUNT_SUSPENDED = "ACCOUNT_SUSPENDED"
    PRIVACY_SETTINGS_UPDATED = "PRIVACY_SETTINGS_UPDATED"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_WITHDRAWN = "CONSENT_WITHDRAWN"
    DATA_EXPORT_REQUESTED = "DATA_EXPORT_REQUESTED"
    DATA_EXPORT_COMPLETED = "DATA_EXPORT_COMPLETED"
    ACCOUNT_DELETION_REQUESTED = "ACCOUNT_DELETION_REQUESTED"
    ACCOUNT_DELETION_COMPLETED = "ACCOUNT_DELETION_COMPLETED"


class SecurityAuditEventResponse(BaseModel):
    id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: Optional[str] = None
    actor_email: Optional[str] = None
    status: str
    ip_address: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

