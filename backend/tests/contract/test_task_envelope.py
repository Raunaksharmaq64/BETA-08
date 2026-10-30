"""
Contract Tests: Asynchronous Task Envelope Contract
Version: 1.0.0
"""

import pytest
from pydantic import ValidationError

from contracts.common.tasks import TaskEnvelope


def test_task_envelope_valid():
    """Verifies valid task envelope creation and serialization."""
    envelope = TaskEnvelope(
        task_id="task-uuid-88912",
        task_type="lead.discovery.scheduled",
        correlation_id="corr-lead-999",
        max_retries=5,
        timeout_seconds=600,
        payload={"query": "Accountants", "city": "Indore", "max_results": 50},
    )

    assert envelope.task_id == "task-uuid-88912"
    assert envelope.task_type == "lead.discovery.scheduled"
    assert envelope.correlation_id == "corr-lead-999"
    assert envelope.max_retries == 5
    assert envelope.timeout_seconds == 600
    assert envelope.payload["city"] == "Indore"

    dumped = envelope.model_dump(mode="json")
    assert dumped["task_type"] == "lead.discovery.scheduled"
    assert "created_at" in dumped


def test_task_envelope_validation():
    """Verifies that invalid retry count or missing required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        TaskEnvelope(
            task_id="task-123",
            task_type="job.ingest",
            correlation_id="corr-1",
            max_retries=-1,  # Must be >= 0
        )

