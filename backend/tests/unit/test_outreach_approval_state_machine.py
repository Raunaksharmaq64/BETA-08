"""
Phase 9 Unit Tests — Outreach Mandatory Approval & Suppression State Machine
"""

import pytest
from app.core.database import AsyncSessionLocal
from app.db.models import User, CandidateProfile
from app.services.freelance_service import freelance_service


@pytest.fixture
async def sample_candidate():
    async with AsyncSessionLocal() as session:
        u = User(
            email="outreach_candidate@test.com",
            password_hash="fake_hash",
            full_name="Sarah Miller",
            role="CANDIDATE",
            status="ACTIVE",
            is_email_verified=True,
        )
        session.add(u)
        await session.flush()
        cp = CandidateProfile(user_id=u.id, headline="Full Stack Developer")
        session.add(cp)
        await session.commit()
        return u


@pytest.mark.asyncio
async def test_draft_creation_requires_explicit_approval_before_send(sample_candidate):
    async with AsyncSessionLocal() as session:
        # Create an opportunity
        opp = await freelance_service.import_lead_as_opportunity(
            session,
            {"name": "Local Clinic", "city": "Seattle", "website": "https://localclinic.com", "is_broken_website": True}
        )

        draft = await freelance_service.generate_outreach_draft(
            session, user_id=sample_candidate.id, opportunity_id=opp.id
        )
        assert draft.status == "DRAFT"
        assert draft.is_approved is False

        # Attempt to send without approval must be blocked
        with pytest.raises(PermissionError) as exc_info:
            await freelance_service.send_outreach_message(session, user_id=sample_candidate.id, draft_id=draft.id)
        assert "candidate has not explicitly approved" in str(exc_info.value)


@pytest.mark.asyncio
async def test_editing_approved_draft_invalidates_approval(sample_candidate):
    async with AsyncSessionLocal() as session:
        opp = await freelance_service.import_lead_as_opportunity(
            session,
            {"name": "Metro Bakery", "city": "Denver", "email": "info@metrobakery.com"}
        )
        draft = await freelance_service.generate_outreach_draft(session, sample_candidate.id, opp.id)

        # Explicit candidate approval
        approved = await freelance_service.approve_outreach_draft(session, sample_candidate.id, draft.id)
        assert approved.is_approved is True
        assert approved.status == "APPROVED"
        assert approved.approved_body_hash is not None

        # Candidate edits body -> MUST invalidate approval
        edited = await freelance_service.update_outreach_draft(
            session, sample_candidate.id, draft.id, message_body="Edited message with new portfolio link."
        )
        assert edited.is_approved is False
        assert edited.status == "PENDING_REVIEW"
        assert edited.approved_body_hash is None
        assert edited.candidate_edits_count == 1

        # Attempt to send must fail until re-approved
        with pytest.raises(PermissionError):
            await freelance_service.send_outreach_message(session, sample_candidate.id, draft.id)

        # Re-approval
        reapproved = await freelance_service.approve_outreach_draft(session, sample_candidate.id, draft.id)
        assert reapproved.is_approved is True
        assert reapproved.status == "APPROVED"


@pytest.mark.asyncio
async def test_suppressed_recipient_aborts_send(sample_candidate):
    async with AsyncSessionLocal() as session:
        opp = await freelance_service.import_lead_as_opportunity(
            session,
            {"name": "Quiet Books", "city": "Boston", "email": "optout@quietbooks.com"}
        )
        draft = await freelance_service.generate_outreach_draft(session, sample_candidate.id, opp.id)
        await freelance_service.approve_outreach_draft(session, sample_candidate.id, draft.id)

        # Add recipient to suppression list
        await freelance_service.add_suppression(session, "optout@quietbooks.com", reason="UNSUBSCRIBED")

        # Attempt send should be aborted by suppression filter
        with pytest.raises(PermissionError) as exc_info:
            await freelance_service.send_outreach_message(session, sample_candidate.id, draft.id)
        assert "suppression list" in str(exc_info.value)
