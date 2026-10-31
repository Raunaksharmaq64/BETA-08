"""
RIGHT FIT Core — RemoteOK Permitted Job Feed Connector
Version: 1.0.0
Phase: 5 / Master Implementation

Interacts with official public RemoteOK API endpoint:
https://remoteok.com/api
Zero HTML scraping required; strictly permitted public API feed.
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

USER_AGENT = "RIGHT-FIT-Career-Intelligence/1.0 (+https://rightfit.platform)"


class RemoteOKConnector(BaseJobConnector):
    """Connector for official RemoteOK public API."""

    @property
    def provider_name(self) -> str:
        return "remoteok"

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates base URL."""
        if not base_url or len(base_url.strip()) < 5:
            raise ValueError("RemoteOK base URL is required (e.g. 'https://remoteok.com/api')")

    def _resolve_api_url(self, base_url: Optional[str]) -> str:
        b = (base_url or "").strip() or "https://remoteok.com/api"
        if not b.endswith("/api"):
            return f"{b.rstrip('/')}/api"
        return b

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Checks availability of RemoteOK public endpoint."""
        url = self._resolve_api_url(source.base_url)
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.get(url)
                latency = (time.time() - start_time) * 1000.0
                resp.raise_for_status()
                return HealthCheckResult(
                    healthy=True,
                    status_code=resp.status_code,
                    latency_ms=round(latency, 2),
                    message="RemoteOK Feed accessible",
                )
        except Exception as e:
            latency = (time.time() - start_time) * 1000.0
            return HealthCheckResult(
                healthy=False,
                status_code=None,
                latency_ms=round(latency, 2),
                message=f"RemoteOK connection failure: {str(e)}",
            )

    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls public listings from RemoteOK feed."""
        url = self._resolve_api_url(source.base_url)

        async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        # RemoteOK first element is legal/disclaimer metadata dict
        raw_items = [d for d in data if isinstance(d, dict) and "id" in d] if isinstance(data, list) else []
        records: List[RawJobPayload] = []

        for item in raw_items[:limit]:
            ext_id = str(item.get("id"))
            apply_url = item.get("url") or f"https://remoteok.com/remote-jobs/{ext_id}"

            created_at = None
            if item.get("date"):
                try:
                    created_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
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
            total_found=len(raw_items),
            metadata={"source_feed": "remoteok", "fetched_count": len(records)},
        )

