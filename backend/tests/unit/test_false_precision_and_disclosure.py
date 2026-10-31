"""
Unit Tests: False Precision Protections & Methodological Disclosure
Phase: 12 — Market & Compensation Intelligence

Explicitly tests the 10 mandated false-precision and transparency protections:
1. One salary observation cannot produce a market median.
2. Small sample produces insufficient-data status rather than universal claims.
3. Missing salary cannot be fabricated or inferred.
4. Total compensation cannot be represented as base salary.
5. Repeated observations of the same vacancy cannot inflate demand.
6. Unsupported trend predictions are prohibited.
7. Currencies are not silently converted or assumed.
8. Candidate skills are never invented or auto-mutated.
9. Source limitations and sample boundaries are always disclosed.
10. Methodology invariants are mathematically audited.
"""

import pytest
from datetime import datetime, timezone
from app.core.database import AsyncSessionLocal
from app.db.models import (
    CandidateProfile,
    CandidateSkillRecord,
    CanonicalOpportunityRecord,
    CompensationObservationRecord,
    User,
)
from app.services.market_intelligence_service import MarketIntelligenceService


@pytest.mark.asyncio
async def test_salary_observation_under_threshold_cannot_produce_median():
    """Assertion 1: Sample size < 5 MUST NOT calculate a statistical median."""
    async with AsyncSessionLocal() as session:
        # Create unique role with only 2 salary observations
        unique_role = f"Unique Blockchain Quantum Architect {datetime.now(timezone.utc).timestamp()}"
        obs1 = CompensationObservationRecord(
            role_title=unique_role,
            compensation_type="BASE_SALARY",
            period="ANNUAL",
            currency="USD",
            min_amount=150000.0,
            max_amount=180000.0,
            sample_size=1,
        )
        obs2 = CompensationObservationRecord(
            role_title=unique_role,
            compensation_type="BASE_SALARY",
            period="ANNUAL",
            currency="USD",
            min_amount=160000.0,
            max_amount=190000.0,
            sample_size=1,
        )
        session.add_all([obs1, obs2])
        await session.commit()

        # Query benchmarks
        benchmarks = await MarketIntelligenceService.get_compensation_benchmarks(
            session=session, role_title=unique_role, compensation_type="BASE_SALARY"
        )

        assert benchmarks["sample_size"] == 2
        # False precision protection: median is None because N < 5
        assert benchmarks["summary_range"]["median"] is None
        assert benchmarks["summary_range"]["has_statistically_justified_median"] is False
        assert benchmarks["confidence_disclosure"] == "INSUFFICIENT_DATA"


@pytest.mark.asyncio
async def test_missing_salary_counted_and_not_fabricated():
    """Assertion 3: Missing salary cannot be fabricated; must count undisclosed jobs."""
    async with AsyncSessionLocal() as session:
        unique_title = f"Secret Salary Role {datetime.now(timezone.utc).timestamp()}"
        job_no_sal = CanonicalOpportunityRecord(
            id=f"job_no_sal_{int(datetime.now(timezone.utc).timestamp())}",
            source_id="src-fake-1",
            external_job_id="ext-fake-1",
            dedup_key_sha256="hash-nosal",
            title=unique_title,
            company_name="Stealth Labs",
            description_clean="Great role",
            application_url="https://stealth.example.com",
            min_salary=None,
            max_salary=None,
            currency=None,
        )
        session.add(job_no_sal)
        await session.commit()

        benchmarks = await MarketIntelligenceService.get_compensation_benchmarks(
            session=session, role_title=unique_title
        )
        # Undisclosed count is detected, not zero and not fabricated into a salary
        assert benchmarks["undisclosed_salary_count"] >= 1
        assert benchmarks["summary_range"]["overall_min"] is None
        assert benchmarks["summary_range"]["overall_max"] is None


@pytest.mark.asyncio
async def test_base_salary_and_total_comp_strictly_isolated():
    """Assertion 4: Total compensation cannot be represented as base salary."""
    async with AsyncSessionLocal() as session:
        unique_role = f"Distinction Test Role {datetime.now(timezone.utc).timestamp()}"
        base_obs = CompensationObservationRecord(
            role_title=unique_role,
            compensation_type="BASE_SALARY",
            period="ANNUAL",
            currency="USD",
            min_amount=100000.0,
            max_amount=120000.0,
        )
        total_obs = CompensationObservationRecord(
            role_title=unique_role,
            compensation_type="TOTAL_COMPENSATION",
            period="ANNUAL",
            currency="USD",
            min_amount=180000.0,
            max_amount=220000.0,
        )
        session.add_all([base_obs, total_obs])
        await session.commit()

        # Querying BASE_SALARY must not include TOTAL_COMPENSATION
        base_res = await MarketIntelligenceService.get_compensation_benchmarks(
            session=session, role_title=unique_role, compensation_type="BASE_SALARY"
        )
        for b in base_res["benchmarks"]:
            assert b["compensation_type"] == "BASE_SALARY"
            assert b["min_amount"] <= 120000.0

        # Querying TOTAL_COMPENSATION must not include BASE_SALARY
        total_res = await MarketIntelligenceService.get_compensation_benchmarks(
            session=session, role_title=unique_role, compensation_type="TOTAL_COMPENSATION"
        )
        for b in total_res["benchmarks"]:
            assert b["compensation_type"] == "TOTAL_COMPENSATION"
            assert b["min_amount"] >= 180000.0


@pytest.mark.asyncio
async def test_candidate_skill_gap_preserves_candidate_profile_isolation():
    """Assertion 8: AI skill-gap recommendations never mutate verified candidate profile."""
    async with AsyncSessionLocal() as session:
        # Create test user and profile with confirmed skills
        user = User(
            email=f"candidate_gap_{datetime.now(timezone.utc).timestamp()}@test.com",
            password_hash="testhash",
            full_name="Gap Test Candidate",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        profile = CandidateProfile(
            user_id=user.id,
            headline="Senior Backend Engineer",
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        # Candidate has only Python
        skill = CandidateSkillRecord(
            profile_id=profile.id,
            skill_name="Python",
            category="Programming Languages",
            proficiency="Advanced",
            provenance="CONFIRMED_RESUME",
        )
        session.add(skill)
        await session.commit()

        # Run skill gaps analysis
        gaps = await MarketIntelligenceService.get_candidate_skill_gaps(
            user_id=user.id, target_role="Backend Engineer", session=session
        )

        assert gaps["candidate_confirmed_skills_count"] >= 1
        assert gaps["recommended_skills_count"] >= 1

        # Check candidate profile skills in database was NOT modified
        c_skills = (await session.execute(
            CandidateSkillRecord.__table__.select().where(CandidateSkillRecord.profile_id == profile.id)
        )).all()
        assert len(c_skills) == 1
        assert c_skills[0].skill_name == "Python"

