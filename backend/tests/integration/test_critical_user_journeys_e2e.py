"""
Integration & End-to-End Test Suite for Phase 14: Critical User Journeys (A through H)
Validates complete user workflows across the unified platform.
"""

import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import AsyncSessionLocal
from app.services.market_intelligence_service import MarketIntelligenceService
from app.services.beta_validation_service import BetaValidationService


async def get_test_auth_headers(client: AsyncClient, email: str = "journey_tester@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Journey Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_critical_journey_a_account_and_health():
    """Journey A: System health, registration endpoint, and liveness."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Liveness & Readiness
        res_live = await client.get("/health/live")
        assert res_live.status_code == 200
        assert res_live.json()["status"] == "healthy"

        res_ready = await client.get("/health/ready")
        assert res_ready.status_code == 200


@pytest.mark.asyncio
async def test_critical_journey_c_and_g_job_search_and_unified_dashboard():
    """Journey C & G: Job search, unified opportunities aggregation, and dashboard metrics."""
    async with AsyncSessionLocal() as session:
        await MarketIntelligenceService.ensure_baseline_seeded(session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        email = f"journey_cg_{int(datetime.now(timezone.utc).timestamp())}@test.com"
        headers = await get_test_auth_headers(client, email=email)

        # Unified Dashboard with Auth
        dash_res = await client.get("/api/v1/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["success"] is True
        assert "summary_metrics" in dash_data["data"]

        # Unified Opportunities Pipeline Feed
        opp_res = await client.get("/api/v1/opportunities/all?limit=10", headers=headers)
        assert opp_res.status_code == 200
        opp_data = opp_res.json()
        assert opp_data["success"] is True
        assert isinstance(opp_data["data"], list)


@pytest.mark.asyncio
async def test_critical_journey_e_and_f_freelance_and_startups():
    """Journey E & F: Freelance opportunities (LeadHunter) and Startup Intelligence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        email = f"journey_ef_{int(datetime.now(timezone.utc).timestamp())}@test.com"
        headers = await get_test_auth_headers(client, email=email)

        # Freelance discovery with Auth
        fl_res = await client.get("/api/v1/freelance?limit=5", headers=headers)
        assert fl_res.status_code == 200
        assert fl_res.json()["success"] is True

        # Startup discovery with Auth
        st_res = await client.get("/api/v1/startups?limit=5", headers=headers)
        assert st_res.status_code == 200
        assert st_res.json()["success"] is True


@pytest.mark.asyncio
async def test_critical_journey_h_market_and_beta_feedback():
    """Journey H: Market intelligence, canonical taxonomy, and user feedback intake."""
    async with AsyncSessionLocal() as session:
        await MarketIntelligenceService.ensure_baseline_seeded(session)
        await BetaValidationService.ensure_baseline_seeded(session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Market Demand
        demand_res = await client.get("/api/v1/market/demand/skills?time_window=30d")
        assert demand_res.status_code == 200
        assert demand_res.json()["success"] is True

        # Beta Feedback Submission
        fb_payload = {
            "category": "ACCESSIBILITY",
            "description": "High contrast mode works well on dark slate, but font size on skill tag could be 1px larger.",
            "related_feature": "MARKET_INTELLIGENCE",
            "severity": "LOW",
        }
        fb_res = await client.post("/api/v1/beta/feedback", json=fb_payload)
        assert fb_res.status_code == 201
        assert fb_res.json()["success"] is True
        assert fb_res.json()["data"]["category"] == "ACCESSIBILITY"
