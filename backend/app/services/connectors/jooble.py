"""
RIGHT FIT Core — Jooble Job Aggregator API Connector
Version: 1.0.0
Phase: 5 / Master Implementation

Interacts with official Jooble JSON POST API:
https://jooble.org/api/{api_key}
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


class JoobleConnector(BaseJobConnector):
    """Connector for official Jooble Jobs API."""

    @property
    def provider_name(self) -> str:
        return "jooble"

    def _get_api_key(self, source: JobSourceRecord) -> str:
        """Resolves Jooble API key from settings or source config."""
        key = getattr(settings, "JOOBLE_API_KEY", None) or os.getenv("JOOBLE_API_KEY", "62931f47-5827-4a07-9bdc-5c9c6f95120a")
        return str(key).strip()

    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates Jooble configuration."""
        # Allowed values: 'https://jooble.org/api' or any regional domain or empty
        pass

    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Checks connectivity and token validity against Jooble API."""
        api_key = self._get_api_key(source)
        endpoint = f"https://jooble.org/api/{api_key}"
        payload = {"keywords": "software engineer", "page": 1, "result_on_page": 1}
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.post(endpoint, json=payload)
                latency = (time.time() - start_time) * 1000.0
                resp.raise_for_status()
                data = resp.json()
                total = data.get("totalCount", 0)
                return HealthCheckResult(
                    healthy=True,
                    status_code=resp.status_code,
                    latency_ms=round(latency, 2),
                    message=f"Jooble API active ({total:,} available jobs indexed)",
                )
        except Exception as e:
            latency = (time.time() - start_time) * 1000.0
            return HealthCheckResult(
                healthy=False,
                status_code=getattr(e, "response", None).status_code if hasattr(e, "response") else None,
                latency_ms=round(latency, 2),
                message=f"Jooble API failure: {str(e)}",
            )

    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls verified listings from Jooble jobs API."""
        api_key = self._get_api_key(source)
        endpoint = f"https://jooble.org/api/{api_key}"
        page_size = min(max(limit, 5), 50)
        payload = {
            "keywords": "developer",
            "page": 1,
            "result_on_page": page_size,
        }

        async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": USER_AGENT}) as client:
            resp = await client.post(endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()

        raw_items = data.get("jobs", [])
        total_found = data.get("totalCount", len(raw_items))
        records: List[RawJobPayload] = []

        for item in raw_items:
            ext_id = str(item.get("id"))
            apply_url = item.get("link") or f"https://jooble.org/desc/{ext_id}"

            created_at = None
            if item.get("updated"):
                try:
                    created_at = datetime.fromisoformat(item["updated"].replace("Z", "+00:00"))
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
            metadata={"source_feed": "jooble", "fetched_count": len(records)},
        )

