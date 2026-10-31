"""
Integration Tests: Freelance Opportunity Discovery, Detail & Saved Listings
Phase: 9 — LeadHunter Integration
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.main import app
from app.services.freelance_service import freelance_service


async def get_test_auth_headers(client: AsyncClient, email: str = "freelance_user@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Freelance Tester"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_and_filter_freelance_opportunities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="freelance_list@test.com")

        # Seed test opportunities via freelance_service
        async with AsyncSessionLocal() as session:
            await freelance_service.import_lead_as_opportunity(
                session,
                {"name": "Alpha Law Firm", "city": "Chicago", "category": "Legal", "website": None, "is_broken_website": False}
            )
            await freelance_service.import_lead_as_opportunity(
                session,
                {"name": "Beta Dental Care", "city": "Chicago", "category": "Dental", "website": "https://betadental.com", "is_broken_website": True}
            )

        # 1. List all opportunities
        res = await client.get("/api/v1/freelance", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) >= 2

        # 2. Filter by city
        res_city = await client.get("/api/v1/freelance?city=Chicago", headers=headers)
        assert res_city.status_code == 200
        assert all("Chicago" in item["city"] for item in res_city.json()["data"])


@pytest.mark.asyncio
async def test_save_and_retrieve_freelance_opportunity():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="freelance_save@test.com")

        async with AsyncSessionLocal() as session:
            opp = await freelance_service.import_lead_as_opportunity(
                session,
                {"name": "Save Me Spa", "city": "Miami", "website": "https://savemespa.com", "is_broken_website": True}
            )

        # Save opportunity
        save_res = await client.post(
            f"/api/v1/freelance/{opp.id}/save",
            headers=headers,
            json={"notes": "High priority client with broken SSL"},
        )
        assert save_res.status_code == 200
        assert save_res.json()["success"] is True

        # Retrieve saved list
        saved_list_res = await client.get("/api/v1/freelance/saved/all", headers=headers)
        assert saved_list_res.status_code == 200
        saved_items = saved_list_res.json()["data"]
        assert any(item["opportunity_id"] == opp.id for item in saved_items)
