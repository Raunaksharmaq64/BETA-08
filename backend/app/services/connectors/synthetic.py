"""
RIGHT FIT Core — Synthetic Test Connector
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Provides deterministic, offline job fixtures for testing resilience,
normalization, circuit breaker state machine, and deduplication.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.db.models import JobSourceRecord
from app.services.connectors.base import (
    BaseJobConnector,
    ConnectorFetchResult,
    HealthCheckResult,
    RawJobPayload,
)


class SyntheticJobConnector(BaseJobConnector):
    """Deterministic synthetic connector for testing and verification."""

    @property
    def provider_name(self) -> str:
        return "synthetic"

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates synthetic source config."""
        if not base_url or not base_url.startswith(("mock://", "synthetic://", "http://", "https://")):
            raise ValueError("Synthetic base_url must start with synthetic://, mock://, http://, or https://")

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Evaluates simulated health status."""
        if source.credential_reference == "SIMULATE_UNHEALTHY":
            return HealthCheckResult(
                healthy=False,
                status_code=503,
                latency_ms=15.0,
                message="Synthetic probe simulated failure: 503 Service Unavailable"
            )

        return HealthCheckResult(
            healthy=True,
            status_code=200,
            latency_ms=4.2,
            message="Synthetic mock endpoint is operational"
        )

    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Generates realistic synthetic opportunities."""
        # Simulated fault injection for resilience testing
        if source.credential_reference == "SIMULATE_TRANSIENT_ERROR":
            request = httpx.Request("GET", source.base_url)
            response = httpx.Response(status_code=503, request=request)
            raise httpx.HTTPStatusError("Simulated 503 Service Unavailable", request=request, response=response)

        if source.credential_reference == "SIMULATE_AUTH_ERROR":
            request = httpx.Request("GET", source.base_url)
            response = httpx.Response(status_code=401, request=request)
            raise httpx.HTTPStatusError("Simulated 401 Unauthorized", request=request, response=response)

        # Generate deterministic synthetic records
        sample_roles = [
            {
                "id": "syn-001",
                "title": "Senior Backend Engineer (Python / FastAPI)",
                "department": "Core Platform",
                "location": "San Francisco, CA (Remote)",
                "is_remote": True,
                "content": "<p>We are seeking a <strong>Senior Backend Engineer</strong> to build distributed services.</p><h3>Requirements</h3><ul><li>5+ years Python</li><li>FastAPI & PostgreSQL</li><li>Docker</li></ul>",
                "salary": {"min": 160000, "max": 210000, "currency": "USD", "period": "YEAR"},
                "url": "https://example.com/jobs/syn-001",
            },
            {
                "id": "syn-002",
                "title": "Staff AI Systems Architect",
                "department": "Artificial Intelligence",
                "location": "New York, NY",
                "is_remote": False,
                "content": "<p>Architect modern agentic intelligence workflows.</p><p>Experience with LLMs and vector stores required.</p>",
                "salary": {"min": 220000, "max": 280000, "currency": "USD", "period": "YEAR"},
                "url": "https://example.com/jobs/syn-002",
            },
            {
                "id": "syn-003",
                "title": "Frontend Lead (Next.js / TypeScript)",
                "department": "Product Engineering",
                "location": "Remote - US & Canada",
                "is_remote": True,
                "content": "<p>Lead our dashboard and UI systems using React and Tailwind CSS.</p>",
                "salary": None,  # Test explicit lack of compensation (should NOT fabricate)
                "url": "https://example.com/jobs/syn-003",
            },
        ]

        records: List[RawJobPayload] = []
        now = datetime.now(timezone.utc)

        for item in sample_roles[:limit]:
            records.append(
                RawJobPayload(
                    external_job_id=item["id"],
                    listing_url=item["url"],
                    raw_payload=item,
                    source_published_at=now,
                    source_updated_at=now,
                )
            )

        return ConnectorFetchResult(
            records=records,
            total_found=len(sample_roles),
            metadata={"synthetic": True, "count": len(records)}
        )
