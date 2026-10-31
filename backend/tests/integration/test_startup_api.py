"""
Integration Tests: Startup Opportunity Discovery, Detail, Save & Unsave
Phase: 10 — Startup Intelligence Integration
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.main import app
from app.services.startup_service import StartupService


async def get_test_auth_headers(client: AsyncClient, email: str = "startup_tester@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Startup Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_and_filter_startup_opportunities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="startup_list@test.com")

        # Seed test opportunities via StartupService
        async with AsyncSessionLocal() as session:
            await StartupService.import_startup_leads(
                [
                    {
                        "id": "test-opp-01",
                        "startup_name": "CloudPulse",
                        "url": "https://cloudpulse.io",
                        "category": "Performance",
                        "detected_signal": "Site latency spikes causing customer churn",
                        "score": 9,
                        "source": "Reddit RSS (/r/saas)",
                    },
                    {
                        "id": "test-opp-02",
                        "startup_name": "DataBridge AI",
                        "url": "https://databridge.ai",
                        "category": "AI",
                        "detected_signal": "Need help implementing vector index caching",
                        "score": 8,
                        "source": "Hacker News (Show HN)",
                    },
                ],
                session,
            )

        # 1. List all
        res = await client.get("/api/v1/startups", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) >= 2

        # 2. Filter by category
        res_cat = await client.get("/api/v1/startups?category=Performance", headers=headers)
        assert res_cat.status_code == 200
        items = res_cat.json()["data"]
        assert len(items) >= 1
        assert all(item["category"] == "Performance" for item in items)


@pytest.mark.asyncio
async def test_startup_detail_and_bookmarking_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="startup_bookmark@test.com")

        # Seed single opportunity
        async with AsyncSessionLocal() as session:
            import_res = await StartupService.import_startup_leads(
                [
                    {
                        "id": "test-opp-03",
                        "startup_name": "VectorOps",
                        "url": "https://vectorops.dev",
                        "category": "Development",
                        "detected_signal": "Kubernetes pod memory limits exceeded on ingest",
                        "score": 8,
                        "source": "GitHub",
                    }
                ],
                session,
            )

        # Retrieve list to get assigned ID
        res_list = await client.get("/api/v1/startups?search=VectorOps", headers=headers)
        opp_id = res_list.json()["data"][0]["id"]

        # 1. Get Detail
        res_detail = await client.get(f"/api/v1/startups/{opp_id}", headers=headers)
        assert res_detail.status_code == 200
        detail_data = res_detail.json()["data"]
        assert detail_data["opportunity"]["startup_name"] == "VectorOps"
        assert len(detail_data["evidence_ledger"]) >= 1
        assert "disclaimer" in detail_data["ai_summary"]

        # 2. Save / Bookmark
        res_save = await client.post(f"/api/v1/startups/{opp_id}/save", json={"notes": "Priority follow-up"}, headers=headers)
        assert res_save.status_code == 200

        # 3. List Saved
        res_saved_all = await client.get("/api/v1/startups/saved/all", headers=headers)
        assert res_saved_all.status_code == 200
        saved_items = res_saved_all.json()["data"]
        assert any(item["opportunity"]["id"] == opp_id for item in saved_items)

        # 4. Unsave
        res_unsave = await client.delete(f"/api/v1/startups/{opp_id}/save", headers=headers)
        assert res_unsave.status_code == 200

