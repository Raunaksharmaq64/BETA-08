"""
RIGHT FIT Core — Freelance Intelligence Migration Helper v2
Creates newly added tables:
- freelance_search_history
- freelance_candidate_settings
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base
from app.db.models import (
    FreelanceOpportunityRecord,
    ContactEvidenceRecord,
    SavedFreelanceOpportunityRecord,
    OutreachDraftRecord,
    OutreachDeliveryLogRecord,
    OutreachSuppressionRecord,
    FreelanceSearchHistoryRecord,
    FreelanceCandidateSettingsRecord,
)


async def run_migration():
    print("Connecting to database via async engine to create Freelance tables...")
    tables_to_create = [
        FreelanceOpportunityRecord.__table__,
        ContactEvidenceRecord.__table__,
        SavedFreelanceOpportunityRecord.__table__,
        OutreachDraftRecord.__table__,
        OutreachDeliveryLogRecord.__table__,
        OutreachSuppressionRecord.__table__,
        FreelanceSearchHistoryRecord.__table__,
        FreelanceCandidateSettingsRecord.__table__,
    ]

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn, tables=tables_to_create))
    print("Freelance Intelligence tables created successfully.")


if __name__ == "__main__":
    asyncio.run(run_migration())
