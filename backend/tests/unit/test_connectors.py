"""
Unit Tests: Job Connectors & Adapter Registry
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

import pytest

from app.db.models import JobSourceRecord
from app.services.connectors import (
    AshbyConnector,
    GreenhouseConnector,
    SyntheticJobConnector,
    get_connector,
    list_supported_providers,
)


def test_connector_registry_lookup():
    """Retrieves registered connectors and validates supported list."""
    assert "greenhouse" in list_supported_providers()
    assert "ashby" in list_supported_providers()
    assert "synthetic" in list_supported_providers()

    gh = get_connector("greenhouse")
    assert isinstance(gh, GreenhouseConnector)

    ash = get_connector("ashby")
    assert isinstance(ash, AshbyConnector)

    syn = get_connector("synthetic")
    assert isinstance(syn, SyntheticJobConnector)

    with pytest.raises(ValueError, match="Unsupported connector provider"):
        get_connector("unsupported_provider_xyz")


def test_greenhouse_url_normalization():
    """Transforms raw slugs or board URLs into canonical boards-api URLs."""
    gh = GreenhouseConnector()

    # Raw slug
    url1 = gh._build_api_url("stripe")
    assert url1 == "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"

    # Board website URL
    url2 = gh._build_api_url("https://boards.greenhouse.io/airbnb")
    assert url2 == "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true"

    # Direct boards-api URL without content=true
    url3 = gh._build_api_url("https://boards-api.greenhouse.io/v1/boards/github/jobs")
    assert "content=true" in url3


def test_ashby_url_normalization():
    """Transforms raw slugs or board URLs into canonical Ashby posting URLs."""
    ash = AshbyConnector()

    # Raw slug
    url1 = ash._build_api_url("notion")
    assert url1 == "https://api.ashbyhq.com/posting-api/job-board/notion"

    # Board website URL
    url2 = ash._build_api_url("https://jobs.ashbyhq.com/figma")
    assert url2 == "https://api.ashbyhq.com/posting-api/job-board/figma"


@pytest.mark.asyncio
async def test_synthetic_connector_fetch_and_fault_injection():
    """Synthetic connector generates deterministic payloads and handles simulated faults."""
    syn = SyntheticJobConnector()
    source = JobSourceRecord(
        id="src-syn-01",
        source_key="synthetic-test",
        display_name="Synthetic Board",
        provider="synthetic",
        base_url="synthetic://default",
        timeout_seconds=5.0,
    )

    # Normal fetch
    res = await syn.fetch_jobs(source, limit=2)
    assert len(res.records) == 2
    assert res.records[0].external_job_id == "syn-001"
    assert "Python" in res.records[0].raw_payload["title"]

    # Health check
    health = await syn.check_health(source)
    assert health.healthy is True
    assert health.status_code == 200

    # Fault injection: transient error simulation
    source.credential_reference = "SIMULATE_TRANSIENT_ERROR"
    with pytest.raises(Exception):
        await syn.fetch_jobs(source)
