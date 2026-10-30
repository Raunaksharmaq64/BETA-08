"""
Contract Tests: Standard API Error Envelope
Version: 1.0.0
"""

import pytest
from pydantic import ValidationError

from contracts.common.errors import APIErrorResponse, ErrorCode, ErrorDetail, ErrorPayload


def test_standard_error_response_structure():
    """Verifies that APIErrorResponse creates the compliant JSON structure."""
    detail = ErrorDetail(
        field="query.limit",
        issue="Limit must not exceed 100",
        rejected_value=250,
    )
    payload = ErrorPayload(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed on 1 field.",
        details=[detail],
        request_id="req-uuid-test-001",
        service="core_career_engine",
        retryable=False,
    )
    error_response = APIErrorResponse(error=payload)

    # Success must always default to False
    assert error_response.success is False
    assert error_response.error.code == ErrorCode.VALIDATION_ERROR
    assert error_response.error.request_id == "req-uuid-test-001"
    assert len(error_response.error.details) == 1
    assert error_response.error.details[0].field == "query.limit"
    assert error_response.error.details[0].rejected_value == 250
    assert error_response.error.retryable is False

    # Check JSON output shape
    dumped = error_response.model_dump(mode="json")
    assert dumped["success"] is False
    assert dumped["error"]["code"] == "VALIDATION_ERROR"
    assert "service" in dumped["error"]
    assert "request_id" in dumped["error"]


def test_upstream_retryable_error():
    """Verifies retryable flag on upstream outage errors."""
    payload = ErrorPayload(
        code=ErrorCode.SERVICE_UNAVAILABLE,
        message="LeadHunter satellite service is currently unreachable.",
        details=[],
        request_id="req-uuid-timeout-503",
        service="leadhunter",
        retryable=True,
    )
    error_response = APIErrorResponse(error=payload)

    assert error_response.error.retryable is True
    assert error_response.error.code == ErrorCode.SERVICE_UNAVAILABLE


def test_all_standard_error_codes_exist():
    """Guarantees that all required error codes are defined in ErrorCode enum."""
    expected_codes = {
        "BAD_REQUEST",
        "VALIDATION_ERROR",
        "UNAUTHENTICATED",
        "UNAUTHORIZED",
        "RESOURCE_NOT_FOUND",
        "RESOURCE_CONFLICT",
        "RATE_LIMIT_EXCEEDED",
        "IDEMPOTENCY_VIOLATION",
        "INTERNAL_SERVER_ERROR",
        "UPSTREAM_SERVICE_ERROR",
        "SERVICE_UNAVAILABLE",
        "UPSTREAM_TIMEOUT",
    }
    actual_codes = {item.value for item in ErrorCode}
    assert expected_codes.issubset(actual_codes)

