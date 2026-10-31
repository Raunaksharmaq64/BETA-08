"""
Unit Tests: Candidate Relevance Feedback Isolation
Phase: 11 — Unified Opportunities Engine and Dashboard
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from app.db.models import (
    CandidateOpportunityFeedbackRecord,
    CanonicalOpportunityRecord,
    User,
)
from app.core.database import AsyncSessionLocal
from app.services.unified_opportunity_service import UnifiedOpportunityService


@pytest.mark.asyncio
async def test_record_candidate_feedback_preserves_isolation():
    async with AsyncSessionLocal() as session:
        # Create test candidate
        user = User(
            email=f"feedback_candidate_{datetime.now(timezone.utc).timestamp()}@test.com",
            password_hash="testhash",
            full_name="Feedback Tester",
        )
        session.add(user)

        # Create canonical job opportunity
        job = CanonicalOpportunityRecord(
            id=f"job_feedback_test_{int(datetime.now(timezone.utc).timestamp())}",
            source_id="gh-feedback-test",
            external_job_id="gh-fb-1",
            dedup_key_sha256="hash-fb",
            title="Senior Rust Engineer",
            company_name="Rustacean Corp",
            description_clean="Build high performance systems.",
            application_url="https://rustacean.example.com",
            verification_status="VERIFIED",
        )
        session.add(job)
        await session.commit()
        await session.refresh(user)
        await session.refresh(job)

        # Initial state checks
        orig_verification_status = job.verification_status

        # 1. Candidate marks job as IRRELEVANT
        feedback_rec = await UnifiedOpportunityService.record_candidate_feedback(
            user_id=user.id,
            opportunity_type="JOB",
            opportunity_id=job.id,
            feedback_category="IRRELEVANT",
            explanation="Looking for Python roles, not Rust",
            session=session,
        )

        assert feedback_rec.id is not None
        assert feedback_rec.user_id == user.id
        assert feedback_rec.opportunity_id == job.id
        assert feedback_rec.opportunity_type == "JOB"
        assert feedback_rec.feedback_category == "IRRELEVANT"
        assert feedback_rec.explanation == "Looking for Python roles, not Rust"

        # 2. Assert source canonical opportunity was NOT altered (candidate isolation rule)
        reloaded_job = (await session.execute(
            select(CanonicalOpportunityRecord).where(CanonicalOpportunityRecord.id == job.id)
        )).scalar_one()

        assert reloaded_job.verification_status == orig_verification_status
        assert reloaded_job.verification_status == "VERIFIED"


@pytest.mark.asyncio
async def test_feedback_persisted_in_db():
    async with AsyncSessionLocal() as session:
        user = User(
            email=f"feedback_db_{datetime.now(timezone.utc).timestamp()}@test.com",
            password_hash="testhash",
            full_name="Feedback Query Tester",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Record multiple feedback entries
        await UnifiedOpportunityService.record_candidate_feedback(
            user_id=user.id,
            opportunity_type="FREELANCE",
            opportunity_id="freelance-lead-777",
            feedback_category="ALREADY_APPLIED",
            explanation="Reached out via phone yesterday",
            session=session,
        )
        await UnifiedOpportunityService.record_candidate_feedback(
            user_id=user.id,
            opportunity_type="STARTUP_PAIN_POINT",
            opportunity_id="startup-lead-888",
            feedback_category="INCORRECT_SKILLS",
            explanation="Requires Scala expertise",
            session=session,
        )

        # Verify feedback queryable by user
        stmt = select(CandidateOpportunityFeedbackRecord).where(CandidateOpportunityFeedbackRecord.user_id == user.id)
        res = await session.execute(stmt)
        feedbacks = res.scalars().all()

        assert len(feedbacks) == 2
        categories = {f.feedback_category for f in feedbacks}
        assert "ALREADY_APPLIED" in categories
        assert "INCORRECT_SKILLS" in categories
