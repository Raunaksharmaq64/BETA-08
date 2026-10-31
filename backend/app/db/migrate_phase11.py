"""
RIGHT FIT Core — Phase 11 Database Migration Helper
Creates Phase 11 tables using the native async engine:
- candidate_opportunity_feedback
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base
from app.db.models import CandidateOpportunityFeedbackRecord


async def run_migration():
    print("Connecting to database via async engine to create Phase 11 tables...")
    tables_to_create = [
        CandidateOpportunityFeedbackRecord.__table__,
    ]

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn, tables=tables_to_create))
    print("Phase 11 tables created successfully (1 table: candidate_opportunity_feedback).")


if __name__ == "__main__":
    asyncio.run(run_migration())

