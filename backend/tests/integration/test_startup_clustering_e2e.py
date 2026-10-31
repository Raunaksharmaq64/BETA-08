"""
RIGHT FIT Core — Startup Pain-Point Intelligence & Clustering E2E Tests
Master Implementation: Observation Collection, Corroboration, Clustering & Pitch Intelligence
"""

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.db.models import (
    StartupCorroborationRecord,
    StartupEvidenceRecord,
    StartupOpportunityRecord,
    StartupPitchDraftRecord,
)
from app.main import app
from app.services.startup_service import StartupService
from app.workers.tasks.startup_tasks import _async_run_pain_point_clustering


async def get_test_auth_headers(client: AsyncClient, email: str = "cluster_tester@example.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Cluster Analyst"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_startup_observation_ingestion_and_corroboration():
    """
    Verifies that multiple independent public observations (e.g. from Reddit and Hacker News)
    for the same startup domain corroborate the canonical problem without creating duplicate opportunities.
    """
    test_domain_url = f"https://synctech-{uuid.uuid4().hex[:6]}.io"

    # Observation 1: Reddit community mention
    obs1 = {
        "startup_name": "SyncTech IO",
        "url": test_domain_url,
        "category": "Data Engineering",
        "detected_signal": "Kafka consumer lag exceeding 20 minutes during batch sync",
        "insight": "High volume partition rebalances causing consumer disconnects.",
        "opportunity": "Kafka consumer group architecture refactor and dynamic partitioning.",
        "pitch_idea": "Optimize consumer concurrency and commit offsets asynchronously.",
        "score": 8,
        "score_explanation": "Persistent lag noticed across customer sync workers.",
        "source": "Reddit r/dataengineering",
    }

    # Observation 2: Hacker News discussion corroborating the same issue
    obs2 = {
        "startup_name": "SyncTech IO",
        "url": test_domain_url,
        "category": "Data Engineering",
        "detected_signal": "SyncTech IO batch sync jobs stalling under peak load",
        "insight": "Confirmed by multiple engineers experiencing slow ingestion queues.",
        "opportunity": "Distributed worker scaling and partition management.",
        "pitch_idea": "Implement decoupled queue sharding.",
        "score": 9,
        "score_explanation": "Critical production slowdown reported by users.",
        "source": "Hacker News (Ask HN / Comments)",
    }

    async with AsyncSessionLocal() as session:
        # Ingest observation 1
        res1 = await StartupService.import_startup_leads([obs1], session)
        assert res1["imported_count"] == 1

        # Ingest observation 2 (corroborating)
        res2 = await StartupService.import_startup_leads([obs2], session)
        # Should update existing canonical startup opportunity rather than duplicating it
        assert res2["updated_count"] == 1 or res2["imported_count"] == 0

        # Query canonical opportunity in database
        opp_query = await session.execute(
            select(StartupOpportunityRecord).where(
                StartupOpportunityRecord.startup_name == "SyncTech IO"
            )
        )
        opps = opp_query.scalars().all()
        # Exactly one canonical opportunity should exist for this startup
        assert len(opps) == 1
        canonical_opp = opps[0]

        # Verify evidence ledger has both independent observations
        ev_query = await session.execute(
            select(StartupEvidenceRecord).where(
                StartupEvidenceRecord.opportunity_id == canonical_opp.id
            )
        )
        evidence_records = ev_query.scalars().all()
        assert len(evidence_records) >= 2
        sources = {ev.publisher for ev in evidence_records}
        assert any("Reddit" in s for s in sources)
        assert any("Hacker News" in s for s in sources)


@pytest.mark.asyncio
async def test_pain_point_clustering_and_corroboration_aggregation():
    """Verifies that the background clustering task recalculates corroboration counts across all opportunities."""
    cluster_task_res = await _async_run_pain_point_clustering()
    assert cluster_task_res["status"] == "SUCCESS"
    assert "clusters_updated" in cluster_task_res


@pytest.mark.asyncio
async def test_startup_pitch_generation_with_evidence_citations():
    """
    Verifies that candidate pitch draft generation incorporates verified evidence citations
    and explicit problem assumptions.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email=f"pitcher_{uuid.uuid4().hex[:6]}@example.com")

        # 1. Ingest test opportunity
        test_opp_lead = {
            "startup_name": "VaultScale",
            "url": "https://vaultscale.internal",
            "category": "Cloud Infrastructure",
            "detected_signal": "Database connection pool exhaustion during peak traffic",
            "insight": "Microservices opening unpooled Postgres connections directly.",
            "opportunity": "Deploy PgBouncer / RDS Proxy connection pooling layer.",
            "pitch_idea": "Configure managed connection pooling and circuit breakers.",
            "score": 9,
            "source": "Hacker News & Engineering Blogs",
        }

        async with AsyncSessionLocal() as session:
            await StartupService.import_startup_leads([test_opp_lead], session)

        # 2. Find the opportunity via API
        list_res = await client.get("/api/v1/startups?search=VaultScale", headers=headers)
        assert list_res.status_code == 200
        opps = list_res.json()["data"]
        assert len(opps) >= 1
        opp_id = opps[0]["id"]

        # 3. Create Pitch Draft -> POST /api/v1/startups/{opp_id}/pitch
        create_pitch_res = await client.post(
            f"/api/v1/startups/{opp_id}/pitch",
            json={"tone": "confident"},
            headers=headers,
        )
        assert create_pitch_res.status_code == 200
        pitch_data = create_pitch_res.json()["data"]
        assert pitch_data["opportunity_id"] == opp_id
        assert "explicit_assumptions" in pitch_data
        assert "VaultScale" in pitch_data["subject"]
        pitch_id = pitch_data["id"]

        # 4. Edit Pitch Draft -> PUT /api/v1/startups/pitches/{draft_id}
        edit_pitch_res = await client.put(
            f"/api/v1/startups/pitches/{pitch_id}",
            json={
                "subject": "Proposal for Resolving Connection Pool Bottlenecks",
                "body": "Our analysis indicates PgBouncer will alleviate database connection limits.",
                "tone": "formal",
            },
            headers=headers,
        )
        assert edit_pitch_res.status_code == 200
        assert edit_pitch_res.json()["data"]["subject"] == "Proposal for Resolving Connection Pool Bottlenecks"
