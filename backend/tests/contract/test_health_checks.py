"""
Contract Tests: Liveness and Readiness Health Probes
Version: 1.0.0
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from contracts.health.models import DependencyHealth, HealthStatus, LivenessResponse, ReadinessResponse


@pytest.mark.asyncio
async def test_liveness_probe_endpoint():
    """Verifies that /health/live returns HTTP 200 and indicates process operational status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "core_career_engine"
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_readiness_probe_endpoint():
    """Verifies that /health/ready returns HTTP 200 and checks subsystem dependencies."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "core_career_engine"
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "redis" in data["dependencies"]
        assert data["dependencies"]["database"]["status"] == "healthy"
        assert data["dependencies"]["redis"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_v1_health_routing():
    """Verifies that health checks are also accessible through the versioned /api/v1 prefix."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_dependency_health_model_validation():
    """Verifies the DependencyHealth model serialization and field limits."""
    dep = DependencyHealth(
        status=HealthStatus.HEALTHY,
        latency_ms=1.45,
        message="Connection pool warm",
    )
    dumped = dep.model_dump()
    assert dumped["status"] == HealthStatus.HEALTHY
    assert dumped["latency_ms"] == 1.45
    assert dumped["message"] == "Connection pool warm"

