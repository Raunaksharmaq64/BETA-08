"""
Phase 9 Unit Tests — Freelance Opportunity Import & Idempotent Deduplication
"""

import pytest
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.db.models import FreelanceOpportunityRecord, ContactEvidenceRecord
from app.services.freelance_service import freelance_service


@pytest.mark.asyncio
async def test_idempotent_import_by_place_id():
    lead_data = {
        "id": "lh_201",
        "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
        "name": "Bhopal IT Solutions",
        "city": "Bhopal",
        "category": "Software",
        "website": "https://bhopalitsolutions.com",
        "is_broken_website": False,
        "phone": "+91-755-1234567",
        "email": "info@bhopalitsolutions.com",
        "rating": 4.5,
        "reviews": 12,
    }

    async with AsyncSessionLocal() as session:
        # First import
        opp1 = await freelance_service.import_lead_as_opportunity(session, lead_data)
        assert opp1.id is not None
        first_id = opp1.id

        # Second import with same place_id but updated rating
        lead_data_updated = dict(lead_data)
        lead_data_updated["rating"] = 4.9
        opp2 = await freelance_service.import_lead_as_opportunity(session, lead_data_updated)

        assert opp2.id == first_id
        assert opp2.rating == 4.9

        # Ensure only 1 record exists
        all_opps = (await session.execute(
            select(FreelanceOpportunityRecord).where(FreelanceOpportunityRecord.place_id == lead_data["place_id"])
        )).scalars().all()
        assert len(all_opps) == 1


@pytest.mark.asyncio
async def test_idempotent_import_by_name_and_city():
    lead_data = {
        "id": "lh_202",
        "name": "Cafe Delight",
        "city": "Pune",
        "category": "Cafe",
        "website": "https://cafedelightpune.com",
        "is_broken_website": True,
        "email": "contact@cafedelight.com",
    }

    async with AsyncSessionLocal() as session:
        opp1 = await freelance_service.import_lead_as_opportunity(session, lead_data)
        opp2 = await freelance_service.import_lead_as_opportunity(session, lead_data)
        assert opp1.id == opp2.id

        # Verify contact evidence was recorded
        evs = (await session.execute(
            select(ContactEvidenceRecord).where(ContactEvidenceRecord.opportunity_id == opp1.id)
        )).scalars().all()
        assert len(evs) >= 2  # EMAIL and WEBSITE
