"""
RIGHT FIT — Core-to-LeadHunter Service API Contract
Version: 1.0.0
Status: ACTIVE CONTRACT

Governs the versioned HTTP REST interface between Core Career Engine
and the independent LeadHunter AI satellite service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ScanJobStatus(StrEnum):
    """Lifecycle states of an asynchronous LeadHunter search scan."""

    QUEUED = "QUEUED"
    SCANNING = "SCANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class LeadDiscoveryRequest(BaseModel):
    """Payload sent by Core Backend to trigger a local business lead discovery scan."""

    query: str = Field(..., min_length=2, description="Target search query (e.g., 'Dentists', 'Accountants').")
    city: str = Field(..., min_length=2, description="Target city or metropolitan area (e.g., 'Austin, TX', 'Bhopal').")
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum number of business candidates to evaluate.")
    include_with_website: bool = Field(default=False, description="Whether to include businesses that already have functioning websites.")
    deep_scan: bool = Field(default=True, description="Whether to perform subpage crawling for owner email & social links.")


class LeadSummary(BaseModel):
    """Normalized business lead candidate returned by LeadHunter."""

    lead_id: str = Field(..., description="LeadHunter unique identifier for the lead record.")
    business_name: str = Field(..., description="Name of the business.")
    category: str = Field(..., description="Business category.")
    city: str = Field(..., description="Target city.")
    website: Optional[str] = Field(default=None, description="Discovered website URL, if any.")
    is_broken_website: bool = Field(default=False, description="True if website failed DNS, SSL, or HTTP status tests.")
    phone: Optional[str] = Field(default=None, description="Business phone number.")
    email: Optional[str] = Field(default=None, description="Discovered contact email.")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Google Maps star rating.")
    reviews_count: int = Field(default=0, ge=0, description="Total review count on Google Maps.")
    suggested_pitch: Optional[str] = Field(default=None, description="AI-drafted outreach pitch.")


class LeadDiscoveryStatus(BaseModel):
    """Status response for an ongoing or completed discovery scan."""

    discovery_id: str = Field(..., description="Tracking UUID for the scan job.")
    status: ScanJobStatus = Field(..., description="Current scan lifecycle state.")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="Completion percentage (0-100).")
    total_found: int = Field(default=0, ge=0, description="Total business entities identified so far.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when discovery job was scheduled."
    )
    completed_at: Optional[datetime] = Field(default=None, description="Timestamp when job finished.")
    error_message: Optional[str] = Field(default=None, description="Failure diagnostic message if FAILED.")


class LeadDiscoveryResult(BaseModel):
    """Collection response containing leads discovered by a scan."""

    discovery_id: str = Field(..., description="Tracking UUID for the scan job.")
    leads: List[LeadSummary] = Field(default_factory=list, description="List of qualified business leads.")
    total_leads: int = Field(..., ge=0, description="Total count of leads returned.")


class WebsiteAuditReport(BaseModel):
    """Detailed technical health findings for a specific business website."""

    url: str = Field(..., description="Audited website URL.")
    dns_resolves: bool = Field(..., description="Whether domain resolves to valid IP address.")
    ssl_valid: bool = Field(..., description="Whether SSL/TLS certificate is active and valid.")
    http_status: Optional[int] = Field(default=None, description="HTTP response status code (e.g. 200, 404, 502).")
    load_time_seconds: Optional[float] = Field(default=None, description="Page latency in seconds.")
    mobile_friendly: bool = Field(default=False, description="Whether responsive viewport tags are configured.")
    tech_stack: List[str] = Field(default_factory=list, description="Detected CMS or frameworks (e.g., WordPress, React).")
    issues: List[str] = Field(default_factory=list, description="Human-readable technical deficiencies flagged.")


class LeadDetailResponse(BaseModel):
    """Comprehensive detail for a single business lead."""

    lead: LeadSummary = Field(..., description="Core business lead details.")
    audit: Optional[WebsiteAuditReport] = Field(default=None, description="Technical health audit details.")
    instagram: Optional[str] = Field(default=None, description="Discovered Instagram profile URL.")
    facebook: Optional[str] = Field(default=None, description="Discovered Facebook page URL.")

