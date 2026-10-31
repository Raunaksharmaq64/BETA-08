"""
Integration Tests: Compensation Benchmarks & Candidate Skill-Gap APIs
Phase: 12 — Market & Compensation Intelligence
"""

import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "market_tester@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Market Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_compensation_benchmarks_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Base salary benchmarks
        res = await client.get("/api/v1/market/compensation?compensation_type=BASE_SALARY")
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["compensation_type"] == "BASE_SALARY"
        assert "benchmarks" in body["data"]

        # 2. Invalid compensation type
        res_inv = await client.get("/api/v1/market/compensation?compensation_type=INVALID_TYPE")
        assert res_inv.status_code == 400


@pytest.mark.asyncio
async def test_candidate_skill_gap_workflow_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(
            client, email=f"gap_api_{int(datetime.now(timezone.utc).timestamp())}@test.com"
        )

        # 1. Fetch skill gaps
        res_gaps = await client.get("/api/v1/market/skill-gaps?role=Backend%20Engineer", headers=headers)
        assert res_gaps.status_code == 200
        body_gaps = res_gaps.json()
        assert body_gaps["success"] is True
        assert "target_role" in body_gaps["data"]
        assert "match_rate_pct" in body_gaps["data"]
        assert "missing_skills" in body_gaps["data"]

        missing_list = body_gaps["data"]["missing_skills"]
        if missing_list:
            rec_id = missing_list[0]["recommendation_id"]
            # 2. Update recommendation status to ALREADY_LEARNING
            res_upd = await client.post(
                f"/api/v1/market/skill-gaps/{rec_id}/status",
                json={"status": "ALREADY_LEARNING"},
                headers=headers,
            )
            assert res_upd.status_code == 200
            assert res_upd.json()["data"]["status"] == "ALREADY_LEARNING"

