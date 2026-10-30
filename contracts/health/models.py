"""
RIGHT FIT — Health & Readiness Check Contracts
Version: 1.0.0
Status: ACTIVE CONTRACT

Governs liveness and readiness probe specifications across all services.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class HealthStatus(StrEnum):
    """Service health state."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class LivenessResponse(BaseModel):
    """Response returned by /health/live."""

    status: HealthStatus = Field(default=HealthStatus.HEALTHY, description="Process operational status.")
    service: str = Field(..., description="Service identifier.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of probe execution."
    )


class DependencyHealth(BaseModel):
    """Health indicator for an individual subsystem dependency."""

    status: HealthStatus = Field(..., description="Health status of the dependency.")
    latency_ms: Optional[float] = Field(default=None, description="Round-trip check latency in milliseconds.")
    message: Optional[str] = Field(default=None, description="Diagnostic note (no secrets).")


class ReadinessResponse(BaseModel):
    """Response returned by /health/ready."""

    status: HealthStatus = Field(..., description="Overall readiness to accept user traffic.")
    service: str = Field(..., description="Service identifier.")
    dependencies: Dict[str, DependencyHealth] = Field(
        default_factory=dict,
        description="Status of critical dependencies (e.g. database, redis, satellites)."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of probe execution."
    )

