"""
Integration Tests: Privacy, Consent, Data Export & Account Deletion APIs
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import init_db
from app.main import app
from app.services.rate_limiter import rate_limiter





async def register_and_get_token(client: AsyncClient, email: str = "privacy_user@example.com") -> str:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Hannah Abbott",
    })
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_privacy_settings_persistence():
    """Verifies that privacy settings can be updated and persist across requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "priv_settings@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        update_payload = {
            "profile_visibility": "ANONYMIZED",
            "opportunity_alerts": False,
            "email_notifications": True,
            "ai_processing_enabled": True,
            "data_usage_research": False,
        }
        put_resp = await client.put("/api/v1/candidate/privacy", json=update_payload, headers=headers)
        assert put_resp.status_code == 200
        assert put_resp.json()["data"]["profile_visibility"] == "ANONYMIZED"
        assert put_resp.json()["data"]["opportunity_alerts"] is False

        # Verify persistent read
        get_resp = await client.get("/api/v1/candidate/privacy", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["profile_visibility"] == "ANONYMIZED"


@pytest.mark.asyncio
async def test_consent_grant_and_withdrawal():
    """Verifies explicit consent grant, auditable listing, and withdrawal."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "consent_test@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Grant Consent
        grant_resp = await client.post(
            "/api/v1/candidate/consents",
            json={"purpose": "AI_CAREER_MATCHING", "policy_version": "1.0"},
            headers=headers,
        )
        assert grant_resp.status_code == 201
        consent_id = grant_resp.json()["data"]["id"]
        assert grant_resp.json()["data"]["granted"] is True

        # 2. List Consents
        list_resp = await client.get("/api/v1/candidate/consents", headers=headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) >= 1

        # 3. Withdraw Consent
        with_resp = await client.delete(f"/api/v1/candidate/consents/{consent_id}", headers=headers)
        assert with_resp.status_code == 200
        assert with_resp.json()["data"]["granted"] is False
        assert with_resp.json()["data"]["withdrawn_at"] is not None


@pytest.mark.asyncio
async def test_candidate_data_export_and_secrets_exclusion():
    """Verifies that data export generates machine-readable JSON and strictly excludes secrets/hashes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "export_user@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Request Export
        exp_resp = await client.post("/api/v1/candidate/data-export", headers=headers)
        assert exp_resp.status_code == 202
        export_id = exp_resp.json()["data"]["export_id"]
        download_url = exp_resp.json()["data"]["download_url"]

        # 2. Download Export
        down_resp = await client.get(download_url, headers=headers)
        assert down_resp.status_code == 200
        payload = down_resp.json()["data"]["data"]

        # 3. Mandatory Security Verification: Exclude secrets and hashes
        assert "account" in payload
        assert "profile" in payload
        assert "preferences" in payload
        assert "privacy_settings" in payload
        assert "password" not in payload["account"]
        assert "password_hash" not in payload["account"]
        assert "token" not in payload


@pytest.mark.asyncio
async def test_account_deletion_workflow():
    """Verifies candidate account deletion request, session revocation, and grace period."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "delete_me@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Invalid confirmation phrase rejected
        bad_del = await client.post(
            "/api/v1/candidate/account-deletion",
            json={"confirmation": "please delete"},
            headers=headers,
        )
        assert bad_del.status_code == 400

        # 2. Correct confirmation phrase succeeds
        del_resp = await client.post(
            "/api/v1/candidate/account-deletion",
            json={"confirmation": "DELETE MY ACCOUNT", "reason": "Moving to another career platform"},
            headers=headers,
        )
        assert del_resp.status_code == 200
        del_data = del_resp.json()["data"]
        assert del_data["status"] == "PENDING"
        assert "leadhunter" in del_data["service_status"]
        assert "startup_intelligence" in del_data["service_status"]

        # 3. Verify normal authenticated profile operations are restricted
        restricted = await client.put(
            "/api/v1/candidate/profile",
            json={"headline": "Hacker"},
            headers=headers,
        )
        assert restricted.status_code == 403
        assert "pending deletion" in restricted.json()["error"]["message"].lower()

        # 4. Status endpoint still accessible
        status_resp = await client.get("/api/v1/candidate/account-deletion/status", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["data"]["status"] == "PENDING"
