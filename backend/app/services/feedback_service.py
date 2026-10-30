"""
RIGHT FIT — User Listing Feedback Service
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    CanonicalOpportunityRecord,
    UserListingFeedbackRecord,
    utc_now,
)
from contracts.verification.schemas import (
    FeedbackStatus,
    FeedbackType,
)
from app.services.verification_service import VerificationService

logger = logging.getLogger("rightfit.feedback")


class FeedbackRateLimiter:
    """In-memory sliding window rate limiter for user listing feedback submissions."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if the identifier is within the rate limit."""
        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self._history.get(identifier, [])
        # Evict timestamps outside current window
        valid_timestamps = [t for t in timestamps if t > window_start]

        if len(valid_timestamps) >= self.max_requests:
            self._history[identifier] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self._history[identifier] = valid_timestamps
        return True


# Global feedback rate limiter instance (5 feedback submissions per minute)
feedback_rate_limiter = FeedbackRateLimiter(max_requests=5, window_seconds=60)


class FeedbackService:
    """Service handling candidate and administrative listing feedback."""

    @staticmethod
    def hash_ip(client_ip: Optional[str]) -> Optional[str]:
        """Hash IP address for privacy-conscious spam detection."""
        if not client_ip:
            return None
        return hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

    @classmethod
    def submit_feedback(
        cls,
        db: Session,
        opportunity_id: str,
        feedback_type: FeedbackType,
        notes: Optional[str] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        auto_verify: bool = True,
    ) -> UserListingFeedbackRecord:
        """
        Submit user feedback on an opportunity listing:
        - Validates opportunity exists
        - Enforces sliding-window rate limit
        - Records feedback immutably
        - Dispatches automated re-verification check without blindly altering status
        """
        # Rate limit identifier
        rate_id = user_id or cls.hash_ip(client_ip) or "anonymous"
        if not feedback_rate_limiter.is_allowed(rate_id):
            raise PermissionError("Feedback submission rate limit exceeded. Please wait a minute before reporting again.")

        opportunity = db.get(CanonicalOpportunityRecord, opportunity_id)
        if not opportunity:
            raise ValueError(f"Opportunity not found: {opportunity_id}")

        ip_hash = cls.hash_ip(client_ip)
        feedback = UserListingFeedbackRecord(
            opportunity_id=opportunity_id,
            user_id=user_id,
            feedback_type=feedback_type.value,
            notes=notes,
            status=FeedbackStatus.RECEIVED.value,
            ip_hash=ip_hash,
            created_at=utc_now(),
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        logger.info(f"User feedback recorded for opportunity {opportunity_id} ({feedback_type.value})")

        # When feedback indicates broken link or closure, trigger evidentiary verification
        if auto_verify and feedback_type in (FeedbackType.BROKEN_LINK, FeedbackType.ALREADY_CLOSED):
            try:
                VerificationService.verify_opportunity(
                    db=db,
                    opportunity_id=opportunity_id,
                    force=True,
                    check_method="URL_PROBE" if feedback_type == FeedbackType.BROKEN_LINK else "DIRECT_API",
                )
                feedback.status = FeedbackStatus.VERIFIED.value
                db.commit()
                db.refresh(feedback)
            except Exception as e:
                logger.warning(f"Auto-verification triggered by feedback failed: {e}")

        return feedback

    @classmethod
    def list_feedbacks_for_opportunity(
        cls,
        db: Session,
        opportunity_id: str,
    ) -> List[UserListingFeedbackRecord]:
        """Fetch all feedback records for an opportunity."""
        return list(
            db.execute(
                select(UserListingFeedbackRecord)
                .where(UserListingFeedbackRecord.opportunity_id == opportunity_id)
                .order_by(UserListingFeedbackRecord.created_at.desc())
            ).scalars().all()
        )

