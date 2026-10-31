"""
Unit tests for Startup Pitch Draft Generator with Explicit Assumptions
Phase: 10 — Startup Intelligence Integration
"""

import json
import pytest
from app.core.database import AsyncSessionLocal
from app.services.startup_service import StartupService
from app.db.models import User, CandidateProfile, CandidateSkillRecord, StartupOpportunityRecord


@pytest.mark.asyncio
async def test_pitch_generator_includes_explicit_assumptions_and_grounded_skills():
    async with AsyncSessionLocal() as session:
        # 1. Create candidate user with profile and skills
        user = User(
            email="founder_pitcher@example.com",
            password_hash="argon2_hashed_secret",
            full_name="Sarah Connor",
            role="CANDIDATE",
            status="ACTIVE",
        )
        session.add(user)
        await session.flush()

        profile = CandidateProfile(
            user_id=user.id,
            headline="Senior DevOps Engineer & Performance Specialist",
        )
        session.add(profile)
        await session.flush()

        skill1 = CandidateSkillRecord(profile_id=profile.id, skill_name="PostgreSQL", category="Database")
        skill2 = CandidateSkillRecord(profile_id=profile.id, skill_name="Next.js", category="Frontend")
        session.add_all([skill1, skill2])
        await session.flush()

        # 2. Create startup opportunity
        opp = StartupOpportunityRecord(
            startup_name="FastScale Cloud",
            domain="fastscale.net",
            category="Database",
            detected_signal="Database query timeouts during spike hours",
            urgency_score=9,
            primary_source="Hacker News",
        )
        session.add(opp)
        await session.commit()

        # 3. Generate pitch draft
        draft = await StartupService.generate_startup_pitch_draft(
            user_id=user.id,
            opportunity_id=opp.id,
            tone="formal",
            session=session
        )

        assert draft.candidate_id == user.id
        assert draft.opportunity_id == opp.id
        assert "FastScale Cloud" in draft.subject
        assert "Sarah Connor" in draft.body
        assert "PostgreSQL" in draft.body or "Next.js" in draft.body

        # Verify explicit assumptions checklist is stored
        assumptions = json.loads(draft.explicit_assumptions)
        assert len(assumptions) >= 4
        assert any("actively seeking external help" in a for a in assumptions)
        assert any("budget" in a for a in assumptions)

        # Verify update increments candidate_edits_count
        updated = await StartupService.update_startup_pitch_draft(
            draft_id=draft.id,
            user_id=user.id,
            subject="Updated Subject Line",
            body="Updated body with personalized note.",
            tone="casual",
            session=session,
        )
        assert updated.candidate_edits_count == 1
        assert updated.subject == "Updated Subject Line"
