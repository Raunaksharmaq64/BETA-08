"""
Integration Tests: Outreach Draft, Approval Workflow & Suppression API
Phase: 9 — LeadHunter Integration
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.main import app
from app.services.freelance_service import freelance_service


async def get_test_auth_headers(client: AsyncClient, email: str = "outreach_api_user@test.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Outreach Api Candidate"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_draft_generate_edit_approve_and_send_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="outreach_flow@test.com")

        # 1. Seed opportunity
        async with AsyncSessionLocal() as session:
            opp = await freelance_service.import_lead_as_opportunity(
                session,
                {"name": "Sunset Auto Repair", "city": "Orlando", "email": "contact@sunsetauto.com", "website": None}
            )

        # 2. Generate Draft
        draft_res = await client.post(f"/api/v1/freelance/{opp.id}/draft", headers=headers)
        assert draft_res.status_code == 200
        draft_data = draft_res.json()["data"]
        draft_id = draft_data["id"]
        assert draft_data["status"] == "DRAFT"
        assert draft_data["is_approved"] is False

        # 3. Edit Draft
        edit_res = await client.put(
            f"/api/v1/freelance/drafts/{draft_id}",
            headers=headers,
            json={"subject": "Customized Subject for Sunset Auto", "message_body": "Customized proposal body text."},
        )
        assert edit_res.status_code == 200
        assert edit_res.json()["data"]["status"] == "PENDING_REVIEW"

        # 4. Attempt to send without approval -> MUST be 403 Forbidden
        send_fail = await client.post(f"/api/v1/freelance/drafts/{draft_id}/send", headers=headers)
        assert send_fail.status_code == 403

        # 5. Explicit Approval
        approve_res = await client.post(f"/api/v1/freelance/drafts/{draft_id}/approve", headers=headers)
        assert approve_res.status_code == 200
        assert approve_res.json()["data"]["is_approved"] is True
        assert approve_res.json()["data"]["status"] == "APPROVED"

        # 6. Send message
        send_res = await client.post(f"/api/v1/freelance/drafts/{draft_id}/send", headers=headers)
        assert send_res.status_code == 200
        assert send_res.json()["success"] is True
        assert send_res.json()["data"]["delivery_status"] == "SENT"


@pytest.mark.asyncio
async def test_recipient_suppression_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="suppress_user@test.com")

        res = await client.post(
            "/api/v1/freelance/suppression",
            headers=headers,
            json={"recipient_contact": "unsub_me@domain.com", "reason": "OPT_OUT"},
        )
        assert res.status_code == 200
        assert res.json()["success"] is True
        assert res.json()["data"]["recipient_value"] == "unsub_me@domain.com"
