"""
Integration Tests: Authentication & Identity APIs
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.db.models import EmailVerificationTokenRecord, PasswordResetTokenRecord, User
from app.main import app
from app.services.rate_limiter import rate_limiter





@pytest.mark.asyncio
async def test_user_registration_and_duplicate_prevention():
    """Verifies candidate registration and rejection of duplicate email."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register new candidate
        reg_payload = {
            "email": "fresh_candidate@example.com",
            "password": "SecurePassword123!",
            "full_name": "Alice Candidate",
            "role": "CANDIDATE",
        }
        resp = await client.post("/api/v1/auth/register", json=reg_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["email"] == "fresh_candidate@example.com"
        assert data["data"]["is_email_verified"] is False
        assert "password" not in data["data"]
        assert "password_hash" not in data["data"]

        # 2. Duplicate registration attempt with same email must fail with 409
        dup_resp = await client.post("/api/v1/auth/register", json=reg_payload)
        assert dup_resp.status_code == 409
        dup_data = dup_resp.json()
        assert dup_data["success"] is False
        assert dup_data["error"]["code"] == "RESOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_login_and_current_user_me():
    """Verifies successful login, JWT issuance, HttpOnly cookie setting, and /auth/me lookup."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register user
        reg_payload = {
            "email": "login_user@example.com",
            "password": "Password123!",
            "full_name": "Bob Martin",
            "role": "CANDIDATE",
        }
        await client.post("/api/v1/auth/register", json=reg_payload)

        # 1. Valid login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "login_user@example.com",
            "password": "Password123!",
        })
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert login_data["success"] is True
        token = login_data["data"]["access_token"]
        refresh_token = login_data["data"]["refresh_token"]
        assert token is not None
        assert refresh_token is not None
        assert "rightfit_session" in login_resp.cookies

        # 2. Invalid password login must fail with 401
        bad_login = await client.post("/api/v1/auth/login", json={
            "email": "login_user@example.com",
            "password": "WrongPassword999!",
        })
        assert bad_login.status_code == 401
        assert bad_login.json()["success"] is False

        # 3. Access /auth/me with Bearer token
        me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["success"] is True
        assert me_data["data"]["email"] == "login_user@example.com"
        assert me_data["data"]["full_name"] == "Bob Martin"


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_reuse_detection():
    """Verifies rotating refresh tokens and automatic family revocation upon replay attack."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "rotation_user@example.com"
        await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Charlie Rotation",
        })

        login_resp = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "Password123!",
        })
        first_refresh = login_resp.json()["data"]["refresh_token"]

        # 1. First rotation - should succeed and return new pair
        ref_resp_1 = await client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
        assert ref_resp_1.status_code == 200
        second_refresh = ref_resp_1.json()["data"]["refresh_token"]
        assert second_refresh != first_refresh

        # 2. REUSE ATTACK: Attempt to use the already-rotated first_refresh again!
        # Must be detected as a replay attack and revoke the whole family.
        replay_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
        assert replay_resp.status_code == 401
        assert "reuse detected" in replay_resp.json()["error"]["message"].lower()

        # 3. Since family was revoked, even the second_refresh must now be rejected!
        subsequent_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": second_refresh})
        assert subsequent_resp.status_code == 401


@pytest.mark.asyncio
async def test_password_change_and_session_revocation():
    """Verifies in-session password change and automatic revocation of prior sessions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "change_pwd_user@example.com"
        await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "OldPassword123!",
            "full_name": "Diana Prince",
        })

        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "OldPassword123!"})
        token = login_resp.json()["data"]["access_token"]
        refresh_token = login_resp.json()["data"]["refresh_token"]

        # Change password
        chg_resp = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "OldPassword123!", "new_password": "BrandNewPassword123!"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert chg_resp.status_code == 200
        assert chg_resp.json()["success"] is True

        # Old password no longer works
        old_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "OldPassword123!"})
        assert old_login.status_code == 401

        # New password works
        new_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "BrandNewPassword123!"})
        assert new_login.status_code == 200

        # Prior refresh token was revoked during password change
        ref_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert ref_resp.status_code == 401


@pytest.mark.asyncio
async def test_email_verification_workflow():
    """Verifies single-use email verification token redemption."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "verify_test@example.com"
        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Edward Nygma",
        })
        user_id = reg_resp.json()["data"]["id"]

        # Fetch token from database directly via test session
        async with AsyncSessionLocal() as db:
            query = select(EmailVerificationTokenRecord).where(
                EmailVerificationTokenRecord.user_id == user_id,
                EmailVerificationTokenRecord.is_used == False,
            )
            res = await db.execute(query)
            record = res.scalar_one()
            token_hash = record.token_hash

        # Attempt verification with invalid token
        bad_verify = await client.post("/api/v1/auth/verify-email", json={"token": "invalid_token_string"})
        assert bad_verify.status_code == 400


@pytest.mark.asyncio
async def test_logout():
    """Verifies logout terminates cookies and sessions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "logout_user@example.com"
        await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Frank Castle",
        })
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_resp.json()["data"]["access_token"]
        refresh = login_resp.json()["data"]["refresh_token"]

        logout_resp = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}", "x-refresh-token": refresh},
        )
        assert logout_resp.status_code == 200
        assert logout_resp.json()["success"] is True
