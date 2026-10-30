"""
Contract Tests: Service Identity & Inter-Service Authentication
Version: 1.0.0
"""

import pytest
from pydantic import ValidationError

from contracts.auth.service_identity import ServiceAuthHeaders, ServiceIdentity, ServiceName, ServiceScope


def test_service_identity_model():
    """Verifies internal service identity attributes and permission scopes."""
    identity = ServiceIdentity(
        service_name=ServiceName.CORE_ENGINE,
        is_authenticated=True,
        scopes=[
            ServiceScope.READ_OPPORTUNITIES,
            ServiceScope.TRIGGER_DISCOVERY,
            ServiceScope.READ_DISCOVERY,
        ],
        client_version="1.0.0",
    )

    assert identity.service_name == ServiceName.CORE_ENGINE
    assert identity.is_authenticated is True
    assert ServiceScope.TRIGGER_DISCOVERY in identity.scopes
    assert identity.client_version == "1.0.0"


def test_service_auth_headers_validation():
    """Verifies that inter-service HTTP headers validate correctly."""
    headers = ServiceAuthHeaders(
        x_request_id="trace-corr-12345",
        x_service_source=ServiceName.CORE_ENGINE,
        x_internal_service_key="internal_shared_secret_token",
    )

    assert headers.x_request_id == "trace-corr-12345"
    assert headers.x_service_source == ServiceName.CORE_ENGINE
    assert headers.x_internal_service_key == "internal_shared_secret_token"


def test_invalid_service_source_rejected():
    """Verifies that unknown service names are rejected by enum validation."""
    with pytest.raises(ValidationError):
        ServiceAuthHeaders(
            x_request_id="trace-corr-12345",
            x_service_source="untrusted_external_bot",  # Invalid enum value
            x_internal_service_key="token",
        )

