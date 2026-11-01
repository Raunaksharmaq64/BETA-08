"""
RIGHT FIT — Asynchronous Task Envelope Contract
Version: 1.0.0
Status: ACTIVE CONTRACT

Defines the serialized payload structure for messages placed onto
Redis Celery queues (career_tasks, lead_tasks, startup_tasks, notification_tasks).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class TaskEnvelope(BaseModel):
    """Universal asynchronous task message contract."""

    task_id: str = Field(..., description="Unique UUID identifying this task instance.")
    task_type: str = Field(..., description="Dot-separated task identifier (e.g., 'lead.discovery', 'resume.parse').")
    schema_version: str = Field(default="1.0", description="Contract schema version for payload evolution.")
    correlation_id: str = Field(..., description="Original client request correlation UUID.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO 8601 UTC timestamp when the task was dispatched."
    )
    max_retries: int = Field(default=3, ge=0, description="Maximum automated retry attempts on transient failure.")
    timeout_seconds: int = Field(default=300, ge=1, description="Worker execution timeout in seconds.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Typed arguments specific to the task type.")

