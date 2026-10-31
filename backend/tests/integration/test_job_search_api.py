"""
Integration Tests: Job Search, Personalized Matching & Saved Features
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.database import AsyncSessionLocal
from app.db.models import CanonicalOpportunityRecord, JobSourceRecord, utc_now


async def get_test_auth_headers(client: AsyncClient, email: str = "search.candidate@example.com") -> dict:
    """Registers and authenticates a test candidate."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Search Test Candidate",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_job_search_endpoint_with_filters_and_coverage():
    """Verify GET /api/v1/search/jobs returns results, pagination, and source coverage metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Search jobs
        res = await client.get("/api/v1/search/jobs?page=1&page_size=10")
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert "items" in data
        assert "total_count" in data
        assert "page" in data
        assert "source_coverage" in data

        coverage = data["source_coverage"]
        assert "total_configured_sources" in coverage
        assert "is_partial_results" in coverage


@pytest.mark.asyncio
async def test_saved_job_lifecycle():
    """Verify candidate saving, reading, updating note, and unsaving a job."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="saved.job.cand@example.com")

        # First find an opportunity ID
        search_res = await client.get("/api/v1/search/jobs?page=1&page_size=5")
        items = search_res.json()["data"]["items"]
        if not items:
            # Seed a dummy opportunity if none exist
            async with AsyncSessionLocal() as session:
                src = JobSourceRecord(
                    source_key="int_test_src",
                    display_name="Integration Test Source",
                    provider="greenhouse",
                    base_url="https://api.test.com",
                )
                session.add(src)
                await session.flush()
                opp = CanonicalOpportunityRecord(
                    source_id=src.id,
                    external_job_id="int-101",
                    dedup_key_sha256="sha-int-101",
                    title="Platform Engineer",
                    company_name="CloudCo",
                    description_clean="Kubernetes and Terraform infrastructure.",
                    application_url="https://cloudco.com/jobs/1",
                    workplace_type="REMOTE",
                    is_remote=True,
                )
                session.add(opp)
                await session.commit()
                opp_id = opp.id
        else:
            opp_id = items[0]["id"]

        # 1. Save Job
        save_res = await client.post(
            "/api/v1/saved-jobs",
            headers=headers,
            json={"opportunity_id": opp_id, "notes": "Interested in infrastructure work"},
        )
        assert save_res.status_code == 201, save_res.text
        saved_id = save_res.json()["data"]["id"]

        # 2. List Saved Jobs
        list_res = await client.get("/api/v1/saved-jobs", headers=headers)
        assert list_res.status_code == 200
        saved_list = list_res.json()["data"]
        assert any(item["opportunity_id"] == opp_id for item in saved_list)

        # 3. Update Notes
        patch_res = await client.patch(
            f"/api/v1/saved-jobs/{saved_id}",
            headers=headers,
            json={"notes": "Updated note: interview scheduled"},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["data"]["notes"] == "Updated note: interview scheduled"

        # 4. Unsave Job
        del_res = await client.delete(f"/api/v1/saved-jobs/{opp_id}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["data"]["success"] is True


@pytest.mark.asyncio
async def test_saved_searches_lifecycle():
    """Verify candidate saving search query, reading, updating frequency, and alert trigger."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="saved.search.cand@example.com")

        # 1. Create Saved Search
        create_res = await client.post(
            "/api/v1/saved-searches",
            headers=headers,
            json={
                "name": "Remote Python Roles",
                "query": "Python",
                "filters": {"is_remote": True},
                "alert_enabled": True,
                "alert_frequency": "DAILY",
            },
        )
        assert create_res.status_code == 201, create_res.text
        search_id = create_res.json()["data"]["id"]

        # 2. List Saved Searches
        list_res = await client.get("/api/v1/saved-searches", headers=headers)
        assert list_res.status_code == 200
        searches = list_res.json()["data"]
        assert any(s["id"] == search_id for s in searches)

        # 3. Patch Alert Cadence
        patch_res = await client.patch(
            f"/api/v1/saved-searches/{search_id}",
            headers=headers,
            json={"alert_frequency": "WEEKLY", "name": "Updated Python Roles"},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["data"]["alert_frequency"] == "WEEKLY"
        assert patch_res.json()["data"]["name"] == "Updated Python Roles"

        # 4. Run Alert Check Worker
        alert_res = await client.post("/api/v1/saved-searches/run-alerts", headers=headers)
        assert alert_res.status_code == 200
        assert isinstance(alert_res.json()["data"], list)

        # 5. Delete Saved Search
        del_res = await client.delete(f"/api/v1/saved-searches/{search_id}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["data"]["success"] is True

