"""
Security & Authorization Tests: Tenant & User Isolation, IDOR Prevention, Token Security
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update

from app.core.database import AsyncSessionLocal, init_db
from app.db.models import SecurityAuditEventRecord, User
from app.main import app
from app.services.rate_limiter import rate_limiter
from contracts.auth.schemas import AccountStatus





async def register_user(client: AsyncClient, email: str, name: str) -> str:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": name,
    })
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_cross_user_isolation_profile_and_preferences():
    """Verifies that User A and User B cannot read or modify each other's resources."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token_a = await register_user(client, "alice@example.com", "Alice Smith")
        token_b = await register_user(client, "bob@example.com", "Bob Jones")

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 1. User A sets a specific headline
        await client.put("/api/v1/candidate/profile", json={"headline": "Alice Headline"}, headers=headers_a)

        # 2. User B sets a different headline
        await client.put("/api/v1/candidate/profile", json={"headline": "Bob Headline"}, headers=headers_b)

        # 3. User A querying profile receives ONLY Alice's profile
        resp_a = await client.get("/api/v1/candidate/profile", headers=headers_a)
        assert resp_a.json()["data"]["headline"] == "Alice Headline"

        # 4. User B querying profile receives ONLY Bob's profile
        resp_b = await client.get("/api/v1/candidate/profile", headers=headers_b)
        assert resp_b.json()["data"]["headline"] == "Bob Headline"


@pytest.mark.asyncio
async def test_idor_prevention_on_sub_resources():
    """Verifies that User A cannot delete an education entry created by User B."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token_a = await register_user(client, "user_a@example.com", "User A")
        token_b = await register_user(client, "user_b@example.com", "User B")

        # User B adds an education entry
        add_resp = await client.post(
            "/api/v1/candidate/education",
            json={
                "institution": "MIT",
                "degree": "MS",
                "field_of_study": "AI",
            },
            headers={"Authorization": f"Bearer {token_b}"},
        )
        bob_edu_id = add_resp.json()["data"]["id"]

        # User A attempts to delete User B's education record
        idor_del = await client.delete(
            f"/api/v1/candidate/education/{bob_edu_id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        # Must fail with 404 Not Found (ownership check hides or blocks existence)
        assert idor_del.status_code == 404
        assert "not owned" in idor_del.json()["error"]["message"].lower() or "not found" in idor_del.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_idor_prevention_on_data_export_download():
    """Verifies that User A cannot download User B's data export archive."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token_a = await register_user(client, "requester_a@example.com", "Requester A")
        token_b = await register_user(client, "victim_b@example.com", "Victim B")

        # User B requests an export
        exp_resp = await client.post(
            "/api/v1/candidate/data-export",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        bob_export_id = exp_resp.json()["data"]["export_id"]

        # User A attempts to download User B's export
        unauth_down = await client.get(
            f"/api/v1/candidate/data-export/{bob_export_id}/download",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert unauth_down.status_code == 404
        assert unauth_down.json()["success"] is False


@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected():
    """Verifies that unauthenticated requests to protected endpoints return 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        protected_endpoints = [
            ("/api/v1/auth/me", "get"),
            ("/api/v1/candidate/profile", "get"),
            ("/api/v1/candidate/preferences", "get"),
            ("/api/v1/candidate/privacy", "get"),
            ("/api/v1/candidate/data-export", "post"),
            ("/api/v1/candidate/account-deletion", "post"),
        ]
        for url, method in protected_endpoints:
            if method == "get":
                resp = await client.get(url)
            else:
                resp = await client.post(url, json={})
            assert resp.status_code == 401
            assert resp.json()["success"] is False
            assert resp.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.asyncio
async def test_suspended_user_is_forbidden():
    """Verifies that suspended users are blocked with HTTP 403."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_user(client, "suspended@example.com", "Suspended User")

        # Mark user SUSPENDED in database
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(User)
                .where(User.email == "suspended@example.com")
                .values(status=AccountStatus.SUSPENDED.value)
            )
            await db.commit()

        resp = await client.get("/api/v1/candidate/profile", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "suspended" in resp.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_audit_log_excludes_sensitive_credentials():
    """Verifies that security audit event details never persist plain text passwords or tokens."""
    async with AsyncSessionLocal() as db:
        query = select(SecurityAuditEventRecord).order_by(SecurityAuditEventRecord.timestamp.desc())
        res = await db.execute(query)
        events = res.scalars().all()

        for ev in events:
            details_str = str(ev.details_json).lower()
            assert "password123" not in details_str
            assert "supersecret" not in details_str
            assert "$argon2id$" not in details_str
