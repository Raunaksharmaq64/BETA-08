"""
Unit Tests: Outage Resilience, False Positive Prevention & Feedback Rate Limiting
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

import pytest
from datetime import timedelta
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.db.models import CanonicalOpportunityRecord, JobSourceRecord, utc_now
from app.services.verification_service import VerificationService
from app.services.feedback_service import FeedbackRateLimiter
from contracts.verification.schemas import VerificationStatus


def test_outage_does_not_falsely_close_open_listing():
    """Verify ATS 503 outage / network timeout results in CHECK_FAILED and does NOT close vacancy."""
    db = MagicMock(spec=Session)
    opp = CanonicalOpportunityRecord(
        id="opp-outage-1",
        source_id="src-1",
        external_job_id="job-1",
        dedup_key_sha256="hash1",
        title="Senior SRE",
        company_name="Cloud Corp",
        description_clean="Desc",
        application_url="https://careers.example.com/jobs/outage-503",
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
        closed_at=None,
        status_changed_at=utc_now() - timedelta(days=2),
    )
    source = JobSourceRecord(
        id="src-1",
        source_key="greenhouse_direct",
        display_name="Greenhouse Direct",
        provider="GREENHOUSE",
        base_url="https://boards-api.greenhouse.io",
    )
    opp.source = source
    db.get.return_value = opp

    verified = VerificationService.verify_opportunity(db, opp.id, force=True)

    # CRITICAL: Must be CHECK_FAILED, NOT CLOSED_CONFIRMED!
    assert verified.verification_status == VerificationStatus.CHECK_FAILED.value
    assert verified.closed_at is None  # Must NOT set closed_at!


def test_feedback_rate_limiter_enforcement():
    """Verify rate limiter permits 5 submissions per minute and blocks the 6th."""
    limiter = FeedbackRateLimiter(max_requests=5, window_seconds=60)
    user_id = "test-user-rate-limit"

    for i in range(5):
        assert limiter.is_allowed(user_id) is True, f"Request {i+1} should be allowed"

    # 6th request within window must be rejected
    assert limiter.is_allowed(user_id) is False
