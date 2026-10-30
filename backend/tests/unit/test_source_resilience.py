"""
Unit Tests: Job Source Resilience & Circuit Breaker Engine
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.services.resilience import (
    CircuitBreakerManager,
    CircuitOpenException,
    RateLimitExceededException,
    RetryPolicy,
    SourceRateLimiter,
)


def test_circuit_breaker_closed_state():
    """Circuit breaker allows execution in CLOSED state."""
    allowed, state, reason = CircuitBreakerManager.can_execute("CLOSED", None)
    assert allowed is True
    assert state == "CLOSED"
    assert reason is None


def test_circuit_breaker_failure_transitions_to_open():
    """Consecutive failures reaching threshold transition circuit to OPEN."""
    state = "CLOSED"
    failures = 0

    # First failure
    state, failures, cooldown = CircuitBreakerManager.record_failure(state, failures, threshold=3, cooldown_seconds=60)
    assert state == "CLOSED"
    assert failures == 1
    assert cooldown is None

    # Second failure
    state, failures, cooldown = CircuitBreakerManager.record_failure(state, failures, threshold=3, cooldown_seconds=60)
    assert state == "CLOSED"
    assert failures == 2

    # Third failure -> Trip circuit to OPEN
    state, failures, cooldown = CircuitBreakerManager.record_failure(state, failures, threshold=3, cooldown_seconds=60)
    assert state == "OPEN"
    assert failures == 3
    assert cooldown is not None
    assert cooldown > datetime.now(timezone.utc)

    # OPEN circuit blocks execution
    allowed, effective, reason = CircuitBreakerManager.can_execute(state, cooldown)
    assert allowed is False
    assert effective == "OPEN"
    assert "Circuit is OPEN" in (reason or "")


def test_circuit_breaker_cooldown_transitions_to_half_open():
    """Expired cooldown allows trial execution in HALF_OPEN state."""
    # Past cooldown
    past_cooldown = datetime.now(timezone.utc) - timedelta(seconds=10)
    allowed, effective, reason = CircuitBreakerManager.can_execute("OPEN", past_cooldown)
    assert allowed is True
    assert effective == "HALF_OPEN"


def test_circuit_breaker_success_resets_to_closed():
    """Success in any state resets failure count and returns to CLOSED."""
    state, failures, cooldown = CircuitBreakerManager.record_success("HALF_OPEN", consecutive_failures=5)
    assert state == "CLOSED"
    assert failures == 0
    assert cooldown is None


def test_retry_policy_transient_error_classification():
    """Accurately classifies transient (retryable) vs permanent errors."""
    # Transient HTTP status codes
    req = httpx.Request("GET", "https://example.com")
    resp_503 = httpx.Response(503, request=req)
    resp_429 = httpx.Response(429, request=req)
    resp_502 = httpx.Response(502, request=req)
    resp_404 = httpx.Response(404, request=req)
    resp_401 = httpx.Response(401, request=req)

    assert RetryPolicy.is_transient_error(httpx.HTTPStatusError("503", request=req, response=resp_503)) is True
    assert RetryPolicy.is_transient_error(httpx.HTTPStatusError("429", request=req, response=resp_429)) is True
    assert RetryPolicy.is_transient_error(httpx.HTTPStatusError("502", request=req, response=resp_502)) is True

    # Non-transient HTTP status codes
    assert RetryPolicy.is_transient_error(httpx.HTTPStatusError("404", request=req, response=resp_404)) is False
    assert RetryPolicy.is_transient_error(httpx.HTTPStatusError("401", request=req, response=resp_401)) is False

    # Timeouts and network breaks
    assert RetryPolicy.is_transient_error(httpx.ReadTimeout("Timeout")) is True
    assert RetryPolicy.is_transient_error(ConnectionResetError("Connection reset")) is True
    assert RetryPolicy.is_transient_error(ValueError("Bad payload")) is False


def test_retry_policy_backoff_calculation():
    """Exponential delay increases with attempts and stays within bounds."""
    d0 = RetryPolicy.calculate_delay(0, base_delay=1.0, max_delay=10.0, jitter=False)
    d1 = RetryPolicy.calculate_delay(1, base_delay=1.0, max_delay=10.0, jitter=False)
    d2 = RetryPolicy.calculate_delay(2, base_delay=1.0, max_delay=10.0, jitter=False)

    assert d0 == 1.0
    assert d1 == 2.0
    assert d2 == 4.0

    # Delay capped at max_delay
    d10 = RetryPolicy.calculate_delay(10, base_delay=1.0, max_delay=10.0, jitter=False)
    assert d10 == 10.0


@pytest.mark.asyncio
async def test_retry_policy_execute_with_retry_success():
    """Executes coroutine, retrying transient failure before succeeding."""
    calls = 0

    async def transient_mock():
        nonlocal calls
        calls += 1
        if calls < 2:
            req = httpx.Request("GET", "https://example.com")
            resp = httpx.Response(503, request=req)
            raise httpx.HTTPStatusError("503", request=req, response=resp)
        return "SUCCESS"

    result = await RetryPolicy.execute_with_retry(transient_mock, max_attempts=3, base_delay=0.01)
    assert result == "SUCCESS"
    assert calls == 2


def test_source_rate_limiter_sliding_window():
    """Enforces quota within sliding window per source."""
    limiter = SourceRateLimiter()
    src_id = "test-source-rate"

    # Allow 2 requests
    allowed1, _ = limiter.acquire(src_id, limit_per_minute=2)
    allowed2, _ = limiter.acquire(src_id, limit_per_minute=2)
    assert allowed1 is True
    assert allowed2 is True

    # 3rd request blocked
    allowed3, retry_after = limiter.acquire(src_id, limit_per_minute=2)
    assert allowed3 is False
    assert retry_after > 0

    # Reset allows again
    limiter.reset(src_id)
    allowed4, _ = limiter.acquire(src_id, limit_per_minute=2)
    assert allowed4 is True
