"""
RIGHT FIT Core — LeadHunter Service Integration Adapter
Version: 1.0.0
Phase: 9 — LeadHunter Integration

Provides an authenticated, resilient HTTP client interface to the independent
LeadHunter AI service (Port 8001 / LEADHUNTER_BASE_URL).
Implements Circuit Breaker, Exponential Backoff with Jitter, and Degraded State Fallbacks.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from contracts.leads.models import (
    LeadDetailResponse,
    LeadDiscoveryRequest,
    LeadDiscoveryResult,
    LeadSummary,
    ScanJobStatus,
)

logger = logging.getLogger(__name__)


class CircuitState(StrEnum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, fast-reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout: float = 30.0  # seconds
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_state_change: float = field(default_factory=time.time)

    def record_success(self) -> None:
        self.failure_count = 0
        if self.state != CircuitState.CLOSED:
            logger.info("[CircuitBreaker] LeadHunter service recovered. Circuit state -> CLOSED")
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold and self.state == CircuitState.CLOSED:
            logger.warning(
                f"[CircuitBreaker] Threshold reached ({self.failure_count}/{self.failure_threshold}). "
                f"Tripping circuit to OPEN."
            )
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_state_change
            if elapsed >= self.recovery_timeout:
                logger.info("[CircuitBreaker] Recovery timeout expired. Testing probe -> HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()
                return True
            return False
        # In HALF_OPEN, allow probe attempt
        return True


class LeadHunterAdapter:
    """Authenticated Core Adapter for the LeadHunter AI Service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        internal_service_key: Optional[str] = None,
        connect_timeout: float = 3.0,
        read_timeout: float = 10.0,
        max_retries: int = 2,
    ):
        self.base_url = (base_url or getattr(settings, "LEADHUNTER_BASE_URL", "http://localhost:8001")).rstrip("/")
        self.internal_service_key = internal_service_key or getattr(
            settings, "INTERNAL_SERVICE_KEY", "rightfit_internal_shared_secret_key_123"
        )
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries
        self.circuit_breaker = CircuitBreaker()

    def _build_headers(self, correlation_id: Optional[str] = None) -> Dict[str, str]:
        cid = correlation_id or str(uuid.uuid4())
        return {
            "Authorization": f"Bearer {self.internal_service_key}",
            "X-Internal-Service-Key": self.internal_service_key,
            "X-Service-Name": "rightfit-core",
            "X-Correlation-ID": cid,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Executes an authenticated HTTP request with circuit-breaker protection and jittered retry."""
        if not self.circuit_breaker.can_execute():
            logger.warning("[LeadHunterAdapter] Circuit breaker is OPEN. Fast-failing request.")
            raise LeadHunterUnavailableError(
                "LeadHunter service is temporarily unreachable (Circuit Breaker OPEN). Degraded mode active."
            )

        url = f"{self.base_url}{path}"
        headers = self._build_headers(correlation_id)
        timeout = httpx.Timeout(connect=self.connect_timeout, read=self.read_timeout, write=5.0, pool=5.0)

        attempt = 0
        last_exception = None

        while attempt <= self.max_retries:
            attempt += 1
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    if method.upper() == "GET":
                        resp = await client.get(url, headers=headers, params=params)
                    elif method.upper() == "POST":
                        resp = await client.post(url, headers=headers, json=payload, params=params)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                # Check HTTP status
                if resp.status_code >= 500:
                    logger.warning(f"[LeadHunterAdapter] Upstream server error {resp.status_code} on attempt {attempt}")
                    self.circuit_breaker.record_failure()
                    if attempt <= self.max_retries:
                        backoff = (2 ** (attempt - 1)) * 0.5 + random.uniform(0.1, 0.3)
                        await asyncio.sleep(backoff)
                        continue
                    resp.raise_for_status()

                if resp.status_code == 401 or resp.status_code == 403:
                    logger.error(f"[LeadHunterAdapter] Authentication failure {resp.status_code} against LeadHunter.")
                    raise LeadHunterAuthError(f"LeadHunter authentication rejected: {resp.text}")

                if resp.status_code >= 400:
                    resp.raise_for_status()

                data = resp.json()
                self.circuit_breaker.record_success()
                return data

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exception = exc
                logger.warning(f"[LeadHunterAdapter] Network exception on attempt {attempt}: {exc}")
                self.circuit_breaker.record_failure()
                if attempt <= self.max_retries:
                    backoff = (2 ** (attempt - 1)) * 0.5 + random.uniform(0.1, 0.3)
                    await asyncio.sleep(backoff)
                else:
                    break
            except (LeadHunterAuthError, LeadHunterUnavailableError):
                raise
            except Exception as exc:
                last_exception = exc
                self.circuit_breaker.record_failure()
                break

        raise LeadHunterUnavailableError(
            f"Failed to communicate with LeadHunter at {url}: {last_exception}"
        ) from last_exception

    async def search_leads(
        self,
        query: str,
        city: str,
        max_results: int = 20,
        include_with_website: bool = False,
        deep_scan: bool = True,
        correlation_id: Optional[str] = None,
    ) -> LeadDiscoveryResult:
        """Triggers business search discovery scan in LeadHunter."""
        payload = {
            "query": query,
            "city": city,
            "max_results": max_results,
            "include_with_website": include_with_website,
            "deep_scan": deep_scan,
        }
        try:
            data = await self._request_with_retry(
                method="POST",
                path="/api/leads/search",
                payload=payload,
                correlation_id=correlation_id,
            )
            # Normalize LeadHunter response into standard contract
            leads_data = data.get("leads", [])
            leads = [
                LeadSummary(
                    lead_id=str(item.get("id") or item.get("lead_id", "")),
                    business_name=item.get("name") or item.get("business_name", ""),
                    category=item.get("category", "General"),
                    city=item.get("city", city),
                    website=item.get("website"),
                    is_broken_website=bool(item.get("is_broken_website", False)),
                    phone=item.get("phone"),
                    email=item.get("email"),
                    rating=float(item.get("rating", 0.0) or 0.0),
                    reviews_count=int(item.get("reviews", 0) or 0),
                    suggested_pitch=item.get("custom_pitch") or item.get("suggested_pitch"),
                )
                for item in leads_data
            ]
            return LeadDiscoveryResult(
                discovery_id=data.get("task_id", str(uuid.uuid4())),
                leads=leads,
                total_leads=len(leads),
            )
        except LeadHunterUnavailableError as e:
            logger.info(f"[LeadHunterAdapter] Fallback triggered: {e}")
            raise

    async def list_leads(
        self,
        city: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves existing saved leads from LeadHunter."""
        params = {"page": page, "per_page": per_page}
        if city:
            params["city"] = city
        if query:
            params["q"] = query

        return await self._request_with_retry(
            method="GET",
            path="/api/leads",
            params=params,
            correlation_id=correlation_id,
        )

    async def check_health(self) -> Dict[str, Any]:
        """Queries the LeadHunter health endpoint."""
        return await self._request_with_retry(method="GET", path="/health")


class LeadHunterUnavailableError(Exception):
    """Raised when LeadHunter service cannot be reached or circuit breaker is OPEN."""
    pass


class LeadHunterAuthError(Exception):
    """Raised when LeadHunter rejects service authentication credentials."""
    pass


# Global singleton instance
leadhunter_adapter = LeadHunterAdapter()

