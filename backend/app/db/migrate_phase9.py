"""
RIGHT FIT Core — Phase 9 Database Migration Helper
Creates Phase 9 tables using the native async engine:
- freelance_opportunities
- contact_evidence
- saved_freelance_opportunities
- outreach_drafts
- outreach_delivery_logs
- outreach_suppression_list
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
)


async def run_migration():
    print("Connecting to database via async engine to create Phase 9 tables...")
    tables_to_create = [
        FreelanceOpportunityRecord.__table__,
        ContactEvidenceRecord.__table__,
        SavedFreelanceOpportunityRecord.__table__,
        OutreachDraftRecord.__table__,
        OutreachDeliveryLogRecord.__table__,
        OutreachSuppressionRecord.__table__,
    ]

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn, tables=tables_to_create))
    print("Phase 9 tables created successfully (6 tables).")


if __name__ == "__main__":
    asyncio.run(run_migration())
