"""
Integration Tests: Reminders, Calendar & Notifications API
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from httpx import ASGITransport, AsyncClient

from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "rem.notif.cand@example.com") -> dict:
    """Registers and authenticates a test candidate."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Reminders Candidate",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_reminders_and_calendar_api():
    """Verify reminder CRUD and aggregated calendar in candidate timezone."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="rem.cand.api@example.com")

        now_utc = datetime.now(timezone.utc)
        due_utc = (now_utc + timedelta(days=2)).isoformat()

        # 1. Create reminder
        create_res = await client.post(
            "/api/v1/reminders",
            headers=headers,
            json={
                "title": "Send thank-you email to hiring manager",
                "due_at_utc": due_utc,
                "timezone": "Asia/Kolkata",
                "reminder_type": "FOLLOW_UP",
            },
        )
        assert create_res.status_code == 201, create_res.text
        rem_data = create_res.json()["data"]
        rem_id = rem_data["id"]

        # 2. Get reminders list
        list_res = await client.get("/api/v1/reminders", headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.json()["data"]) >= 1

        # 3. Get calendar with timezone conversion
        cal_res = await client.get(
            "/api/v1/calendar/events?tz=Asia/Kolkata",
            headers=headers,
        )
        assert cal_res.status_code == 200
        cal_events = cal_res.json()["data"]
        assert len(cal_events) >= 1
        assert any(e["id"] == f"rem_{rem_id}" for e in cal_events)

        # 4. Check conflicts
        time_param = (now_utc + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        conflict_res = await client.get(
            f"/api/v1/calendar/conflicts?time={time_param}&duration_minutes=30",
            headers=headers,
        )
        assert conflict_res.status_code == 200

        # 5. Toggle complete
        patch_res = await client.patch(
            f"/api/v1/reminders/{rem_id}/complete",
            headers=headers,
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["data"]["is_completed"] is True

        # 6. Delete reminder
        del_res = await client.delete(f"/api/v1/reminders/{rem_id}", headers=headers)
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_notifications_and_preferences_api():
    """Verify notifications list, read status, and preferences updates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="notif.cand.api@example.com")

        # 1. Get default preferences
        pref_res = await client.get("/api/v1/notifications/preferences", headers=headers)
        assert pref_res.status_code == 200
        prefs = pref_res.json()["data"]
        assert prefs["in_app_enabled"] is True

        # 2. Update preferences
        update_pref_res = await client.patch(
            "/api/v1/notifications/preferences",
            headers=headers,
            json={
                "in_app_enabled": True,
                "email_enabled": True,
                "interview_reminders": False,
                "application_follow_ups": True,
                "assessment_deadlines": True,
                "prep_milestones": True,
            },
        )
        assert update_pref_res.status_code == 200
        assert update_pref_res.json()["data"]["interview_reminders"] is False

        # 3. Read notifications list
        notifs_res = await client.get("/api/v1/notifications", headers=headers)
        assert notifs_res.status_code == 200

        # 4. Mark all read
        read_all_res = await client.post("/api/v1/notifications/mark-all-read", headers=headers)
        assert read_all_res.status_code == 200
