"""
Contract Tests: FastAPI Main Error Handlers & Middleware Compliance
Version: 1.0.0
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from contracts.common.errors import ErrorCode


@pytest.mark.asyncio
async def test_404_error_handler_produces_api_error_response():
    """Verifies that an unmapped path produces a standard APIErrorResponse envelope."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/nonexistent/endpoint/path")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == ErrorCode.RESOURCE_NOT_FOUND
        assert data["error"]["service"] == "core_career_engine"
        assert "request_id" in data["error"]
        assert "x-request-id" in response.headers
        assert "x-response-time-ms" in response.headers


@pytest.mark.asyncio
async def test_root_endpoint_metadata():
    """Verifies root endpoint exposes system info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "RIGHT FIT Core Career Engine"
        assert data["status"] == "OPERATIONAL"

