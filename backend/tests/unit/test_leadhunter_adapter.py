"""
Phase 9 Unit Tests — LeadHunter Authenticated Adapter & Circuit Breaker
"""

import time
import pytest
from app.integrations.leadhunter.adapter import (
    CircuitBreaker,
    CircuitState,
    LeadHunterAdapter,
    LeadHunterUnavailableError,
)


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # 1st failure
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # 2nd failure
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # 3rd failure -> Trips to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Wait for recovery timeout
    time.sleep(0.25)
    # Probe request moves state to HALF_OPEN
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Success restores to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_adapter_attaches_auth_and_correlation_headers():
    adapter = LeadHunterAdapter(
        base_url="http://localhost:8001",
        internal_service_key="secret_test_key_123",
    )
    headers = adapter._build_headers(correlation_id="corr-test-999")
    assert headers["Authorization"] == "Bearer secret_test_key_123"
    assert headers["X-Internal-Service-Key"] == "secret_test_key_123"
    assert headers["X-Service-Name"] == "rightfit-core"
    assert headers["X-Correlation-ID"] == "corr-test-999"


@pytest.mark.asyncio
async def test_circuit_breaker_open_fast_fails_request():
    adapter = LeadHunterAdapter(base_url="http://127.0.0.1:9999")
    adapter.circuit_breaker.state = CircuitState.OPEN
    adapter.circuit_breaker.last_state_change = time.time()  # Recent, not expired

    with pytest.raises(LeadHunterUnavailableError) as exc_info:
        await adapter.search_leads(query="Plumbers", city="Austin")

    assert "Circuit Breaker OPEN" in str(exc_info.value)

