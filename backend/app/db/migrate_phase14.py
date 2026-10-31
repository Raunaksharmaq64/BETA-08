"""
RIGHT FIT — Phase 14 Database Migration & Baseline Seed Script
Creates:
  - beta_feedback
  - beta_consent_records
  - connector_health_snapshots
  - data_quality_audits
Seeds baseline connector metrics, audit records, and initial quality statistics.
"""

import sys
import os
import datetime
import uuid

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.models import (
    Base,
    BetaFeedbackRecord,
    BetaConsentRecord,
    ConnectorHealthSnapshotRecord,
    DataQualityAuditRecord,
)
from sqlalchemy.orm import Session


def run_migration():
    print(f"[Phase 14 Migration] Target DATABASE_URL: {settings.DATABASE_URL}")
    db_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")
    engine = create_engine(db_url, echo=False)

    print("[Phase 14 Migration] Creating Phase 14 tables...")
    Base.metadata.create_all(
        bind=engine,
        tables=[
            BetaFeedbackRecord.__table__,
            BetaConsentRecord.__table__,
            ConnectorHealthSnapshotRecord.__table__,
            DataQualityAuditRecord.__table__,
        ],
    )
    print("[Phase 14 Migration] Tables created successfully.")

    with Session(engine) as session:
        # 1. Seed Baseline Connector Health Snapshots
        existing_snaps = session.query(ConnectorHealthSnapshotRecord).count()
        if existing_snaps == 0:
            print("[Phase 14 Migration] Seeding baseline connector health snapshots...")
            now = datetime.datetime.now(datetime.timezone.utc)
            connectors = [
                ("greenhouse_ats", "SUCCESS", 1240.5, 45, 12, 3, 0),
                ("lever_ats", "SUCCESS", 980.2, 32, 8, 2, 0),
                ("ashby_ats", "SUCCESS", 810.0, 18, 5, 1, 0),
                ("workday_direct", "PARTIAL_SUCCESS", 3420.1, 80, 25, 12, 4),
                ("curated_tech_boards", "SUCCESS", 1450.3, 60, 14, 8, 1),
                ("statutory_filings", "SUCCESS", 2100.0, 110, 30, 4, 0),
            ]
            for key, status, dur, disc, upd, rej_d, rej_q in connectors:
                snap = ConnectorHealthSnapshotRecord(
                    id=str(uuid.uuid4()),
                    source_key=key,
                    run_timestamp=now - datetime.timedelta(hours=2),
                    status=status,
                    duration_ms=dur,
                    records_discovered=disc,
                    records_updated=upd,
                    records_rejected_dedup=rej_d,
                    records_rejected_quality=rej_q,
                    error_message="Minor parsing warning on legacy date format" if status == "PARTIAL_SUCCESS" else None,
                )
                session.add(snap)

        # 2. Seed Baseline Data Quality Audit Record
        existing_audits = session.query(DataQualityAuditRecord).count()
        if existing_audits == 0:
            print("[Phase 14 Migration] Seeding baseline data quality audit record...")
            audit = DataQualityAuditRecord(
                id=str(uuid.uuid4()),
                audit_date=datetime.datetime.now(datetime.timezone.utc),
                total_active_listings=345,
                duplicate_detection_count=42,
                false_positive_merge_count=0,
                broken_link_count=3,
                broken_link_rate_pct=0.87,
                closed_listing_detection_count=14,
            )
            session.add(audit)

        # 3. Seed Baseline Beta Feedback Item (Sample triage record)
        existing_feedback = session.query(BetaFeedbackRecord).count()
        if existing_feedback == 0:
            print("[Phase 14 Migration] Seeding initial triaged beta feedback...")
            fb = BetaFeedbackRecord(
                id=str(uuid.uuid4()),
                user_id=None,
                category="SEARCH_RELEVANCE",
                related_feature="JOB_SEARCH",
                related_record_id=None,
                description="Search for 'Kubernetes' returned both DevOps and general cloud listings appropriately, but rank weighting for junior roles was slightly high.",
                severity="LOW",
                review_status="TRIAGED",
                resolution_notes="Adjusted experience filter default threshold in Phase 7 engine.",
                responsible_owner="SearchArchitect",
            )
            session.add(fb)

        session.commit()
        print("[Phase 14 Migration] Baseline data seeded successfully.")

    print(f"[Phase 14 Migration] Total schema tables in Base: {len(Base.metadata.tables)}")
    return True


if __name__ == "__main__":
    run_migration()

