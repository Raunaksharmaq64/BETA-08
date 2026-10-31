"""
Unit tests for Startup Opportunity Deduplication and Corroboration Ledger
Phase: 10 — Startup Intelligence Integration
"""

import pytest
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.services.startup_service import StartupService
from app.db.models import StartupOpportunityRecord, StartupEvidenceRecord, StartupCorroborationRecord


@pytest.mark.asyncio
async def test_startup_lead_idempotent_import_and_deduplication():
    sample_leads = [
        {
            "id": "lead-uuid-001",
            "startup_name": "Acme SaaS",
            "url": "https://acme-saas.io",
            "category": "Performance",
            "detected_signal": "Page load speeds exceeding 3s on landing",
            "insight": "High bounce rates on mobile",
            "opportunity": "Speed optimization package",
            "pitch_idea": "Hey Acme team, noticed your load times...",
            "score": 8,
            "source": "Reddit RSS (/r/saas)",
            "created_at": "2026-10-30T12:00:00Z",
            "analyzed": True,
            "tech_audit": {"tech_stack": ["React", "Next.js", "Vercel"]}
        },
        {
            "id": "lead-uuid-002",
            "startup_name": "DevFlow Tools",
            "url": "https://devflow.dev",
            "category": "Development",
            "detected_signal": "Need help setting up Postgres connection pooler",
            "insight": "Database connection exhaustion",
            "opportunity": "Backend architecture consulting",
            "score": 9,
            "source": "Hacker News (Show HN)",
            "created_at": "2026-10-30T14:30:00Z",
            "analyzed": False
        }
    ]

    async with AsyncSessionLocal() as session:
        # First import
        res1 = await StartupService.import_startup_leads(sample_leads, session)
        assert res1["imported_count"] == 2
        assert res1["updated_count"] == 0

        # Second import with same leads -> should update, not create duplicates
        res2 = await StartupService.import_startup_leads(sample_leads, session)
        assert res2["imported_count"] == 0
        assert res2["updated_count"] == 2

        # Verify canonical count is exactly 2
        records_res = await session.execute(select(StartupOpportunityRecord))
        records = records_res.scalars().all()
        assert len(records) == 2
