"""
Unit Tests: Unified Opportunity Service & Common Envelope Normalization
Phase: 11 — Unified Opportunities Engine and Dashboard
"""

import pytest
from datetime import datetime, timezone
from app.db.models import (
    CanonicalOpportunityRecord,
    FreelanceOpportunityRecord,
    StartupOpportunityRecord,
    SavedJobRecord,
    SavedFreelanceOpportunityRecord,
    SavedStartupOpportunityRecord,
    User,
)
from app.core.database import AsyncSessionLocal
from app.services.unified_opportunity_service import UnifiedOpportunityService


@pytest.mark.asyncio
async def test_format_job_envelope():
    job = CanonicalOpportunityRecord(
        id="job-uuid-101",
        source_id="gh-12345",
        external_job_id="gh-101",
        dedup_key_sha256="hash-101",
        title="Senior Python Backend Engineer",
        company_name="Acme Corp",
        description_clean="Build high scale microservices.",
        city="San Francisco",
        country="USA",
        workplace_type="REMOTE",
        min_salary=140000.0,
        max_salary=180000.0,
        currency="USD",
        employment_type="FULL_TIME",
        application_url="https://acme.com/jobs/101",
        verification_status="VERIFIED",
        required_skills_json=["Python", "FastAPI", "PostgreSQL"],
    )

    envelope = UnifiedOpportunityService.format_job_envelope(job, is_saved=True)

    assert envelope["schema_version"] == "1.0"
    assert envelope["opportunity_id"] == "job-uuid-101"
    assert envelope["opportunity_type"] == "JOB"
    assert envelope["title"] == "Senior Python Backend Engineer"
    assert envelope["organization_name"] == "Acme Corp"
    assert envelope["source_service"] == "core"
    assert envelope["is_saved"] is True
    assert envelope["freshness_state"] == "FRESH"
    assert envelope["classification_state"] == "VERIFIED"

    payload = envelope["type_specific_payload"]
    assert payload["employer"] == "Acme Corp"
    assert payload["employment_type"] == "FULL_TIME"
    assert "Python" in payload["required_skills"]
    assert payload["salary_min"] == 140000
    assert payload["fit_score"] == 0.85
    # Enforce rule: No universal trust score merging fit and urgency
    assert "universal_trust_score" not in envelope


@pytest.mark.asyncio
async def test_format_freelance_envelope():
    freelance = FreelanceOpportunityRecord(
        id="freelance-uuid-202",
        leadhunter_lead_id="lh-lead-888",
        business_name="Apex Dental Clinic",
        opportunity_title="Website Performance Optimization",
        service_category="Web Performance",
        classification_state="POTENTIAL_FREELANCE_OPPORTUNITY",
        classification_reason="Slow mobile page load > 4.5s",
        city="Austin, TX",
        website="https://apexdental.example.com",
        phone="+15125550199",
        email="contact@apexdental.example.com",
        rating=4.2,
        reviews_count=48,
        is_broken_website=False,
        suggested_service="Next.js SEO & Speed Audit",
        required_skills="Next.js, Tailwind CSS, Core Web Vitals",
    )

    envelope = UnifiedOpportunityService.format_freelance_envelope(freelance, is_saved=False)

    assert envelope["schema_version"] == "1.0"
    assert envelope["opportunity_id"] == "freelance-uuid-202"
    assert envelope["opportunity_type"] == "FREELANCE"
    assert envelope["organization_name"] == "Apex Dental Clinic"
    assert envelope["source_service"] == "leadhunter"
    assert envelope["is_saved"] is False

    payload = envelope["type_specific_payload"]
    assert payload["client_name"] == "Apex Dental Clinic"
    assert payload["service_category"] == "Web Performance"
    assert "Next.js" in payload["required_skills"]
    assert payload["contact_evidence_status"] == "OBSERVED"
    assert payload["rating"] == 4.2


@pytest.mark.asyncio
async def test_format_startup_envelope():
    startup = StartupOpportunityRecord(
        id="startup-uuid-303",
        service_record_id="startups-prob-77",
        startup_name="OmniFlow Data",
        domain="omniflow.io",
        website_url="https://omniflow.io",
        category="Infrastructure",
        detected_signal="Database query bottlenecks under high ingestion",
        pain_point_description="PostgreSQL deadlocks on time-series telemetry data",
        urgency_score=9,
        score_explanation="Critical production block preventing enterprise rollouts",
        primary_source="Hacker News Ask HN",
        source_url="https://news.ycombinator.com/item?id=77",
        corroboration_count=3,
        has_conflicting_evidence=False,
        ai_insight="Offer managed TimescaleDB migration and index partitioning",
    )

    envelope = UnifiedOpportunityService.format_startup_envelope(startup, is_saved=True)

    assert envelope["schema_version"] == "1.0"
    assert envelope["opportunity_id"] == "startup-uuid-303"
    assert envelope["opportunity_type"] == "STARTUP_PAIN_POINT"
    assert envelope["organization_name"] == "OmniFlow Data"
    assert envelope["source_service"] == "startup_intelligence"
    assert envelope["is_saved"] is True

    payload = envelope["type_specific_payload"]
    assert payload["startup_name"] == "OmniFlow Data"
    assert payload["urgency_score"] == 9
    assert payload["corroboration_count"] == 3
    assert payload["has_conflicting_evidence"] is False


@pytest.mark.asyncio
async def test_polymorphic_save_and_unsave():
    async with AsyncSessionLocal() as session:
        # Create test user
        user = User(
            email=f"polymorphic_{datetime.now(timezone.utc).timestamp()}@test.com",
            password_hash="testhash",
            full_name="Polymorphic Candidate",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # 1. Save Job
        res_job = await UnifiedOpportunityService.save_unified_opportunity(
            user_id=user.id,
            opportunity_type="JOB",
            opportunity_id="sample-job-id-999",
            notes="Interested in backend scale",
            session=session,
        )
        assert res_job["opportunity_type"] == "JOB"
        assert res_job["opportunity_id"] == "sample-job-id-999"

        # 2. Save Freelance
        res_fl = await UnifiedOpportunityService.save_unified_opportunity(
            user_id=user.id,
            opportunity_type="FREELANCE",
            opportunity_id="sample-freelance-id-888",
            notes="Local client website optimization",
            session=session,
        )
        assert res_fl["opportunity_type"] == "FREELANCE"

        # 3. Save Startup
        res_su = await UnifiedOpportunityService.save_unified_opportunity(
            user_id=user.id,
            opportunity_type="STARTUP_PAIN_POINT",
            opportunity_id="sample-startup-id-777",
            notes="High urgency database problem",
            session=session,
        )
        assert res_su["opportunity_type"] == "STARTUP_PAIN_POINT"

        # 4. Unsave each
        assert await UnifiedOpportunityService.unsave_unified_opportunity(
            user_id=user.id, opportunity_type="JOB", opportunity_id="sample-job-id-999", session=session
        ) is True

        assert await UnifiedOpportunityService.unsave_unified_opportunity(
            user_id=user.id, opportunity_type="FREELANCE", opportunity_id="sample-freelance-id-888", session=session
        ) is True

        assert await UnifiedOpportunityService.unsave_unified_opportunity(
            user_id=user.id, opportunity_type="STARTUP_PAIN_POINT", opportunity_id="sample-startup-id-777", session=session
        ) is True
