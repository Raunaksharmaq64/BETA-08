"""
RIGHT FIT Core — Phase 10 Database Migration Helper
Creates Phase 10 tables using the native async engine:
- startup_opportunities
- startup_evidence
- startup_tech_findings
- startup_corroborations
- startup_pitch_drafts
- saved_startup_opportunities
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base
from app.db.models import (
    StartupOpportunityRecord,
    StartupEvidenceRecord,
    StartupTechFindingRecord,
    StartupCorroborationRecord,
    StartupPitchDraftRecord,
    SavedStartupOpportunityRecord,
)


async def run_migration():
    print("Connecting to database via async engine to create Phase 10 tables...")
    tables_to_create = [
        StartupOpportunityRecord.__table__,
        StartupEvidenceRecord.__table__,
        StartupTechFindingRecord.__table__,
        StartupCorroborationRecord.__table__,
        StartupPitchDraftRecord.__table__,
        SavedStartupOpportunityRecord.__table__,
    ]

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn, tables=tables_to_create))
    print("Phase 10 tables created successfully (6 tables).")


if __name__ == "__main__":
    asyncio.run(run_migration())

