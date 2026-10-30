"""
RIGHT FIT Core — Connectors Package
"""

from app.services.connectors.ashby import AshbyConnector
from app.services.connectors.base import (
    BaseJobConnector,
    ConnectorFetchResult,
    HealthCheckResult,
    RawJobPayload,
)
from app.services.connectors.greenhouse import GreenhouseConnector
from app.services.connectors.registry import get_connector, list_supported_providers
from app.services.connectors.synthetic import SyntheticJobConnector

__all__ = [
    "AshbyConnector",
    "BaseJobConnector",
    "ConnectorFetchResult",
    "GreenhouseConnector",
    "HealthCheckResult",
    "RawJobPayload",
    "SyntheticJobConnector",
    "get_connector",
    "list_supported_providers",
]
