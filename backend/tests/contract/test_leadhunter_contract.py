"""
Contract Tests: Core-to-LeadHunter API Contracts & Deterministic Mock Provider
Version: 1.0.0
"""

import pytest

from backend.app.integrations.mock_providers import MockLeadHunterClient
from contracts.health.models import HealthStatus
from contracts.leads.models import (
    LeadDetailResponse,
    LeadDiscoveryRequest,
    LeadDiscoveryResult,
    LeadDiscoveryStatus,
    LeadSummary,
    ScanJobStatus,
    WebsiteAuditReport,
)
from contracts.opportunities.models import FreelanceOpportunityPayload, OpportunityEnvelope, OpportunityType


@pytest.mark.asyncio
async def test_leadhunter_mock_success_scenario():
    """Verifies that MockLeadHunterClient behaves deterministically in 'success' mode."""
    client = MockLeadHunterClient(mode="success")

    # 1. Check Liveness & Readiness
    live = await client.get_liveness()
    ready = await client.get_readiness()
    assert live.status == HealthStatus.HEALTHY
    assert ready.status == HealthStatus.HEALTHY
    assert ready.dependencies["database"].status == HealthStatus.HEALTHY

    # 2. Trigger Discovery
    req = LeadDiscoveryRequest(
        query="Dentists",
        city="Austin, TX",
        max_results=10,
        include_with_website=True,
    )
    status_resp = await client.trigger_discovery(req, correlation_id="test-corr-lh-1")
    assert status_resp.status == ScanJobStatus.COMPLETED
    assert status_resp.total_found == 2
    assert status_resp.progress_percentage == 100

    # 3. Retrieve Results
    results = await client.get_discovery_results(status_resp.discovery_id)
    assert results.total_leads == 2
    assert len(results.leads) == 2
    first_lead = results.leads[0]
    assert first_lead.business_name == "Downtown Dental Clinic"
    assert first_lead.is_broken_website is True

    # 4. Canonical Opportunity Envelope Conversion
    envelopes = client.convert_to_opportunity_envelopes(results)
    assert len(envelopes) == 2
    for env in envelopes:
        assert env.opportunity_type == OpportunityType.FREELANCE
        assert isinstance(env.payload, FreelanceOpportunityPayload)
        assert env.organization.name in ["Downtown Dental Clinic", "Austin Prime Accounting"]


@pytest.mark.asyncio
async def test_leadhunter_mock_empty_scenario():
    """Verifies that MockLeadHunterClient behaves correctly when no leads are found."""
    client = MockLeadHunterClient(mode="empty")
    req = LeadDiscoveryRequest(query="NonExistentNiche", city="NowhereLand")
    status_resp = await client.trigger_discovery(req, correlation_id="test-corr-lh-2")
    assert status_resp.total_found == 0

    results = await client.get_discovery_results(status_resp.discovery_id)
    assert results.total_leads == 0
    assert len(results.leads) == 0

    envelopes = client.convert_to_opportunity_envelopes(results)
    assert len(envelopes) == 0


@pytest.mark.asyncio
async def test_leadhunter_mock_validation_error_scenario():
    """Verifies that invalid parameters raise ValueError in validation_error mode."""
    client = MockLeadHunterClient(mode="validation_error")
    req = LeadDiscoveryRequest(query="Plumbers", city="Austin")

    with pytest.raises(ValueError) as exc_info:
        await client.trigger_discovery(req, correlation_id="test-corr-lh-3")
    assert "City parameter cannot be resolved" in str(exc_info.value)


@pytest.mark.asyncio
async def test_leadhunter_mock_unavailable_scenario():
    """Verifies that outage mode triggers runtime errors and reports unhealthy readiness."""
    client = MockLeadHunterClient(mode="unavailable")

    ready = await client.get_readiness()
    assert ready.status == HealthStatus.UNHEALTHY
    assert ready.dependencies["database"].status == HealthStatus.UNHEALTHY

    req = LeadDiscoveryRequest(query="Dentists", city="Austin")
    with pytest.raises(RuntimeError) as exc_info:
        await client.trigger_discovery(req, correlation_id="test-corr-lh-4")
    assert "LeadHunter service unavailable" in str(exc_info.value)


@pytest.mark.asyncio
async def test_leadhunter_lead_detail_and_audit():
    """Verifies retrieval of detailed audit report for a specific lead."""
    client = MockLeadHunterClient(mode="success")
    detail = await client.get_lead_detail("lead_mock_001")

    assert detail.lead.business_name == "Downtown Dental Clinic"
    assert detail.audit is not None
    assert detail.audit.ssl_valid is False
    assert detail.audit.mobile_friendly is False
    assert "Missing valid TLS/SSL certificate" in detail.audit.issues
