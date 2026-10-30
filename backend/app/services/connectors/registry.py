"""
RIGHT FIT Core — Connector Registry
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

from typing import Dict, Type

from app.services.connectors.ashby import AshbyConnector
from app.services.connectors.base import BaseJobConnector
from app.services.connectors.greenhouse import GreenhouseConnector
from app.services.connectors.synthetic import SyntheticJobConnector

_REGISTRY: Dict[str, BaseJobConnector] = {
    "greenhouse": GreenhouseConnector(),
    "ashby": AshbyConnector(),
    "synthetic": SyntheticJobConnector(),
}


def get_connector(provider: str) -> BaseJobConnector:
    """Retrieves the connector adapter instance for the specified provider."""
    normalized = provider.strip().lower()
    connector = _REGISTRY.get(normalized)
    if not connector:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(f"Unsupported connector provider '{provider}'. Supported providers: {available}")
    return connector


def list_supported_providers() -> list[str]:
    """Returns sorted list of all active connector provider slugs."""
    return sorted(_REGISTRY.keys())
