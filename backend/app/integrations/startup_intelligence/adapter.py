"""
RIGHT FIT Core — Startup Intelligence Service Integration Adapter
Version: 1.0.0
Phase: 10 — Startup Intelligence Integration

Provides an authenticated, resilient HTTP client interface to the independent
Startup Intelligence satellite service (Port 8002 / STARTUP_INTELLIGENCE_BASE_URL).
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

logger = logging.getLogger(__name__)


class CircuitState(StrEnum):
    CLOSED = "CLOSED"        # Normal operation
    OPEN = "OPEN"            # Failing, fast-reject requests
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
            logger.info("[CircuitBreaker] Startup Intelligence service recovered. Circuit state -> CLOSED")
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


class StartupIntelligenceUnavailableError(Exception):
    """Raised when Startup Intelligence is offline, timing out, or circuit breaker is OPEN."""
    pass


class StartupIntelligenceAuthError(Exception):
    """Raised when service-to-service authentication is rejected."""
    pass


class StartupIntelligenceAdapter:
    """Authenticated Core Adapter for the Startup Intelligence Satellite Service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        internal_service_key: Optional[str] = None,
        connect_timeout: float = 3.0,
        read_timeout: float = 10.0,
        max_retries: int = 2,
    ):
        self.base_url = (base_url or getattr(settings, "STARTUP_INTELLIGENCE_BASE_URL", "http://localhost:8002")).rstrip("/")
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
    ) -> Any:
        """Executes an authenticated HTTP request with circuit-breaker protection and jittered retry."""
        if not self.circuit_breaker.can_execute():
            logger.warning("[StartupIntelligenceAdapter] Circuit breaker is OPEN. Fast-failing request.")
            raise StartupIntelligenceUnavailableError(
                "Startup Intelligence service is temporarily unreachable (Circuit Breaker OPEN). Degraded mode active."
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
                    logger.warning(f"[StartupIntelligenceAdapter] Upstream server error {resp.status_code} on attempt {attempt}")
                    self.circuit_breaker.record_failure()
                    if attempt <= self.max_retries:
                        backoff = (2 ** (attempt - 1)) * 0.5 + random.uniform(0.1, 0.3)
                        await asyncio.sleep(backoff)
                        continue
                    resp.raise_for_status()

                if resp.status_code in (401, 403):
                    logger.error(f"[StartupIntelligenceAdapter] Authentication failure {resp.status_code} against Startup Intelligence.")
                    raise StartupIntelligenceAuthError(f"Startup Intelligence authentication rejected: {resp.text}")

                if resp.status_code >= 400:
                    resp.raise_for_status()

                data = resp.json()
                self.circuit_breaker.record_success()
                return data

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exception = exc
                logger.warning(f"[StartupIntelligenceAdapter] Network exception on attempt {attempt}: {exc}")
                self.circuit_breaker.record_failure()
                if attempt <= self.max_retries:
                    backoff = (2 ** (attempt - 1)) * 0.5 + random.uniform(0.1, 0.3)
                    await asyncio.sleep(backoff)
                else:
                    break
            except (StartupIntelligenceAuthError, StartupIntelligenceUnavailableError):
                raise
            except Exception as exc:
                last_exception = exc
                self.circuit_breaker.record_failure()
                break

        raise StartupIntelligenceUnavailableError(
            f"Failed to communicate with Startup Intelligence at {url}: {last_exception}"
        ) from last_exception

    async def get_health(self, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Queries the health check endpoint of Startup Intelligence."""
        try:
            return await self._request_with_retry("GET", "/health", correlation_id=correlation_id)
        except Exception as exc:
            logger.warning(f"[StartupIntelligenceAdapter] Health check failed: {exc}")
            return {
                "status": "degraded",
                "circuit_state": self.circuit_breaker.state.value,
                "error": str(exc),
            }

    async def list_leads(
        self,
        category: Optional[str] = None,
        min_score: Optional[int] = None,
        source: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        correlation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves raw startup problem leads from Startup Intelligence."""
        params: Dict[str, Any] = {}
        if category and category != "All":
            params["category"] = category
        if min_score is not None:
            params["min_score"] = min_score
        if source and source != "All":
            params["source"] = source
        if limit is not None:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        res = await self._request_with_retry("GET", "/api/leads", params=params, correlation_id=correlation_id)
        if isinstance(res, list):
            return res
        return []

    async def get_lead_by_id(
        self,
        lead_id: str,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetches detailed record of a single lead from Startup Intelligence."""
        return await self._request_with_retry("GET", f"/api/leads/{lead_id}", correlation_id=correlation_id)

    async def trigger_feed_scrape(
        self,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Triggers live feed scraping scan across all active startup platforms."""
        return await self._request_with_retry("POST", "/api/scrape/feeds", payload={}, correlation_id=correlation_id)

    async def analyze_lead(
        self,
        lead_id: str,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Triggers AI technical audit and deep analysis on a specific lead."""
        payload = {"id": lead_id}
        return await self._request_with_retry("POST", "/api/leads/analyze", payload=payload, correlation_id=correlation_id)

