"""
RIGHT FIT Core — Greenhouse Job Board API Connector
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Interacts with official public Greenhouse board JSON APIs:
https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
Zero HTML scraping required; strictly permitted public API feed.
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import httpx

from app.db.models import JobSourceRecord
from app.services.connectors.base import (
    BaseJobConnector,
    ConnectorFetchResult,
    HealthCheckResult,
    RawJobPayload,
)

USER_AGENT = "RIGHT-FIT-Career-Intelligence/1.0 (+https://rightfit.platform)"


class GreenhouseConnector(BaseJobConnector):
    """Connector for official Greenhouse public job board JSON API."""

    @property
    def provider_name(self) -> str:
        return "greenhouse"

    def _build_api_url(self, base_url: str) -> str:
        """Converts provided board URL or slug into canonical boards-api URL with content=true."""
        clean = base_url.strip()
        if "boards-api.greenhouse.io" in clean:
            if "content=true" not in clean:
                separator = "&" if "?" in clean else "?"
                return f"{clean}{separator}content=true"
            return clean

        # If user passed board page: https://boards.greenhouse.io/{board_token}
        if "boards.greenhouse.io" in clean:
            parsed = urlparse(clean)
            parts = [p for p in parsed.path.split("/") if p]
            token = parts[0] if parts else clean
            return f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

        # If raw slug / token passed
        token = clean.strip("/")
        return f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates board URL format."""
        if not base_url or len(base_url.strip()) < 2:
            raise ValueError("Greenhouse base_url or board token is required")

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Checks availability of Greenhouse public board API."""
        api_url = self._build_api_url(source.base_url)
        # Use simpler URL without content=true for fast ping
        health_url = api_url.replace("content=true", "")
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.get(health_url)
                latency = (time.time() - start_time) * 1000.0
                resp.raise_for_status()
                return HealthCheckResult(
                    healthy=True,
                    status_code=resp.status_code,
                    latency_ms=round(latency, 2),
                    message="Greenhouse board API reachable and responsive"
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
        """Pulls raw jobs from Greenhouse public JSON API."""
        api_url = self._build_api_url(source.base_url)

        async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
            resp = await client.get(api_url)
            resp.raise_for_status()
            data = resp.json()

        jobs_data = data.get("jobs", []) if isinstance(data, dict) else []
        records: List[RawJobPayload] = []

        for item in jobs_data[:limit]:
            ext_id = str(item.get("id"))
            listing_url = item.get("absolute_url") or f"{api_url}#{ext_id}"

            # Parse updated_at timestamp if present
            updated_at = None
            raw_updated = item.get("updated_at")
            if raw_updated:
                try:
                    updated_at = datetime.fromisoformat(raw_updated.replace("Z", "+00:00"))
                except Exception:
                    updated_at = None

            records.append(
                RawJobPayload(
                    external_job_id=ext_id,
                    listing_url=listing_url,
                    raw_payload=item,
                    source_published_at=updated_at,
                    source_updated_at=updated_at,
                )
            )

        return ConnectorFetchResult(
            records=records,
            total_found=len(jobs_data),
            metadata={"board_api_url": api_url, "records_in_payload": len(jobs_data)}
        )
