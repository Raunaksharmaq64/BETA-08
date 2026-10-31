"""
Integration tests for Phase 14: Connector Health Metrics, Data Quality Telemetry & Release Notes API
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import AsyncSessionLocal
from app.services.beta_validation_service import BetaValidationService


@pytest.mark.asyncio
async def test_connector_health_metrics_api():
    """Tests GET /api/v1/beta/connectors returns accurate reliability metrics."""
    async with AsyncSessionLocal() as session:
        await BetaValidationService.ensure_baseline_seeded(session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/beta/connectors")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        payload = data["data"]
        assert payload["total_runs"] >= 6
        assert payload["overall_success_rate_pct"] > 0
        assert len(payload["connectors"]) >= 4
        # Verify greenhouse connector exists
        gh = next((c for c in payload["connectors"] if c["source_key"] == "greenhouse_ats"), None)
        assert gh is not None
        assert gh["runs"] >= 1


@pytest.mark.asyncio
async def test_data_quality_metrics_api():
    """Tests GET /api/v1/beta/quality returns deduplication and broken link metrics."""
    async with AsyncSessionLocal() as session:
        await BetaValidationService.ensure_baseline_seeded(session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/beta/quality")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        payload = data["data"]
        assert payload["total_active_listings"] > 0
        assert payload["duplicate_detection_rate_pct"] >= 0.0
        assert payload["broken_link_rate_pct"] >= 0.0


@pytest.mark.asyncio
async def test_source_governance_and_release_notes_api():
    """Tests GET /api/v1/beta/source-governance and /api/v1/beta/release-notes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Source governance
        gov_res = await client.get("/api/v1/beta/source-governance")
        assert gov_res.status_code == 200
        gov_data = gov_res.json()
        assert gov_data["success"] is True
        assert "policy_statement" in gov_data["data"]

        # 2. Release notes
        rel_res = await client.get("/api/v1/beta/release-notes")
        assert rel_res.status_code == 200
        rel_data = rel_res.json()
        assert rel_data["success"] is True
        rel_payload = rel_data["data"]
        assert rel_payload["version"] == "1.0.0-beta.1"
        assert len(rel_payload["verified_capabilities"]) >= 5
        assert len(rel_payload["known_limitations"]) >= 3
        assert "support" in rel_payload
