"""
Base Collector — Abstract interface and data models for business lead collectors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class DiscoveredLead:
    """Represents a single business lead discovered from an external provider."""
    name: str
    phone: str = ""
    address: str = ""
    website: str = ""
    rating: float = 0.0
    reviews: int = 0
    category: str = ""
    city: str = ""
    priority: str = "LOW"  # HIGH, MEDIUM, LOW, IGNORE
    whatsapp_number: str = ""
    place_id: str = ""
    source: str = "google_maps"
    instagram: str = ""
    facebook: str = ""
    is_broken_website: bool = False
    line_type: str = ""
    email: str = ""
    custom_pitch: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseCollector(ABC):
    """Abstract base class for all platform business collectors."""

    @abstractmethod
    def search(
        self,
        query: str,
        city: str,
        max_results: int = 20,
        exclude_place_ids: Optional[Set[str]] = None,
        start_offset: int = 0,
        api_key: Optional[str] = None,
    ) -> List[DiscoveredLead]:
        """Search for businesses on the platform."""
        pass

    @abstractmethod
    def get_details(self, place_id: str) -> Optional[DiscoveredLead]:
        """Get detailed information for a specific business."""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name of the platform."""
        pass
