"""
Unit Tests: Verification State Machine & Evidence Logging
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

import pytest
from datetime import timedelta
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.db.models import CanonicalOpportunityRecord, JobSourceRecord, VerificationEvidenceRecord, utc_now
from app.services.verification_service import VerificationService
from contracts.verification.schemas import VerificationStatus


def test_verification_status_enum_values():
    """Verify all formal Phase 6 verification statuses exist."""
    statuses = [s.value for s in VerificationStatus]
    assert "UNVERIFIED" in statuses
    assert "OPEN_CONFIRMED" in statuses
    assert "CLOSED_CONFIRMED" in statuses
    assert "EXPIRED_CONFIRMED" in statuses
    assert "UNAVAILABLE" in statuses
    assert "CHECK_FAILED" in statuses
    assert "AMBIGUOUS" in statuses
    assert "STALE" in statuses


def test_synthetic_verification_open():
    """Verify synthetic job source probes return OPEN_CONFIRMED when 200 returned."""
    db = MagicMock(spec=Session)
    opp = CanonicalOpportunityRecord(
        id="opp-test-1",
        source_id="src-syn-1",
        external_job_id="job-1",
        dedup_key_sha256="hash1",
        title="Software Engineer",
        company_name="Acme",
        description_clean="Desc",
        application_url="https://careers.example.com/jobs/1",
        verification_status=VerificationStatus.UNVERIFIED.value,
        first_seen_at=utc_now() - timedelta(days=2),
        last_seen_at=utc_now(),
    )
    source = JobSourceRecord(
        id="src-syn-1",
        source_key="synthetic_feed",
        display_name="Synthetic Source",
        provider="SYNTHETIC",
        base_url="https://careers.example.com",
    )
    opp.source = source
    db.get.return_value = opp

    verified_opp = VerificationService.verify_opportunity(db, opp.id, force=True)

    assert verified_opp.verification_status == VerificationStatus.OPEN_CONFIRMED.value
    assert verified_opp.last_verified_at is not None
    assert db.add.called  # Evidence record persisted


def test_synthetic_verification_closed_on_404():
    """Verify 404 response transitions opportunity to CLOSED_CONFIRMED with closed_at set."""
    db = MagicMock(spec=Session)
    opp = CanonicalOpportunityRecord(
        id="opp-test-2",
        source_id="src-syn-1",
        external_job_id="job-2",
        dedup_key_sha256="hash2",
        title="Product Designer",
        company_name="Acme",
        description_clean="Desc",
        application_url="https://careers.example.com/jobs/404",
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
        first_seen_at=utc_now() - timedelta(days=5),
        last_seen_at=utc_now(),
    )
    source = JobSourceRecord(
        id="src-syn-1",
        source_key="synthetic_feed",
        display_name="Synthetic Source",
        provider="SYNTHETIC",
        base_url="https://careers.example.com",
    )
    opp.source = source
    db.get.return_value = opp

    verified_opp = VerificationService.verify_opportunity(db, opp.id, force=True)

    assert verified_opp.verification_status == VerificationStatus.CLOSED_CONFIRMED.value
    assert verified_opp.closed_at is not None
    assert verified_opp.status_changed_at is not None
