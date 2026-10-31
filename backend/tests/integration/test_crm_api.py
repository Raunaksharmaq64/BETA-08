"""
Integration Tests: Application CRM Lifecycle, Status Transitions & Notes
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "crm.cand@example.com") -> dict:
    """Registers and authenticates a test candidate."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "CRM Test Candidate",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_crm_application_crud_and_status_transitions():
    """Verify application creation, state progression, and link tracking."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="crm.crud.cand@example.com")

        # 1. Create application
        create_res = await client.post(
            "/api/v1/applications",
            headers=headers,
            json={
                "company_name": "Acme Distributed Labs",
                "job_title": "Staff Infrastructure Engineer",
                "application_url": "https://acme.careers/jobs/staff-infra",
                "status": "SAVED",
            },
        )
        assert create_res.status_code == 201, create_res.text
        app_data = create_res.json()["data"]
        app_id = app_data["id"]
        assert app_data["status"] == "SAVED"
        assert app_data["company_name"] == "Acme Distributed Labs"

        # 2. Get stats
        stats_res = await client.get("/api/v1/applications/stats", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()["data"]
        assert stats["total_applications"] >= 1

        # 3. Open apply link (tracks timestamp, transitions SAVED -> PLANNING_TO_APPLY)
        open_res = await client.post(
            f"/api/v1/applications/{app_id}/apply-link-opened",
            headers=headers,
        )
        assert open_res.status_code == 200
        opened_data = open_res.json()["data"]
        assert opened_data["status"] == "PLANNING_TO_APPLY"
        assert opened_data["apply_link_opened_at"] is not None
        # Does NOT set APPLIED
        assert opened_data["status"] != "APPLIED"

        # 4. Attempt unconfirmed APPLIED transition -> fails with 400
        fail_res = await client.post(
            f"/api/v1/applications/{app_id}/transition",
            headers=headers,
            json={"to_status": "APPLIED", "confirm_submission": False},
        )
        assert fail_res.status_code == 400

        # 5. Transition to APPLIED with explicit confirmation
        apply_res = await client.post(
            f"/api/v1/applications/{app_id}/transition",
            headers=headers,
            json={
                "to_status": "APPLIED",
                "reason": "Submitted resume and answers on portal",
                "confirm_submission": True,
            },
        )
        assert apply_res.status_code == 200
        applied_data = apply_res.json()["data"]
        assert applied_data["status"] == "APPLIED"
        assert applied_data["is_submission_confirmed"] is True
        assert applied_data["applied_at"] is not None

        # 6. Add candidate private note
        note_res = await client.post(
            f"/api/v1/applications/{app_id}/notes",
            headers=headers,
            json={
                "content": "Recruiter mentioned salary band is $190k-$220k.",
                "note_type": "GENERAL",
            },
        )
        assert note_res.status_code == 201
        note_data = note_res.json()["data"]
        note_id = note_data["id"]

        # 7. Get application details including audit history & notes
        detail_res = await client.get(f"/api/v1/applications/{app_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()["data"]
        assert len(detail["recent_notes"]) >= 1
        assert len(detail["status_history"]) >= 2

        # 8. Delete candidate note
        del_note_res = await client.delete(
            f"/api/v1/applications/notes/{note_id}",
            headers=headers,
        )
        assert del_note_res.status_code == 200
