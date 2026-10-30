"""
RIGHT FIT Core — Resilience, Rate Limiting & Circuit Breaker Engine
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Provides:
- 3-State Circuit Breaker (CLOSED, OPEN, HALF_OPEN)
- Per-source sliding-window rate limiting
- Transient error classification & exponential backoff with jitter
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple, TypeVar

from app.services.rate_limiter import SlidingWindowRateLimiter

logger = logging.getLogger("rightfit.resilience")

T = TypeVar("T")


class CircuitOpenException(Exception):
    """Raised when an operation is attempted while circuit breaker is OPEN."""
    def __init__(self, message: str, cooldown_until: Optional[datetime] = None) -> None:
        super().__init__(message)
        self.cooldown_until = cooldown_until


class RateLimitExceededException(Exception):
    """Raised when source request rate limit quota is exhausted."""
    def __init__(self, message: str, retry_after: int = 1) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreakerManager:
    """Manages the 3-state circuit breaker lifecycle for external sources."""

    @staticmethod
    def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
        """Ensures datetime is timezone-aware in UTC."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @classmethod
    def can_execute(
        cls,
        circuit_state: str,
        cooldown_until: Optional[datetime],
        force: bool = False
    ) -> Tuple[bool, str, Optional[str]]:
        """Determines if execution is permitted based on circuit state.

        Returns:
            (allowed: bool, effective_state: str, reason: Optional[str])
        """
        now = datetime.now(timezone.utc)
        state = circuit_state.upper() if circuit_state else "CLOSED"

        if state == "CLOSED":
            return True, "CLOSED", None

        aware_cooldown = cls.ensure_utc(cooldown_until)

        if state == "OPEN":
            if force:
                return True, "HALF_OPEN", "Forced execution trial"
            if aware_cooldown and now >= aware_cooldown:
                # Cooldown expired, transition to trial state
                return True, "HALF_OPEN", None
            return False, "OPEN", f"Circuit is OPEN. Cooldown expires at {aware_cooldown}"

        if state == "HALF_OPEN":
            return True, "HALF_OPEN", None

        # Fallback to CLOSED
        return True, "CLOSED", None

    @classmethod
    def record_success(
        cls,
        current_state: str,
        consecutive_failures: int
    ) -> Tuple[str, int, Optional[datetime]]:
        """Updates circuit state upon successful operation.

        Returns:
            (new_state: str, consecutive_failures: int, cooldown_until: Optional[datetime])
        """
        return "CLOSED", 0, None

    @classmethod
    def record_failure(
        cls,
        current_state: str,
        consecutive_failures: int,
        threshold: int = 3,
        cooldown_seconds: float = 60.0
    ) -> Tuple[str, int, Optional[datetime]]:
        """Updates circuit state upon failed operation.

        Returns:
            (new_state: str, consecutive_failures: int, cooldown_until: Optional[datetime])
        """
        now = datetime.now(timezone.utc)
        new_failures = consecutive_failures + 1

        if current_state.upper() == "HALF_OPEN" or new_failures >= threshold:
            cooldown_until = now + timedelta(seconds=cooldown_seconds)
            return "OPEN", new_failures, cooldown_until

        return "CLOSED", new_failures, None


class RetryPolicy:
    """Calculates backoff delays and classifies retryable vs non-retryable errors."""

    @staticmethod
    def is_transient_error(exc: Exception) -> bool:
        """Determines if an exception is transient (network, timeout, 429, 5xx)."""
        import httpx

        if isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError, TimeoutError)):
            return True
        if isinstance(exc, (httpx.NetworkError, ConnectionError)):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            if status == 429 or status in (500, 502, 503, 504):
                return True
            return False

        # Generic exceptions with retryable keywords
        msg = str(exc).lower()
        if any(term in msg for term in ("timeout", "connection reset", "broken pipe", "rate limit", "too many requests")):
            return True

        return False

    @staticmethod
    def calculate_delay(
        attempt: int,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        factor: float = 2.0,
        jitter: bool = True
    ) -> float:
        """Calculates exponential backoff delay with jitter."""
        delay = min(max_delay, base_delay * (factor ** attempt))
        if jitter:
            jitter_amount = random.uniform(0, 0.25 * delay)
            delay += jitter_amount
        return delay

    @classmethod
    async def execute_with_retry(
        cls,
        coro_fn: Callable[[], Coroutine[Any, Any, T]],
        max_attempts: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0
    ) -> T:
        """Executes coroutine with exponential backoff on transient errors."""
        last_exception: Optional[Exception] = None

        for attempt in range(max(1, max_attempts)):
            try:
                return await coro_fn()
            except Exception as exc:
                last_exception = exc
                if not cls.is_transient_error(exc) or attempt == max_attempts - 1:
                    logger.warning(f"Operation failed on attempt {attempt + 1}/{max_attempts}: {exc} (non-retryable or max attempts)")
                    raise exc

                delay = cls.calculate_delay(attempt, base_delay=base_delay, max_delay=max_delay)
                logger.info(f"Transient error on attempt {attempt + 1}: {exc}. Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)

        assert last_exception is not None
        raise last_exception


class SourceRateLimiter:
    """Sliding-window rate limiter per source."""

    def __init__(self) -> None:
        self._limiter = SlidingWindowRateLimiter()

    def acquire(self, source_id: str, limit_per_minute: int) -> Tuple[bool, int]:
        """Checks if a request slot is available for this source.

        Returns:
            (allowed: bool, retry_after_seconds: int)
        """
        key = f"source_rate_limit:{source_id}"
        return self._limiter.is_allowed(key, max_requests=limit_per_minute, window_seconds=60)

    def reset(self, source_id: str) -> None:
        """Resets rate limit counter for source."""
        key = f"source_rate_limit:{source_id}"
        self._limiter.reset(key)


# Global resilience instances
source_rate_limiter = SourceRateLimiter()
circuit_breaker = CircuitBreakerManager()
