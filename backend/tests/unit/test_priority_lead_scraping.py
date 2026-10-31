"""
Unit tests for Freelance Intelligence:
- Direct Local Discovery Collector
- Priority classification (HIGH, MEDIUM, LOW, IGNORE)
- SerpApi fallback resilience
- Database priority storage and priority filtering
"""

import pytest
from app.modules.freelance.collectors.base_collector import DiscoveredLead
from app.modules.freelance.collectors.direct_collector import DirectLocalDiscoveryCollector
from app.modules.freelance.collectors.serpapi_collector import SerpApiCollector
from app.modules.freelance.utils.data_cleaner import DataCleaner
from app.services.freelance_service import freelance_service
from app.db.models import FreelanceOpportunityRecord


def test_priority_assignment_rules():
    """Verify priority rules strictly adhere to LeadHunter logic."""
    # 1. Active website that is working -> LOW / IGNORE
    lead_working = DiscoveredLead(
        name="Working Dental",
        website="https://working-site.com",
        is_broken_website=False,
        phone="+91 98260 11111",
        reviews=20,
    )
    assert DataCleaner.assign_priority(lead_working) == "IGNORE"

    # 2. Broken website with phone & < 50 reviews -> HIGH
    lead_broken_high = DiscoveredLead(
        name="Broken Dental Urgent",
        website="http://broken-site-offline.com",
        is_broken_website=True,
        phone="+91 98260 11111",
        reviews=25,
    )
    assert DataCleaner.assign_priority(lead_broken_high) == "HIGH"

    # 3. No website with phone & < 50 reviews -> HIGH
    lead_no_site_high = DiscoveredLead(
        name="No Site High",
        website="",
        is_broken_website=False,
        phone="+91 98260 22222",
        reviews=15,
    )
    assert DataCleaner.assign_priority(lead_no_site_high) == "HIGH"

    # 4. No website with phone & 50-200 reviews -> MEDIUM
    lead_no_site_med = DiscoveredLead(
        name="No Site Medium",
        website="",
        is_broken_website=False,
        phone="+91 98260 33333",
        reviews=95,
    )
    assert DataCleaner.assign_priority(lead_no_site_med) == "MEDIUM"

    # 5. No website, no phone -> LOW
    lead_no_phone = DiscoveredLead(
        name="No Phone",
        website="",
        is_broken_website=False,
        phone="",
        reviews=10,
    )
    assert DataCleaner.assign_priority(lead_no_phone) == "LOW"


def test_direct_local_discovery_collector():
    """Verify DirectLocalDiscoveryCollector returns leads with valid attributes."""
    collector = DirectLocalDiscoveryCollector()
    leads = collector.search("Dentists", "Indore", max_results=6)
    assert len(leads) >= 5
    for l in leads:
        assert l.name
        assert l.city == "Indore"
        assert l.source == "Direct Local Discovery"


def test_serpapi_collector_fallback():
    """Verify SerpApiCollector seamlessly falls back to discovery when key is empty."""
    collector = SerpApiCollector(default_api_key="")
    leads = collector.search("Bakeries", "Austin", max_results=5)
    assert len(leads) >= 4
    for l in leads:
        assert l.name


def test_map_lead_to_opportunity_priority():
    """Verify map_lead_to_opportunity_fields sets priority properly."""
    fields = freelance_service.map_lead_to_opportunity_fields({
        "business_name": "Indore Smile Hub",
        "city": "Indore",
        "phone": "+91 98260 44444",
        "website": "",
        "reviews_count": 22,
    })
    assert fields["priority"] == "HIGH"
    assert fields["business_name"] == "Indore Smile Hub"
    assert fields["relevance_score"] == 95.0
