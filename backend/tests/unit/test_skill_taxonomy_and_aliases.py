"""
Unit Tests: Canonical Skill Taxonomy, Alias Resolution & Ambiguity Prevention
Phase: 12 — Market & Compensation Intelligence
"""

import pytest
from app.core.database import AsyncSessionLocal
from app.services.market_intelligence_service import MarketIntelligenceService


@pytest.mark.asyncio
async def test_canonical_skill_listing():
    async with AsyncSessionLocal() as session:
        skills = await MarketIntelligenceService.list_skills(session=session)
        assert len(skills) >= 5
        slugs = {s["slug"] for s in skills}
        assert "python" in slugs
        assert "javascript" in slugs
        assert "postgresql" in slugs
        assert "react" in slugs


@pytest.mark.asyncio
async def test_skill_alias_resolution():
    async with AsyncSessionLocal() as session:
        # 1. 'js' -> JavaScript
        res_js = await MarketIntelligenceService.resolve_skill_alias("js", session=session)
        assert res_js["resolved"] is True
        assert res_js["canonical_name"] == "JavaScript"
        assert res_js["slug"] == "javascript"

        # 2. 'postgres' -> PostgreSQL
        res_pg = await MarketIntelligenceService.resolve_skill_alias("postgres", session=session)
        assert res_pg["resolved"] is True
        assert res_pg["canonical_name"] == "PostgreSQL"
        assert res_pg["slug"] == "postgresql"

        # 3. 'k8s' -> Kubernetes
        res_k8s = await MarketIntelligenceService.resolve_skill_alias("k8s", session=session)
        assert res_k8s["resolved"] is True
        assert res_k8s["canonical_name"] == "Kubernetes"

        # 4. 'react.js' -> React
        res_react = await MarketIntelligenceService.resolve_skill_alias("react.js", session=session)
        assert res_react["resolved"] is True
        assert res_react["canonical_name"] == "React"

        # 5. 'py' -> Python
        res_py = await MarketIntelligenceService.resolve_skill_alias("py", session=session)
        assert res_py["resolved"] is True
        assert res_py["canonical_name"] == "Python"


@pytest.mark.asyncio
async def test_ambiguous_or_unknown_skills_not_falsely_merged():
    async with AsyncSessionLocal() as session:
        # Unknown random technology
        res_unknown = await MarketIntelligenceService.resolve_skill_alias("nonexistent_framework_999", session=session)
        assert res_unknown["resolved"] is False
        assert res_unknown["canonical_name"] is None
        assert res_unknown["confidence"] == 0.0

        # Empty string
        res_empty = await MarketIntelligenceService.resolve_skill_alias("   ", session=session)
        assert res_empty["resolved"] is False


@pytest.mark.asyncio
async def test_skill_detail_retrieval():
    async with AsyncSessionLocal() as session:
        detail = await MarketIntelligenceService.get_skill_detail("python", session=session)
        assert detail is not None
        assert detail["canonical_name"] == "Python"
        assert detail["category"] == "Programming Languages"
        assert len(detail["aliases"]) >= 1

