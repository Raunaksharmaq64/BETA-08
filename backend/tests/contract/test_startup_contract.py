"""
Contract Tests: Core-to-Startup Hunter API Contracts & Deterministic Mock Provider
Version: 1.0.0
"""

import pytest

from backend.app.integrations.mock_providers import MockStartupHunterClient
from contracts.health.models import HealthStatus
from contracts.opportunities.models import OpportunityEnvelope, OpportunityType, StartupProblemPayload
from contracts.pain_points.models import (
    CommunitySource,
    StartupDiscoveryRequest,
    StartupDiscoveryResult,
    StartupDiscoveryStatus,
    StartupProblemDetailResponse,
    StartupProblemSummary,
    StartupScanStatus,
)


@pytest.mark.asyncio
async def test_startup_mock_success_scenario():
    """Verifies that MockStartupHunterClient behaves deterministically in 'success' mode."""
    client = MockStartupHunterClient(mode="success")

    # 1. Health
    live = await client.get_liveness()
    ready = await client.get_readiness()
    assert live.status == HealthStatus.HEALTHY
    assert ready.status == HealthStatus.HEALTHY

    # 2. Trigger Discovery
    req = StartupDiscoveryRequest(
        sources=[CommunitySource.REDDIT, CommunitySource.HACKER_NEWS],
        keywords=["Postgres", "slow", "Next.js"],
        categories=["Database", "Performance"],
        max_signals=10,
    )
    status_resp = await client.trigger_discovery(req, correlation_id="test-corr-si-1")
    assert status_resp.status == StartupScanStatus.COMPLETED
    assert status_resp.total_opportunities_found == 2
    assert status_resp.total_signals_analyzed == 25

    # 3. Retrieve Results
    results = await client.get_discovery_results(status_resp.discovery_id)
    assert results.total_count == 2
    assert len(results.problems) == 2
    first_problem = results.problems[0]
    assert first_problem.startup_name == "CloudMetric SaaS"
    assert first_problem.category == "Database"
    assert first_problem.urgency_score == 8

    # 4. Canonical Opportunity Envelope Conversion
    envelopes = client.convert_to_opportunity_envelopes(results)
    assert len(envelopes) == 2
    for env in envelopes:
        assert env.opportunity_type == OpportunityType.STARTUP_PROBLEM
        assert isinstance(env.payload, StartupProblemPayload)
        assert env.organization.name in ["CloudMetric SaaS", "DevShip.io"]
        assert env.payload.urgency_score in [8, 7]


@pytest.mark.asyncio
async def test_startup_mock_empty_scenario():
    """Verifies that MockStartupHunterClient behaves correctly when no problems are found."""
    client = MockStartupHunterClient(mode="empty")
    req = StartupDiscoveryRequest(keywords=["completely_obscure_phrase_9981"])
    status_resp = await client.trigger_discovery(req, correlation_id="test-corr-si-2")
    assert status_resp.total_opportunities_found == 0

    results = await client.get_discovery_results(status_resp.discovery_id)
    assert results.total_count == 0
    assert len(results.problems) == 0

    envelopes = client.convert_to_opportunity_envelopes(results)
    assert len(envelopes) == 0


@pytest.mark.asyncio
async def test_startup_mock_validation_error_scenario():
    """Verifies that invalid parameters raise ValueError in validation_error mode."""
    client = MockStartupHunterClient(mode="validation_error")
    req = StartupDiscoveryRequest(keywords=["too", "many", "keywords", "here", "exceeding", "permitted", "limit", "test", "fail", "now", "overflow"])

    with pytest.raises(ValueError) as exc_info:
        await client.trigger_discovery(req, correlation_id="test-corr-si-3")
    assert "Keywords list exceeds permitted maximum of 10" in str(exc_info.value)


@pytest.mark.asyncio
async def test_startup_mock_timeout_scenario():
    """Verifies that upstream latency timeout triggers TimeoutError."""
    client = MockStartupHunterClient(mode="timeout")
    req = StartupDiscoveryRequest()

    with pytest.raises(TimeoutError) as exc_info:
        await client.trigger_discovery(req, correlation_id="test-corr-si-4")
    assert "Startup Intelligence query timed out after 5.0s" in str(exc_info.value)


@pytest.mark.asyncio
async def test_startup_problem_detail():
    """Verifies retrieval of detailed raw excerpt and founder contact info."""
    client = MockStartupHunterClient(mode="success")
    detail = await client.get_problem_detail("sig_mock_001")

    assert detail.problem.startup_name == "CloudMetric SaaS"
    assert "production database connection pool exhaustion" in detail.raw_excerpt
    assert detail.founder_contact_info.get("reddit_user") == "u/saas_dev_dan"
