"""
RIGHT FIT Core — Adzuna Job Aggregator API Connector
Version: 1.0.0
Phase: 5 / Master Implementation

Interacts with official Adzuna REST API:
https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id={app_id}&app_key={app_key}
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.db.models import JobSourceRecord
from app.services.connectors.base import (
    BaseJobConnector,
    ConnectorFetchResult,
    HealthCheckResult,
    RawJobPayload,
)

USER_AGENT = "RIGHT-FIT-Career-Intelligence/1.0 (+https://rightfit.platform)"


class AdzunaConnector(BaseJobConnector):
    """Connector for official Adzuna Jobs REST API."""

    @property
    def provider_name(self) -> str:
        return "adzuna"

    def _get_credentials(self, source: JobSourceRecord) -> tuple[str, str]:
        """Resolves Adzuna app_id and app_key from settings or source config."""
        app_id = getattr(settings, "ADZUNA_APP_ID", None) or os.getenv("ADZUNA_APP_ID", "4d096737")
        app_key = getattr(settings, "ADZUNA_APP_KEY", None) or os.getenv("ADZUNA_APP_KEY", "3612fca6ffecd9ce96b304e690c39ddd")
        return str(app_id).strip(), str(app_key).strip()

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates Adzuna endpoint config."""
        if not base_url or len(base_url.strip()) < 2:
            raise ValueError("Adzuna country code or base URL is required (e.g. 'in' or 'https://api.adzuna.com')")

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Checks connectivity and credential validity against Adzuna API."""
        app_id, app_key = self._get_credentials(source)
        country = source.base_url.strip().lower() if len(source.base_url.strip()) == 2 else "in"
        api_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={app_id}&app_key={app_key}&results_per_page=1"
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.get(api_url)
                latency = (time.time() - start_time) * 1000.0
                resp.raise_for_status()
                data = resp.json()
                total = data.get("count", 0)
                return HealthCheckResult(
                    healthy=True,
                    status_code=resp.status_code,
                    latency_ms=round(latency, 2),
                    message=f"Adzuna API active ({total:,} available jobs in {country.upper()})",
                )
        except Exception as e:
            latency = (time.time() - start_time) * 1000.0
            return HealthCheckResult(
                healthy=False,
                status_code=getattr(e, "response", None).status_code if hasattr(e, "response") else None,
                latency_ms=round(latency, 2),
                message=f"Adzuna API failure: {str(e)}",
            )

    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls verified listings from Adzuna jobs API."""
        app_id, app_key = self._get_credentials(source)
        country = source.base_url.strip().lower() if len(source.base_url.strip()) == 2 else "in"
        page_size = min(max(limit, 5), 50)
        api_url = (
            f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            f"?app_id={app_id}&app_key={app_key}&results_per_page={page_size}&what=software"
        )

        async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
            resp = await client.get(api_url)
            resp.raise_for_status()
            data = resp.json()

        raw_items = data.get("results", [])
        total_found = data.get("count", len(raw_items))
        records: List[RawJobPayload] = []

        for item in raw_items:
            ext_id = str(item.get("id"))
            apply_url = item.get("redirect_url") or f"https://www.adzuna.in/jobs/details/{ext_id}"

            created_at = None
            if item.get("created"):
                try:
                    created_at = datetime.fromisoformat(item["created"].replace("Z", "+00:00"))
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
            total_found=total_found,
            metadata={"source_feed": "adzuna", "country": country, "fetched_count": len(records)},
        )

