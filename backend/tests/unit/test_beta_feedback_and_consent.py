"""
Unit tests for Phase 14: Beta Feedback Intake & Consent Lifecycle Management
"""

import pytest
import uuid
from app.core.database import AsyncSessionLocal
from app.services.beta_validation_service import BetaValidationService


@pytest.mark.asyncio
async def test_feedback_submission_and_validation():
    """Verifies feedback submission handles categories, severities, and persists properly."""
    async with AsyncSessionLocal() as session:
        fb = await BetaValidationService.submit_feedback(
            session=session,
            category="SEARCH_RELEVANCE",
            description="Search results for 'FastAPI' included relevant Python jobs but missed one recently posted remote job.",
            related_feature="JOB_SEARCH",
            severity="MEDIUM",
        )

        assert fb["id"] is not None
        assert fb["category"] == "SEARCH_RELEVANCE"
        assert fb["related_feature"] == "JOB_SEARCH"
        assert fb["severity"] == "MEDIUM"
        assert fb["review_status"] == "NEW"


@pytest.mark.asyncio
async def test_feedback_listing_and_triage():
    """Verifies listing feedback with filters and updating triage status with resolution notes."""
    async with AsyncSessionLocal() as session:
        # Submit feedback
        fb1 = await BetaValidationService.submit_feedback(
            session=session,
            category="BROKEN_APPLICATION_LINK",
            description="Link to Acme Corp engineering lead gives HTTP 404.",
            related_feature="JOB_SEARCH",
            severity="HIGH",
        )

        # Triage the feedback
        triaged = await BetaValidationService.update_feedback_status(
            session=session,
            feedback_id=fb1["id"],
            review_status="TRIAGED",
            resolution_notes="Marked listing as EXPIRED and notified source connector.",
            responsible_owner="SiteReliabilityEngineer",
        )

        assert triaged["review_status"] == "TRIAGED"
        assert triaged["responsible_owner"] == "SiteReliabilityEngineer"

        # Query filtered list
        listing = await BetaValidationService.list_feedback(
            session=session,
            review_status="TRIAGED",
        )
        assert listing["total"] >= 1
        found = any(item["id"] == fb1["id"] for item in listing["items"])
        assert found is True


@pytest.mark.asyncio
async def test_consent_lifecycle_and_retention():
    """Verifies recording beta consent, 90-day retention horizon, and retrieval."""
    test_user_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as session:
        consent = await BetaValidationService.record_consent(
            session=session,
            user_id=test_user_id,
            consent_version="v1.0-beta",
            has_consented_data_collection=True,
            has_consented_ai_processing=True,
            has_consented_anonymized_analytics=True,
        )

        assert consent["user_id"] == test_user_id
        assert consent["is_active"] is True
        assert consent["data_retention_expiry"] is not None

        # Retrieve consent
        fetched = await BetaValidationService.get_consent(session=session, user_id=test_user_id)
        assert fetched is not None
        assert fetched["has_consented_data_collection"] is True
        assert fetched["is_active"] is True


@pytest.mark.asyncio
async def test_consent_withdrawal_and_minimization():
    """Verifies that withdrawing consent disables active flags and schedules minimization."""
    test_user_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as session:
        await BetaValidationService.record_consent(
            session=session,
            user_id=test_user_id,
            consent_version="v1.0-beta",
        )

        # Withdraw consent
        withdrawn = await BetaValidationService.withdraw_consent(session=session, user_id=test_user_id)
        assert withdrawn["status"] == "CONSENT_WITHDRAWN"

        # Verify state in DB
        fetched = await BetaValidationService.get_consent(session=session, user_id=test_user_id)
        assert fetched["is_active"] is False
        assert fetched["has_consented_data_collection"] is False
        assert fetched["withdrawn_at"] is not None
