"""
Unit tests for Core-to-Startup Intelligence Adapter and Circuit Breaker
Phase: 10 — Startup Intelligence Integration
"""

import pytest
import time
from unittest.mock import AsyncMock, patch
import httpx

from app.integrations.startup_intelligence.adapter import (
    CircuitBreaker,
    CircuitState,
    StartupIntelligenceAdapter,
    StartupIntelligenceAuthError,
    StartupIntelligenceUnavailableError,
)


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # 1 failure -> still closed
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1

    # 2 failures -> still closed
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # 3 failures -> trips to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Wait for recovery timeout -> transitions to HALF_OPEN on query
    time.sleep(0.25)
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Success in HALF_OPEN resets to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


@pytest.mark.asyncio
async def test_adapter_headers_and_correlation_id():
    adapter = StartupIntelligenceAdapter(
        base_url="http://localhost:8002",
        internal_service_key="test_secret_123"
    )
    headers = adapter._build_headers(correlation_id="corr-test-101")
    assert headers["Authorization"] == "Bearer test_secret_123"
    assert headers["X-Internal-Service-Key"] == "test_secret_123"
    assert headers["X-Service-Name"] == "rightfit-core"
    assert headers["X-Correlation-ID"] == "corr-test-101"


@pytest.mark.asyncio
async def test_adapter_circuit_breaker_open_fast_fails():
    adapter = StartupIntelligenceAdapter(base_url="http://localhost:8002")
    adapter.circuit_breaker.state = CircuitState.OPEN
    adapter.circuit_breaker.last_state_change = time.time()

    with pytest.raises(StartupIntelligenceUnavailableError) as exc_info:
        await adapter.list_leads()
    assert "Circuit Breaker OPEN" in str(exc_info.value)

