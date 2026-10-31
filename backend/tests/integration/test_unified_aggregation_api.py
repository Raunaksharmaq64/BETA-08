"""
Integration Tests: Unified Opportunities Aggregation, Polymorphic Save & Candidate Feedback
Phase: 11 — Unified Opportunities Engine and Dashboard
"""

import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "aggregation_tester@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Aggregation Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_unified_aggregation_feed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email=f"agg_feed_{int(datetime.now(timezone.utc).timestamp())}@test.com")

        # 1. Fetch ALL opportunities
        res = await client.get("/api/v1/opportunities/all?type=ALL", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert "counts_by_type" in body
        assert "service_availability" in body
        assert body["service_availability"]["core"] == "AVAILABLE"

        # Verify envelope structure on items
        for item in body["data"][:5]:
            assert "schema_version" in item
            assert "opportunity_id" in item
            assert "opportunity_type" in item
            assert item["opportunity_type"] in ("JOB", "FREELANCE", "STARTUP_PAIN_POINT")
            assert "type_specific_payload" in item

        # 2. Filter by JOB
        res_job = await client.get("/api/v1/opportunities/all?type=JOB", headers=headers)
        assert res_job.status_code == 200
        job_data = res_job.json()["data"]
        for item in job_data:
            assert item["opportunity_type"] == "JOB"

        # 3. Filter by FREELANCE
        res_fl = await client.get("/api/v1/opportunities/all?type=FREELANCE", headers=headers)
        assert res_fl.status_code == 200
        fl_data = res_fl.json()["data"]
        for item in fl_data:
            assert item["opportunity_type"] == "FREELANCE"

        # 4. Filter by STARTUP_PAIN_POINT
        res_su = await client.get("/api/v1/opportunities/all?type=STARTUP_PAIN_POINT", headers=headers)
        assert res_su.status_code == 200
        su_data = res_su.json()["data"]
        for item in su_data:
            assert item["opportunity_type"] == "STARTUP_PAIN_POINT"


@pytest.mark.asyncio
async def test_polymorphic_save_and_feedback_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email=f"poly_api_{int(datetime.now(timezone.utc).timestamp())}@test.com")

        # 1. Save an opportunity
        save_res = await client.post(
            "/api/v1/opportunities/JOB/test-job-poly-1/save",
            json={"notes": "Bookmark for review"},
            headers=headers,
        )
        assert save_res.status_code == 200
        assert save_res.json()["success"] is True

        # 2. Retrieve all saved
        saved_list_res = await client.get("/api/v1/opportunities/saved/all", headers=headers)
        assert saved_list_res.status_code == 200
        assert saved_list_res.json()["success"] is True

        # 3. Submit candidate feedback
        feedback_res = await client.post(
            "/api/v1/opportunities/JOB/test-job-poly-1/feedback",
            json={"feedback_category": "IRRELEVANT", "explanation": "Not my tech stack"},
            headers=headers,
        )
        assert feedback_res.status_code == 200
        assert feedback_res.json()["success"] is True
        assert feedback_res.json()["data"]["feedback_category"] == "IRRELEVANT"

        # 4. Remove bookmark
        unsave_res = await client.delete(
            "/api/v1/opportunities/JOB/test-job-poly-1/save",
            headers=headers,
        )
        assert unsave_res.status_code == 200
        assert unsave_res.json()["success"] is True

