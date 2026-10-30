"""
Contract Tests: Standard API Response Envelope & Pagination
Version: 1.0.0
"""

import pytest
from pydantic import ValidationError

from contracts.common.envelope import PaginatedResponse, PaginationMeta, ResponseMeta, StandardResponse


def test_standard_response_envelope():
    """Verifies that StandardResponse generic envelope structures data and metadata correctly."""
    meta = ResponseMeta(request_id="req-123", service="core")
    resp = StandardResponse[dict](
        data={"user_id": "usr-456", "email": "test@example.com"},
        meta=meta,
    )

    assert resp.success is True
    assert resp.data["user_id"] == "usr-456"
    assert resp.meta.request_id == "req-123"
    assert resp.meta.service == "core"

    dumped = resp.model_dump(mode="json")
    assert dumped["success"] is True
    assert dumped["data"]["email"] == "test@example.com"
    assert "timestamp" in dumped["meta"]


def test_paginated_response_envelope():
    """Verifies that PaginatedResponse correctly validates pagination controls and items."""
    meta = ResponseMeta(request_id="req-paginated-1", service="core")
    pagination = PaginationMeta(
        total_records=120,
        limit=10,
        offset=20,
        has_next=True,
        has_prev=True,
    )
    items = [{"id": f"item-{i}"} for i in range(10)]

    resp = PaginatedResponse[dict](
        data=items,
        pagination=pagination,
        meta=meta,
    )

    assert resp.success is True
    assert len(resp.data) == 10
    assert resp.pagination.total_records == 120
    assert resp.pagination.has_next is True
    assert resp.pagination.has_prev is True


def test_pagination_meta_validation():
    """Verifies boundary constraints on pagination limits and negative offsets."""
    with pytest.raises(ValidationError):
        PaginationMeta(
            total_records=10,
            limit=0,  # ge=1 violated
            offset=0,
            has_next=False,
            has_prev=False,
        )

    with pytest.raises(ValidationError):
        PaginationMeta(
            total_records=10,
            limit=150,  # le=100 violated
            offset=0,
            has_next=False,
            has_prev=False,
        )

    with pytest.raises(ValidationError):
        PaginationMeta(
            total_records=-5,  # ge=0 violated
            limit=10,
            offset=0,
            has_next=False,
            has_prev=False,
        )

