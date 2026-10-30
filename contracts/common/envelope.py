"""
RIGHT FIT — Standard API Response Envelope & Pagination
Version: 1.0.0
Status: ACTIVE CONTRACT
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata attached to every standard API response."""

    request_id: str = Field(..., description="Unique correlation UUID identifying the request trace.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO 8601 UTC timestamp when the response was generated."
    )
    service: str = Field(default="core", description="Identifier of the responding service.")


class PaginationMeta(BaseModel):
    """Pagination details for list/collection endpoints."""

    total_records: int = Field(..., ge=0, description="Total number of items matching the query.")
    limit: int = Field(..., ge=1, le=100, description="Maximum number of items returned in this page.")
    offset: int = Field(..., ge=0, description="Offset index of the first record in this page.")
    has_next: bool = Field(..., description="Whether additional records exist after this page.")
    has_prev: bool = Field(..., description="Whether records exist prior to this offset.")


class StandardResponse(BaseModel, Generic[T]):
    """Standard success envelope for single resource responses."""

    success: bool = Field(default=True, description="Always true for success responses.")
    data: T = Field(..., description="Payload data object.")
    meta: ResponseMeta = Field(..., description="Traceability and metadata block.")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard success envelope for paginated collection responses."""

    success: bool = Field(default=True, description="Always true for success responses.")
    data: List[T] = Field(default_factory=list, description="Array of collection items.")
    pagination: PaginationMeta = Field(..., description="Pagination control metadata.")
    meta: ResponseMeta = Field(..., description="Traceability and metadata block.")

