"""
Unit Tests: Independent Timestamps & Freshness Tracking
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.db.models import CanonicalOpportunityRecord, utc_now
from app.services.verification_service import VerificationService
from contracts.verification.schemas import FreshnessState, VerificationStatus


def test_independent_timestamp_fields_exist():
    """Verify that CanonicalOpportunityRecord defines all required independent timestamps."""
    now = utc_now()
    opp = CanonicalOpportunityRecord(
        source_id="src-123",
        external_job_id="job-999",
        dedup_key_sha256="abc123hash",
        title="Senior Python Backend Engineer",
        company_name="Acme AI",
        description_clean="Clean job description text",
        application_url="https://jobs.example.com/999",
        source_published_at=now - timedelta(days=5),
        source_updated_at=now - timedelta(days=2),
        first_seen_at=now - timedelta(days=5),
        last_seen_at=now - timedelta(hours=1),
        last_checked_at=now - timedelta(minutes=30),
        last_successful_check_at=now - timedelta(minutes=30),
        last_verified_at=now - timedelta(minutes=30),
        status_changed_at=now - timedelta(days=1),
        closed_at=None,
        expires_at=now + timedelta(days=25),
        expiry_derivation_notes="Explicit provider expiry header",
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
        freshness_state=FreshnessState.FRESH.value,
        is_suppressed=False,
    )

    assert opp.source_published_at is not None
    assert opp.source_updated_at is not None
    assert opp.first_seen_at is not None
    assert opp.last_seen_at is not None
    assert opp.last_checked_at is not None
    assert opp.last_successful_check_at is not None
    assert opp.last_verified_at is not None
    assert opp.status_changed_at is not None
    assert opp.closed_at is None
    assert opp.expires_at is not None
    assert opp.expiry_derivation_notes == "Explicit provider expiry header"


def test_freshness_computation_rules():
    """Verify compute_freshness accurately categorizes listings based on timestamp elapsed intervals."""
    now = utc_now()

    # 1. Fresh: seen within 7 days
    fresh_opp = CanonicalOpportunityRecord(
        source_id="src-1",
        external_job_id="job-1",
        dedup_key_sha256="hash1",
        title="Engineer",
        company_name="Corp",
        description_clean="Desc",
        application_url="https://corp.com/jobs/1",
        first_seen_at=now - timedelta(days=3),
        last_seen_at=now - timedelta(days=2),
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
    )
    assert VerificationService.compute_freshness(fresh_opp) == FreshnessState.FRESH

    # 2. Aging: seen 10 days ago (between 7 and 21 days)
    aging_opp = CanonicalOpportunityRecord(
        source_id="src-1",
        external_job_id="job-2",
        dedup_key_sha256="hash2",
        title="Engineer",
        company_name="Corp",
        description_clean="Desc",
        application_url="https://corp.com/jobs/2",
        first_seen_at=now - timedelta(days=15),
        last_seen_at=now - timedelta(days=10),
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
    )
    assert VerificationService.compute_freshness(aging_opp) == FreshnessState.AGING

    # 3. Stale: seen 25 days ago (> 21 days), previously checked
    stale_opp = CanonicalOpportunityRecord(
        source_id="src-1",
        external_job_id="job-3",
        dedup_key_sha256="hash3",
        title="Engineer",
        company_name="Corp",
        description_clean="Desc",
        application_url="https://corp.com/jobs/3",
        first_seen_at=now - timedelta(days=40),
        last_seen_at=now - timedelta(days=25),
        last_checked_at=now - timedelta(days=25),
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
    )
    assert VerificationService.compute_freshness(stale_opp) == FreshnessState.STALE

    # 4. Check Overdue: seen 20 days ago with no verification check performed
    overdue_opp = CanonicalOpportunityRecord(
        source_id="src-1",
        external_job_id="job-overdue",
        dedup_key_sha256="hash_overdue",
        title="Engineer",
        company_name="Corp",
        description_clean="Desc",
        application_url="https://corp.com/jobs/overdue",
        first_seen_at=now - timedelta(days=30),
        last_seen_at=now - timedelta(days=20),
        last_checked_at=None,
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
    )
    assert VerificationService.compute_freshness(overdue_opp) == FreshnessState.CHECK_OVERDUE

    # 4. Link Unavailable
    unavail_opp = CanonicalOpportunityRecord(
        source_id="src-1",
        external_job_id="job-4",
        dedup_key_sha256="hash4",
        title="Engineer",
        company_name="Corp",
        description_clean="Desc",
        application_url="https://corp.com/jobs/4",
        first_seen_at=now - timedelta(days=10),
        last_seen_at=now - timedelta(days=1),
        verification_status=VerificationStatus.UNAVAILABLE.value,
    )
    assert VerificationService.compute_freshness(unavail_opp) == FreshnessState.LINK_UNAVAILABLE


def test_user_explanation_generation():
    """Verify human-readable explanation avoids misleading claims."""
    now = utc_now()
    opp = CanonicalOpportunityRecord(
        source_id="src-1",
        external_job_id="job-1",
        dedup_key_sha256="hash1",
        title="Engineer",
        company_name="Corp",
        description_clean="Desc",
        application_url="https://corp.com/jobs/1",
        first_seen_at=now - timedelta(days=2),
        last_seen_at=now - timedelta(hours=1),
        last_verified_at=now - timedelta(hours=1),
        verification_status=VerificationStatus.OPEN_CONFIRMED.value,
        freshness_state=FreshnessState.FRESH.value,
    )
    label, expl = VerificationService.get_user_explanation(opp)
    assert label == "Status confirmed open"
    assert "active" in expl.lower()
