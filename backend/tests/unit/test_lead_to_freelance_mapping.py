"""
Phase 9 Unit Tests — Lead to Freelance Opportunity Mapping & Evidence Rules
"""

import pytest
from app.services.freelance_service import freelance_service
from contracts.leads.models import LeadSummary


def test_broken_website_maps_to_verified_opportunity_and_repair_skills():
    lead = {
        "id": "lh_101",
        "name": "Apex Dental Clinic",
        "category": "Dentists",
        "city": "Austin",
        "website": "https://apexdentalclinic-broken.com",
        "is_broken_website": True,
        "rating": 4.6,
        "reviews": 35,
        "phone": "+1-512-555-0199",
        "email": "dr_apex@gmail.com",
    }
    mapped = freelance_service.map_lead_to_opportunity_fields(lead)
    assert mapped["classification_state"] == "VERIFIED_OPPORTUNITY"
    assert "Website Restoration" in mapped["opportunity_title"] or "Website Technical" in mapped["suggested_service"]
    assert "SSL Configuration" in mapped["required_skills"]
    assert mapped["relevance_score"] >= 90.0
    assert mapped["is_broken_website"] is True


def test_missing_website_maps_to_new_website_opportunity():
    lead = LeadSummary(
        lead_id="lh_102",
        business_name="Green Valley Landscaping",
        category="Landscaping",
        city="Indore",
        website=None,
        is_broken_website=False,
        phone="+91-9876543210",
        rating=4.8,
        reviews_count=22,
    )
    mapped = freelance_service.map_lead_to_opportunity_fields(lead)
    assert mapped["classification_state"] == "VERIFIED_OPPORTUNITY"
    assert "New Modern Website" in mapped["opportunity_title"]
    assert "Domain & Hosting Setup" in mapped["required_skills"]
    assert mapped["website"] is None


def test_unknown_fields_remain_null_not_fabricated():
    lead = {
        "id": "lh_103",
        "name": "City Cleaners",
        "city": "Dallas",
        "website": None,
        "email": None,
        "phone": None,
    }
    mapped = freelance_service.map_lead_to_opportunity_fields(lead)
    # Verification of anti-hallucination requirement
    assert mapped["phone"] is None
    assert mapped["email"] is None
    assert mapped["website"] is None

