"""
RIGHT FIT Core — Continuous Discovery & Live Auto-Refresh Integration Tests
Master Implementation: Connectors, Discovery Lifecycle, REST Controls & Candidate Skill Intelligence
"""

from __future__ import annotations

import time
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.db.models import (
    CandidateSkillRecord,
    DiscoveryScheduleConfigRecord,
    DiscoveryTaskExecutionRecord,
    JobSourceRecord,
    User,
    utc_now,
)
from app.main import app
from app.services.connectors.lever import LeverConnector
from app.services.connectors.remoteok import RemoteOKConnector
from app.workers.tasks.discovery_tasks import _async_run_continuous_discovery
from app.workers.tasks.startup_tasks import (
    _async_run_continuous_startup_discovery,
    _async_run_pain_point_clustering,
)


async def ensure_discovery_configs_seeded():
    """Seeds baseline discovery schedule configs if not already present."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(DiscoveryScheduleConfigRecord))
        existing = res.scalars().all()
        if not existing:
            default_configs = [
                ("greenhouse-ats", "Greenhouse Public ATS", 1800, 50, 30),
                ("lever-ats", "Lever Job Postings", 1800, 50, 30),
                ("ashby-ats", "Ashby Ingestion Engine", 1800, 50, 30),
                ("remoteok-feed", "RemoteOK Job Board Feed", 3600, 50, 20),
                ("leadhunter-satellite", "LeadHunter AI Freelance Adapter", 1800, 40, 20),
                ("startup-hunter-satellite", "Startup Problems Hunter Satellite", 3600, 30, 15),
            ]
            for src_id, name, interval, max_recs, rate_lim in default_configs:
                cfg = DiscoveryScheduleConfigRecord(
                    source_id=src_id,
                    source_name=name,
                    interval_seconds=interval,
                    is_paused=False,
                    max_records_per_run=max_recs,
                    rate_limit_per_minute=rate_lim,
                    last_run_at=utc_now(),
                    next_run_at=utc_now(),
                )
                session.add(cfg)
            await session.commit()


async def get_test_token(client: AsyncClient, email: str = "discovery.test@example.com") -> str:
    """Registers and authenticates a test user, returning access token."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Discovery Test User",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    return login_res.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_lever_and_remoteok_connector_parsing():
    """Verifies that Lever and RemoteOK connectors parse raw API payloads correctly into canonical schemas."""
    # 1. Lever Connector
    lever = LeverConnector()
    lever.validate_config("netflix")
    assert lever.provider_name == "lever"
    assert "api.lever.co" in lever._build_api_url("netflix")

    dummy_source = JobSourceRecord(
        id=str(uuid.uuid4()),
        source_key="lever_test",
        display_name="Lever Test",
        source_type="ATS_JOB_BOARD",
        provider="lever",
        base_url="https://jobs.lever.co/testco",
        rate_limit_per_minute=60,
        timeout_seconds=5.0,
    )

    mock_lever_response = [
        {
            "id": "lever-12345",
            "text": "Senior Distributed Systems Engineer",
            "hostedUrl": "https://jobs.lever.co/testco/lever-12345",
            "createdAt": int(time.time() * 1000),
            "categories": {
                "team": "Infrastructure",
                "location": "San Francisco, CA",
                "commitment": "Full-Time",
            },
            "descriptionPlain": "We are seeking a senior systems engineer experienced in Rust and Kubernetes.",
        }
    ]

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: mock_lever_response
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        fetch_res = await lever.fetch_jobs(dummy_source, limit=10)
        assert fetch_res.total_found == 1
        assert len(fetch_res.records) == 1
        record = fetch_res.records[0]
        assert record.external_job_id == "lever-12345"
        assert record.listing_url == "https://jobs.lever.co/testco/lever-12345"
        assert record.raw_payload["text"] == "Senior Distributed Systems Engineer"

    # 2. RemoteOK Connector
    remoteok = RemoteOKConnector()
    remoteok.validate_config("https://remoteok.com/api")
    assert remoteok.provider_name == "remoteok"

    dummy_ro_source = JobSourceRecord(
        id=str(uuid.uuid4()),
        source_key="remoteok_test",
        display_name="RemoteOK Test",
        source_type="PUBLIC_JOB_FEED",
        provider="remoteok",
        base_url="https://remoteok.com/api",
        rate_limit_per_minute=30,
        timeout_seconds=5.0,
    )

    mock_ro_response = [
        {"legal": "RemoteOK terms"},  # First element disclaimer
        {
            "id": "ro-998811",
            "position": "Lead Python Platform Engineer",
            "url": "https://remoteok.com/remote-jobs/998811",
            "date": "2026-10-30T10:00:00Z",
            "tags": ["python", "fastapi", "postgresql", "docker"],
            "description": "High throughput data platform engineering.",
        },
    ]

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: mock_ro_response
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        ro_res = await remoteok.fetch_jobs(dummy_ro_source, limit=10)
        assert len(ro_res.records) == 1
        assert ro_res.records[0].external_job_id == "ro-998811"
        assert ro_res.records[0].listing_url == "https://remoteok.com/remote-jobs/998811"


@pytest.mark.asyncio
async def test_continuous_discovery_background_execution():
    """Verifies that background execution tasks run and persist execution telemetry in the database."""
    # Run startup continuous discovery
    startup_res = await _async_run_continuous_startup_discovery()
    assert startup_res["status"] == "SUCCESS"
    assert "stats" in startup_res

    # Run clustering task
    cluster_res = await _async_run_pain_point_clustering()
    assert cluster_res["status"] == "SUCCESS"

    # Verify background execution record in DB
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(DiscoveryTaskExecutionRecord)
            .where(DiscoveryTaskExecutionRecord.task_type == "STARTUP_DISCOVERY")
            .order_by(DiscoveryTaskExecutionRecord.created_at.desc())
        )
        latest_exec = res.scalars().first()
        assert latest_exec is not None
        assert latest_exec.status == "SUCCESS"
        assert latest_exec.execution_duration_ms >= 0


@pytest.mark.asyncio
async def test_discovery_rest_api_lifecycle():
    """Tests GET /status, /config, PUT /config, POST /pause, /resume, and POST /refresh with cooldown."""
    await ensure_discovery_configs_seeded()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_test_token(client, email=f"disco_{uuid.uuid4().hex[:6]}@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. GET /api/v1/discovery/status
        status_res = await client.get("/api/v1/discovery/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["success"] is True
        assert "engine_state" in status_data["data"]
        assert "schedules" in status_data["data"]

        # 2. GET /api/v1/discovery/config
        cfg_res = await client.get("/api/v1/discovery/config")
        assert cfg_res.status_code == 200
        configs = cfg_res.json()["data"]
        assert len(configs) >= 1
        test_source_id = configs[0]["source_id"]

        # 3. PUT /api/v1/discovery/config/{source_id}
        put_res = await client.put(
            f"/api/v1/discovery/config/{test_source_id}",
            json={"interval_seconds": 900, "max_records_per_run": 25},
            headers=headers,
        )
        assert put_res.status_code == 200
        updated_cfg = put_res.json()["data"]
        assert updated_cfg["interval_seconds"] == 900
        assert updated_cfg["max_records_per_run"] == 25

        # 4. POST /api/v1/discovery/pause (global)
        pause_res = await client.post("/api/v1/discovery/pause", headers=headers)
        assert pause_res.status_code == 200
        assert pause_res.json()["data"]["is_paused"] is True

        # 5. POST /api/v1/discovery/resume (global)
        resume_res = await client.post("/api/v1/discovery/resume", headers=headers)
        assert resume_res.status_code == 200
        assert resume_res.json()["data"]["is_paused"] is False

        # 6. POST /api/v1/discovery/refresh (manual refresh)
        refresh_res = await client.post(
            "/api/v1/discovery/refresh",
            json={"opportunity_type": "STARTUPS"},
            headers=headers,
        )
        assert refresh_res.status_code == 200
        assert refresh_res.json()["success"] is True

        # 7. Immediate re-trigger should return 429 Too Many Requests (cooldown enforcement)
        cooldown_res = await client.post(
            "/api/v1/discovery/refresh",
            json={"opportunity_type": "STARTUPS"},
            headers=headers,
        )
        assert cooldown_res.status_code == 429
        err_msg = cooldown_res.json().get("error", {}).get("message", "")
        assert "cooldown active" in err_msg.lower()


@pytest.mark.asyncio
async def test_candidate_skill_confirmation_and_recompute_lifecycle():
    """Tests candidate skill confirmation, rejection, and matching recomputation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_test_token(client, email=f"cand_skill_{uuid.uuid4().hex[:6]}@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Add an unconfirmed / extracted skill with valid FieldProvenance enum
        add_skill_res = await client.post(
            "/api/v1/candidate/skills",
            json={
                "skill_name": "Kubernetes",
                "category": "Infrastructure",
                "proficiency": "Intermediate",
                "years_experience": 2.0,
                "provenance": "RESUME_EXTRACTED",
            },
            headers=headers,
        )
        assert add_skill_res.status_code == 201
        skill_id = add_skill_res.json()["data"]["id"]

        # 2. Confirm the skill -> POST /api/v1/candidate/skills/{id}/confirm
        confirm_res = await client.post(
            f"/api/v1/candidate/skills/{skill_id}/confirm",
            headers=headers,
        )
        assert confirm_res.status_code == 200
        assert confirm_res.json()["success"] is True
        confirmed_data = confirm_res.json()["data"]
        assert confirmed_data["confirmation_status"] == "CONFIRMED"

        # 3. Add a second skill and reject it -> POST /api/v1/candidate/skills/{id}/reject
        add_skill_res2 = await client.post(
            "/api/v1/candidate/skills",
            json={
                "skill_name": "PHP",
                "category": "Backend",
                "proficiency": "Novice",
                "years_experience": 1.0,
                "provenance": "AI_SUGGESTED",
            },
            headers=headers,
        )
        assert add_skill_res2.status_code == 201
        skill2_id = add_skill_res2.json()["data"]["id"]

        reject_res = await client.post(
            f"/api/v1/candidate/skills/{skill2_id}/reject",
            headers=headers,
        )
        assert reject_res.status_code == 200
        rejected_data = reject_res.json()["data"]
        assert rejected_data["confirmation_status"] == "REJECTED"

        # 4. Trigger profile skills recomputation -> POST /api/v1/candidate/skills/recompute
        recompute_res = await client.post(
            "/api/v1/candidate/skills/recompute",
            headers=headers,
        )
        assert recompute_res.status_code == 200
        recompute_data = recompute_res.json()["data"]
        assert recompute_data["confirmed_skills_count"] >= 1
        assert "unconfirmed_skills_count" in recompute_data
        assert "recomputed_at" in recompute_data
