"""
RIGHT FIT Core — Phase 7 Database Migration Helper
Creates Phase 7 tables (saved_jobs, saved_searches, alert_delivery_logs) in active database.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.db.models import Base, SavedJobRecord, SavedSearchRecord, AlertDeliveryLogRecord


def run_migration():
    sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite:", "sqlite:")
    sync_url = sync_url.replace("postgresql+asyncpg:", "postgresql:")
    print(f"Connecting to {sync_url} to create Phase 7 tables...")
    engine = create_engine(sync_url)
    
    # Create tables
    Base.metadata.create_all(
        bind=engine,
        tables=[
            SavedJobRecord.__table__,
            SavedSearchRecord.__table__,
            AlertDeliveryLogRecord.__table__,
        ]
    )
    print("Phase 7 tables created successfully: saved_jobs, saved_searches, alert_delivery_logs")


if __name__ == "__main__":
    run_migration()

