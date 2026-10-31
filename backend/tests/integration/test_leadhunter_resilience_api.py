"""
Integration Tests: LeadHunter Resilience, Circuit Breaker & Degraded Mode
Phase: 9 — LeadHunter Integration
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.integrations.leadhunter.adapter import leadhunter_adapter
from app.main import app
from app.services.freelance_service import freelance_service


async def get_test_auth_headers(client: AsyncClient, email: str = "resilience_cand@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Resilience Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_degraded_service_mode_when_leadhunter_is_offline():
    """
    Simulates LeadHunter service being offline (or circuit breaker tripped).
    Verifies that the Core API returns degraded=True with local cached records
    and DOES NOT crash or return a 500 error.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="degraded_cand@test.com")

        # Seed at least 1 local opportunity
        async with AsyncSessionLocal() as session:
            await freelance_service.import_lead_as_opportunity(
                session,
                {"name": "Local Safe Plumbers", "city": "Dallas", "website": None}
            )

        # Force adapter to point to an unreachable port
        original_base = leadhunter_adapter.base_url
        try:
            leadhunter_adapter.base_url = "http://127.0.0.1:54321"  # Unreachable

            scan_res = await client.post(
                "/api/v1/freelance/scan-leads",
                headers=headers,
                json={"query": "Plumbers", "city": "Dallas", "max_results": 10},
            )
            assert scan_res.status_code == 200
            data = scan_res.json()
            assert data["success"] is True
            assert data["degraded"] is True
            assert "offline or unreachable" in data["message"]
            assert isinstance(data["data"], list)

            # Check status endpoint
            status_res = await client.get("/api/v1/freelance/integration-status", headers=headers)
            assert status_res.status_code == 200
            status_data = status_res.json()
            assert "circuit_state" in status_data
        finally:
            leadhunter_adapter.base_url = original_base
            leadhunter_adapter.circuit_breaker.record_success()

