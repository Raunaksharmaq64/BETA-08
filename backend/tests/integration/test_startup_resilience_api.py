"""
Integration Tests: Startup Intelligence Degraded Mode & Resilience
Phase: 10 — Startup Intelligence Integration
"""

from __future__ import annotations

from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient

from app.integrations.startup_intelligence.adapter import StartupIntelligenceUnavailableError
from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "resilience_user@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Resilience Tester"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_degraded_service_mode_when_startup_intelligence_is_offline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="startup_offline@test.com")

        # Mock adapter throwing StartupIntelligenceUnavailableError
        with patch(
            "app.api.v1.endpoints.startups.startup_adapter.list_leads",
            side_effect=StartupIntelligenceUnavailableError("Service connection refused at http://localhost:8002"),
        ):
            res = await client.post(
                "/api/v1/startups/scan-leads",
                json={"category": "Performance"},
                headers=headers,
            )
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["degraded"] is True
            assert "offline or unreachable" in data["message"]

