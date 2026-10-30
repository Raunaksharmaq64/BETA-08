"""
RIGHT FIT — Service Identity & Inter-Service Authentication Contract
Version: 1.0.0
Status: ACTIVE CONTRACT

Governs service-to-service authentication between Core Career Engine,
LeadHunter AI, and Startup Intelligence.
"""

from __future__ import annotations

from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field


class ServiceName(StrEnum):
    """Recognized internal services."""

    CORE_ENGINE = "core_engine"
    LEADHUNTER = "leadhunter"
    STARTUP_INTELLIGENCE = "startup_intelligence"
    FRONTEND_GATEWAY = "frontend_gateway"


class ServiceScope(StrEnum):
    """Permitted operation scopes for service credentials."""

    READ_OPPORTUNITIES = "opportunities:read"
    TRIGGER_DISCOVERY = "discovery:trigger"
    READ_DISCOVERY = "discovery:read"
    TRIGGER_OUTREACH = "outreach:trigger"
    READ_AUDIT = "audit:read"
    FULL_INTERNAL_ACCESS = "internal:all"


class ServiceIdentity(BaseModel):
    """Authenticated caller identity derived from internal token/key validation."""

    service_name: ServiceName = Field(..., description="Identity of the calling service.")
    is_authenticated: bool = Field(default=False, description="Whether credential verification succeeded.")
    scopes: List[ServiceScope] = Field(default_factory=list, description="Permitted operations for this caller.")
    client_version: Optional[str] = Field(default=None, description="Reported version of the calling service.")


class ServiceAuthHeaders(BaseModel):
    """Expected HTTP request headers for inter-service communication."""

    x_request_id: str = Field(..., description="Distributed correlation UUID.")
    x_service_source: ServiceName = Field(..., description="Calling service identifier.")
    x_internal_service_key: str = Field(..., description="Shared secret or JWT token for inter-service auth.")

