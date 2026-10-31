"""
RIGHT FIT Core — Lever Public Postings API Connector
Version: 1.0.0
Phase: 5 / Master Implementation

Interacts with official public Lever Postings JSON APIs:
https://api.lever.co/v0/postings/{company_slug}?mode=json
Zero HTML scraping required; strictly permitted public API feed.
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


class LeverConnector(BaseJobConnector):
    """Connector for official Lever public postings JSON API."""

    @property
    def provider_name(self) -> str:
        return "lever"

    def _build_api_url(self, base_url: str) -> str:
        """Converts provided company URL or slug into canonical Lever postings API URL."""
        clean = base_url.strip()
        if "api.lever.co" in clean:
            separator = "&" if "?" in clean else "?"
            return f"{clean}{separator}mode=json" if "mode=json" not in clean else clean

        # If user passed jobs.lever.co/{company}
        if "jobs.lever.co" in clean:
            parsed = urlparse(clean)
            parts = [p for p in parsed.path.split("/") if p]
            token = parts[0] if parts else clean
            return f"https://api.lever.co/v0/postings/{token}?mode=json"

        # Raw company slug
        token = clean.strip("/")
        return f"https://api.lever.co/v0/postings/{token}?mode=json"

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates company slug or Lever URL."""
        if not base_url or len(base_url.strip()) < 2:
            raise ValueError("Lever company slug or URL is required")

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Checks availability of Lever public postings API."""
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
                    message="Lever Postings API accessible",
                )
        except httpx.HTTPStatusError as e:
            latency = (time.time() - start_time) * 1000.0
            return HealthCheckResult(
                healthy=False,
                status_code=e.response.status_code,
                latency_ms=round(latency, 2),
                message=f"Lever returned HTTP {e.response.status_code}",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000.0
            return HealthCheckResult(
                healthy=False,
                status_code=None,
                latency_ms=round(latency, 2),
                message=f"Lever connection failure: {str(e)}",
            )

    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls public postings from Lever JSON API."""
        api_url = self._build_api_url(source.base_url)

        async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
            resp = await client.get(api_url)
            resp.raise_for_status()
            data = resp.json()

        postings = data if isinstance(data, list) else []
        records: List[RawJobPayload] = []

        for item in postings[:limit]:
            ext_id = str(item.get("id") or item.get("text", "unknown"))
            apply_url = item.get("hostedUrl") or item.get("applyUrl") or ""

            created_at = None
            if item.get("createdAt"):
                try:
                    created_at = datetime.fromtimestamp(item["createdAt"] / 1000.0, tz=timezone.utc)
                except Exception:
                    created_at = None

            records.append(
                RawJobPayload(
                    external_job_id=ext_id,
                    listing_url=apply_url,
                    raw_payload=item,
                    source_published_at=created_at,
                    source_updated_at=created_at,
                )
            )

        return ConnectorFetchResult(
            records=records,
            total_found=len(postings),
            metadata={"lever_company": source.base_url, "fetched_count": len(records)},
        )

