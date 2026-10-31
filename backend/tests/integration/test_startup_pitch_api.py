"""
Integration Tests: Startup Pitch Draft Generator and Editing Workflow
Phase: 10 — Startup Intelligence Integration
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.main import app
from app.services.startup_service import StartupService


async def get_test_auth_headers(client: AsyncClient, email: str = "pitch_user@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Pitch Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_startup_pitch_generation_and_edit_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="pitch_lifecycle@test.com")

        # Seed opportunity
        async with AsyncSessionLocal() as session:
            await StartupService.import_startup_leads(
                [
                    {
                        "id": "test-opp-pitch-1",
                        "startup_name": "SpeedScale Inc",
                        "url": "https://speedscale.io",
                        "category": "Performance",
                        "detected_signal": "Need React and Next.js performance optimization",
                        "score": 9,
                        "source": "Reddit RSS (/r/startups)",
                    }
                ],
                session,
            )

        # Get opp ID
        res_list = await client.get("/api/v1/startups?search=SpeedScale", headers=headers)
        opp_id = res_list.json()["data"][0]["id"]

        # 1. Generate Pitch Draft
        res_pitch = await client.post(
            f"/api/v1/startups/{opp_id}/pitch",
            json={"tone": "casual"},
            headers=headers,
        )
        assert res_pitch.status_code == 200
        draft_data = res_pitch.json()["data"]
        assert draft_data["opportunity_id"] == opp_id
        assert "SpeedScale" in draft_data["subject"]
        assert "explicit_assumptions" in draft_data
        draft_id = draft_data["id"]

        # 2. Edit Pitch Draft
        res_edit = await client.put(
            f"/api/v1/startups/pitches/{draft_id}",
            json={"subject": "Customized Subject Line", "body": "Customized pitch text.", "tone": "formal"},
            headers=headers,
        )
        assert res_edit.status_code == 200
        updated_data = res_edit.json()["data"]
        assert updated_data["subject"] == "Customized Subject Line"
        assert updated_data["candidate_edits_count"] == 1

