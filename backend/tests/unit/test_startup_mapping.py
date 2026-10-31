"""
Unit tests for Startup Lead Mapping and Evidence Separation
Phase: 10 — Startup Intelligence Integration
"""

import pytest
from app.services.startup_service import classify_source_type, extract_domain


def test_classify_source_types():
    assert classify_source_type("GitHub Help Wanted") == "OFFICIAL_API"
    assert classify_source_type("Reddit RSS (/r/saas)") == "OFFICIAL_FEED"
    assert classify_source_type("Product Hunt Launches") == "OFFICIAL_FEED"
    assert classify_source_type("Hacker News Newest") == "OFFICIAL_FEED"
    assert classify_source_type("DuckDuckGo Search") == "DISCOVERY_ONLY"
    assert classify_source_type("IndieHackers") == "DISCOVERY_ONLY"
    assert classify_source_type("Website Technical Audit") == "PERMITTED_PUBLIC_SOURCE"


def test_extract_domain():
    assert extract_domain("https://www.example.com/blog?p=1") == "example.com"
    assert extract_domain("http://sub.startup.io/app") == "sub.startup.io"
    assert extract_domain("devship.co") == "devship.co"
    assert extract_domain(None) is None
    assert extract_domain("") is None

