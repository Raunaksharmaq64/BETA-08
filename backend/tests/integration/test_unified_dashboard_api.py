"""
Integration Tests: Unified Dashboard API & Metric Reconciliation
Phase: 11 — Unified Opportunities Engine and Dashboard
"""

import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "dashboard_tester@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Dashboard Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_unified_dashboard_metrics_reconciliation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email=f"dash_rec_{int(datetime.now(timezone.utc).timestamp())}@test.com")

        res = await client.get("/api/v1/dashboard", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True

        metrics = body["data"]["summary_metrics"]
        # Mandatory count reconciliation rule:
        # total_opportunities MUST equal sum of individual modules
        assert metrics["total_opportunities"] == (
            metrics["total_jobs"] + metrics["total_freelance"] + metrics["total_startups"]
        )

        assert metrics["total_jobs"] >= 0
        assert metrics["total_freelance"] >= 0
        assert metrics["total_startups"] >= 0
        assert metrics["total_saved"] >= 0
        assert metrics["active_applications"] >= 0

        # Source health
        health = body["data"]["source_health"]
        assert "core_career_engine" in health
        assert "leadhunter_satellite" in health
        assert "startup_intelligence_satellite" in health
        assert health["core_career_engine"] == "HEALTHY"

        # Recent opportunities list
        assert isinstance(body["data"]["recent_opportunities"], list)


@pytest.mark.asyncio
async def test_dashboard_unauthenticated_still_returns_reconciled_totals():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/dashboard")
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        metrics = body["data"]["summary_metrics"]
        assert metrics["total_opportunities"] == (
            metrics["total_jobs"] + metrics["total_freelance"] + metrics["total_startups"]
        )

