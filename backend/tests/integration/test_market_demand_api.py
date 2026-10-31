"""
Integration Tests: Market Demand, Skill Taxonomy & Sources REST APIs
Phase: 12 — Market & Compensation Intelligence
"""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_skills_and_alias_resolution_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List skills
        res = await client.get("/api/v1/market/skills")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["total"] >= 5

        # 2. Resolve alias 'postgres'
        res_alias = await client.get("/api/v1/market/skills/resolve?query=postgres")
        assert res_alias.status_code == 200
        res_data = res_alias.json()["data"]
        assert res_data["resolved"] is True
        assert res_data["canonical_name"] == "PostgreSQL"

        # 3. Resolve alias 'js'
        res_js = await client.get("/api/v1/market/skills/resolve?query=js")
        assert res_js.status_code == 200
        assert res_js.json()["data"]["canonical_name"] == "JavaScript"


@pytest.mark.asyncio
async def test_market_demand_time_windows_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Valid 30d window
        res_30d = await client.get("/api/v1/market/demand/skills?time_window=30d")
        assert res_30d.status_code == 200
        body_30d = res_30d.json()
        assert body_30d["success"] is True
        assert "sample_size" in body_30d["data"]
        assert "methodology" in body_30d["data"]
        assert "limitations" in body_30d["data"]

        # Invalid window returns 400
        res_inv = await client.get("/api/v1/market/demand/skills?time_window=invalid_window")
        assert res_inv.status_code == 400


@pytest.mark.asyncio
async def test_market_trends_and_sources_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trends
        res_trends = await client.get("/api/v1/market/trends?time_window=30d")
        assert res_trends.status_code == 200
        body_tr = res_trends.json()
        assert body_tr["success"] is True
        assert "current_period" in body_tr["data"]
        assert "comparison_period" in body_tr["data"]

        # 2. Documented Sources
        res_sources = await client.get("/api/v1/market/sources")
        assert res_sources.status_code == 200
        body_src = res_sources.json()
        assert body_src["success"] is True
        assert body_src["total"] >= 2
        source_codes = {s["source_code"] for s in body_src["data"]}
        assert "CORE_ATS_OBSERVATIONS" in source_codes
        assert "PUBLIC_LABOR_STATS" in source_codes

        # 3. Methodology disclosure
        res_meth = await client.get("/api/v1/market/methodology")
        assert res_meth.status_code == 200
        body_meth = res_meth.json()
        assert body_meth["success"] is True
        assert "false_precision_protections" in body_meth["data"]

