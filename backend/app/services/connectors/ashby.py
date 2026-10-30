"""
RIGHT FIT Core — Ashby Job Board API Connector
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Interacts with official public Ashby posting JSON API:
https://api.ashbyhq.com/posting-api/job-board/{board_token}
Zero scraping required; public JSON feed.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

from app.db.models import JobSourceRecord
from app.services.connectors.base import (
    BaseJobConnector,
    ConnectorFetchResult,
    HealthCheckResult,
    RawJobPayload,
)

USER_AGENT = "RIGHT-FIT-Career-Intelligence/1.0 (+https://rightfit.platform)"


class AshbyConnector(BaseJobConnector):
    """Connector for official Ashby public job board JSON API."""

    @property
    def provider_name(self) -> str:
        return "ashby"

    def _build_api_url(self, base_url: str) -> str:
        """Converts provided board URL or slug into canonical posting-api URL."""
        clean = base_url.strip()
        if "api.ashbyhq.com" in clean:
            return clean

        if "jobs.ashbyhq.com" in clean:
            parsed = urlparse(clean)
            parts = [p for p in parsed.path.split("/") if p]
            token = parts[0] if parts else clean
            return f"https://api.ashbyhq.com/posting-api/job-board/{token}"

        token = clean.strip("/")
        return f"https://api.ashbyhq.com/posting-api/job-board/{token}"

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates Ashby board URL format."""
        if not base_url or len(base_url.strip()) < 2:
            raise ValueError("Ashby base_url or board token is required")

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Checks availability of Ashby public job board API."""
        api_url = self._build_api_url(source.base_url)
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.get(api_url)
                latency = (time.time() - start_time) * 1000.0
                resp.raise_for_status()
                return HealthCheckResult(
                    healthy=True,
                    status_code=resp.status_code,
                    latency_ms=round(latency, 2),
                    message="Ashby posting API reachable and responsive"
                )
        except Exception as exc:
            latency = (time.time() - start_time) * 1000.0
            return HealthCheckResult(
                healthy=False,
                status_code=getattr(exc, "response", None).status_code if hasattr(exc, "response") and exc.response else None,
                latency_ms=round(latency, 2),
                message=f"Health probe failed: {str(exc)}"
            )

    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls raw listings from Ashby public JSON API."""
        api_url = self._build_api_url(source.base_url)

        async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
            resp = await client.get(api_url)
            resp.raise_for_status()
            data = resp.json()

        jobs_data = data.get("jobs", []) if isinstance(data, dict) else []
        records: List[RawJobPayload] = []

        for item in jobs_data[:limit]:
            ext_id = str(item.get("id"))
            listing_url = item.get("jobUrl") or f"https://jobs.ashbyhq.com/{source.source_key}/{ext_id}"

            published_at = None
            raw_published = item.get("publishedAt")
            if raw_published:
                try:
                    published_at = datetime.fromisoformat(raw_published.replace("Z", "+00:00"))
                except Exception:
                    published_at = None

            records.append(
                RawJobPayload(
                    external_job_id=ext_id,
                    listing_url=listing_url,
                    raw_payload=item,
                    source_published_at=published_at,
                    source_updated_at=published_at,
                )
            )

        return ConnectorFetchResult(
            records=records,
            total_found=len(jobs_data),
            metadata={"board_api_url": api_url, "records_in_payload": len(jobs_data)}
        )
