"""
RIGHT FIT — Standard API Error Contract
Version: 1.0.0
Status: ACTIVE CONTRACT

Defines the universal error envelope returned by all RIGHT FIT services
(Core Career Engine, LeadHunter AI, Startup Intelligence).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    """Stable, machine-readable error codes."""

    # Client-side errors (4xx)
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    UNAUTHORIZED = "UNAUTHORIZED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    IDEMPOTENCY_VIOLATION = "IDEMPOTENCY_VIOLATION"

    # Upstream / Server errors (5xx)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    UPSTREAM_SERVICE_ERROR = "UPSTREAM_SERVICE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    UPSTREAM_TIMEOUT = "UPSTREAM_TIMEOUT"


class ErrorDetail(BaseModel):
    """Field-level issue description."""

    field: Optional[str] = Field(default=None, description="Request field causing the error, if applicable.")
    issue: str = Field(..., description="Human-readable explanation of the issue.")
    rejected_value: Optional[Any] = Field(default=None, description="The value that failed validation, if safe to expose.")


class ErrorPayload(BaseModel):
    """Inner error container."""

    code: ErrorCode = Field(..., description="Stable, machine-readable error classification code.")
    message: str = Field(..., description="Human-readable explanation of the error.")
    details: List[ErrorDetail] = Field(default_factory=list, description="List of granular field-level issues.")
    request_id: str = Field(..., description="Unique correlation UUID identifying the request trace.")
    service: str = Field(..., description="Identifier of the service where the error occurred (e.g. 'core', 'leadhunter', 'startup_intel').")
    retryable: bool = Field(default=False, description="Whether the client may safely retry the operation with exponential backoff.")


class APIErrorResponse(BaseModel):
    """Universal error response envelope."""

    success: bool = Field(default=False, description="Always false for error responses.")
    error: ErrorPayload = Field(..., description="Standardized error details container.")

