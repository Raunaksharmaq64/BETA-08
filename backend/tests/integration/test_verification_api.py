"""
Integration Tests: Verification, Deduplication, Quality & Feedback REST APIs
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.models import (
    CanonicalOpportunityRecord,
    JobSourceRecord,
    OpportunitySourceMappingRecord,
    utc_now,
)
from app.core.database import AsyncSessionLocal


async def get_auth_headers(client: AsyncClient, email: str = "verif.admin@example.com") -> dict:
    """Helper to register and login an admin user."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Verification Admin",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_quality_metrics_endpoint():
    """Verify GET /api/v1/quality/metrics returns 200 with valid KPI structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/quality/metrics")
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert "freshness_rate" in data
        assert "verification_coverage" in data
        assert "confirmed_open_rate" in data
        assert "link_unavailable_rate" in data
        assert "source_breakdown" in data


@pytest.mark.asyncio
async def test_verification_and_feedback_lifecycle():
    """Validates verification timeline query, trigger, and candidate feedback endpoints."""
    # Seed database with test source and opportunity
    async with AsyncSessionLocal() as session:
        source = JobSourceRecord(
            source_key="test-api-board",
            display_name="Test Board",
            source_type="ATS_JOB_BOARD",
            provider="synthetic",
            base_url="https://jobs.example.com",
            policy_status="ACTIVE",
        )
        session.add(source)
        await session.flush()

        opp = CanonicalOpportunityRecord(
            source_id=source.id,
            external_job_id="test-job-101",
            dedup_key_sha256="test_sha_101",
            title="Senior Backend Systems Engineer",
            company_name="Vercel",
            description_clean="Clean job description text",
            application_url="https://jobs.example.com/101",
            verification_status="UNVERIFIED",
            freshness_state="UNKNOWN",
            is_suppressed=False,
            is_active=True,
            first_seen_at=utc_now(),
            last_seen_at=utc_now(),
        )
        session.add(opp)
        await session.flush()

        mapping = OpportunitySourceMappingRecord(
            canonical_opportunity_id=opp.id,
            source_id=source.id,
            external_job_id="test-job-101",
            original_url="https://jobs.example.com/101",
            mapping_status="ACTIVE",
            match_tier="TIER_1_EXACT",
            match_method="EXACT_SOURCE_ID",
            confidence_score=1.0,
        )
        session.add(mapping)
        await session.commit()
        opp_id = opp.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Query Verification Details
        v_res = await client.get(f"/api/v1/opportunities/{opp_id}/verification")
        assert v_res.status_code == 200, v_res.text
        v_data = v_res.json()["data"]
        assert v_data["opportunity_id"] == opp_id
        assert v_data["verification_status"] == "UNVERIFIED"
        assert "evidence_history" in v_data

        # 2. Query Source Mappings
        m_res = await client.get(f"/api/v1/opportunities/{opp_id}/mappings")
        assert m_res.status_code == 200, m_res.text
        m_data = m_res.json()["data"]
        assert len(m_data) == 1
        assert m_data[0]["external_job_id"] == "test-job-101"

        # 3. Submit User Feedback
        fb_res = await client.post(
            f"/api/v1/opportunities/{opp_id}/feedback",
            json={
                "feedback_type": "BROKEN_LINK",
                "notes": "Page returns 404 when clicking apply link.",
            },
        )
        assert fb_res.status_code == 201, fb_res.text
        fb_data = fb_res.json()["data"]
        assert fb_data["opportunity_id"] == opp_id
        assert fb_data["feedback_type"] == "BROKEN_LINK"

        # 4. List Feedback for Opportunity
        list_fb = await client.get(f"/api/v1/opportunities/{opp_id}/feedback")
        assert list_fb.status_code == 200
        assert len(list_fb.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_deduplication_merge_unmerge_and_suppression():
    """Validates duplicate merge, suppression from search discovery, and unmerge reversibility."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_auth_headers(client, email="merge.admin@example.com")

        # Seed two opportunities: primary and duplicate
        async with AsyncSessionLocal() as session:
            source = JobSourceRecord(
                source_key="dedup-board",
                display_name="Dedup Board",
                source_type="ATS_JOB_BOARD",
                provider="synthetic",
                base_url="https://dedup.example.com",
                policy_status="ACTIVE",
            )
            session.add(source)
            await session.flush()

            primary = CanonicalOpportunityRecord(
                source_id=source.id,
                external_job_id="dedup-prim-1",
                dedup_key_sha256="hash_prim_1",
                title="Lead Security Architect",
                company_name="Cloudflare",
                description_clean="Desc",
                application_url="https://cloudflare.com/jobs/prim1",
                is_suppressed=False,
                is_active=True,
                first_seen_at=utc_now(),
                last_seen_at=utc_now(),
            )
            duplicate = CanonicalOpportunityRecord(
                source_id=source.id,
                external_job_id="dedup-dup-1",
                dedup_key_sha256="hash_dup_1",
                title="Lead Security Architect - Enterprise",
                company_name="Cloudflare",
                description_clean="Desc",
                application_url="https://cloudflare.com/jobs/dup1",
                is_suppressed=False,
                is_active=True,
                first_seen_at=utc_now(),
                last_seen_at=utc_now(),
            )
            session.add_all([primary, duplicate])
            await session.flush()

            mapping = OpportunitySourceMappingRecord(
                canonical_opportunity_id=duplicate.id,
                source_id=source.id,
                external_job_id="dedup-dup-1",
                original_url="https://cloudflare.com/jobs/dup1",
                mapping_status="ACTIVE",
                match_tier="TIER_1_EXACT",
                match_method="EXACT_SOURCE_ID",
                confidence_score=1.0,
            )
            session.add(mapping)
            await session.commit()
            prim_id = primary.id
            dup_id = duplicate.id

        # 1. Both should appear in search opportunities initially
        search1 = await client.get("/api/v1/opportunities?search=Security")
        ids1 = [item["id"] for item in search1.json()["data"]]
        assert prim_id in ids1
        assert dup_id in ids1

        # 2. Merge duplicate into primary
        merge_res = await client.post(
            "/api/v1/duplicates/merge",
            headers=headers,
            json={
                "primary_id": prim_id,
                "duplicate_ids": [dup_id],
                "reason": "Admin verified identical requisition across sources",
            },
        )
        assert merge_res.status_code == 200, merge_res.text
        decision_id = merge_res.json()["data"]["decision_id"]

        # 3. Duplicate must now be SUPPRESSED from default candidate discovery!
        search2 = await client.get("/api/v1/opportunities?search=Security")
        ids2 = [item["id"] for item in search2.json()["data"]]
        assert prim_id in ids2
        assert dup_id not in ids2  # SUPPRESSED!

        # 4. Unmerge decision and reverse suppression
        unmerge_res = await client.post(
            f"/api/v1/duplicates/{decision_id}/unmerge",
            headers=headers,
            json={"decision_id": decision_id, "reason": "Unmerging: distinct teams"},
        )
        assert unmerge_res.status_code == 200, unmerge_res.text

        # 5. Duplicate must now be RESTORED to candidate discovery!
        search3 = await client.get("/api/v1/opportunities?search=Security")
        ids3 = [item["id"] for item in search3.json()["data"]]
        assert prim_id in ids3
        assert dup_id in ids3  # RESTORED!

