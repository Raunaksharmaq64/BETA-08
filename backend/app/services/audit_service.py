"""
RIGHT FIT Core — Security Audit Event Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SecurityAuditEventRecord, utc_now
from contracts.security.audit import AuditEventType

logger = logging.getLogger("rightfit.security.audit")

SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "raw_token",
    "access_token",
    "refresh_token",
    "reset_token",
    "verification_token",
    "secret",
    "secret_key",
    "credentials",
}


def sanitize_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively removes sensitive keys from audit event details."""
    sanitized: Dict[str, Any] = {}
    for k, v in details.items():
        if any(sensitive in k.lower() for sensitive in SENSITIVE_KEYS):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_details(v)
        elif isinstance(v, (list, tuple)):
            sanitized[k] = [
                sanitize_details(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            sanitized[k] = v
    return sanitized


class AuditService:
    @staticmethod
    async def record_event(
        db: AsyncSession,
        event_type: AuditEventType,
        status: str,
        user_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityAuditEventRecord:
        """Persists a sanitized security audit event to the database."""
        safe_details = sanitize_details(details or {})
        event = SecurityAuditEventRecord(
            event_type=str(event_type.value if hasattr(event_type, "value") else event_type),
            user_id=user_id,
            actor_email=actor_email,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details_json=safe_details,
            timestamp=utc_now(),
        )
        db.add(event)
        # Flush to persist within current transaction without forcing commit
        await db.flush()

        logger.info(
            f"[SECURITY AUDIT] Event={event.event_type} Status={status} "
            f"User={user_id or actor_email or 'anonymous'} IP={ip_address}"
        )
        return event
