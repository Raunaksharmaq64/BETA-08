"""
RIGHT FIT Core — Base Connector Specification & Data Types
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.models import JobSourceRecord


@dataclass
class HealthCheckResult:
    """Outcome of an external source health probe."""
    healthy: bool
    status_code: Optional[int] = None
    latency_ms: float = 0.0
    message: str = "OK"
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RawJobPayload:
    """Standard container for a fetched raw opportunity before normalization."""
    external_job_id: str
    listing_url: str
    raw_payload: Dict[str, Any]
    source_published_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None


@dataclass
class ConnectorFetchResult:
    """Result returned by a connector fetch execution."""
    records: List[RawJobPayload] = field(default_factory=list)
    total_found: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseJobConnector(ABC):
    """Abstract interface for all opportunity data connectors."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of provider adapter (e.g. 'greenhouse', 'ashby')."""
        pass

    @abstractmethod
    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates configuration parameters prior to registration.
        Raises ValueError or ValueError subclass if invalid.
        """
        pass

    @abstractmethod
    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Probes the source endpoint to verify reachability and HTTP status."""
        pass

    @abstractmethod
    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls raw listings from the source endpoint within limits.

        Returns:
            ConnectorFetchResult with standardized raw items.
        """
        pass
