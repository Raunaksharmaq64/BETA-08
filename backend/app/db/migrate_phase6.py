"""
RIGHT FIT Core — Phase 6 Database Migration Helper
Adds Phase 6 columns and tables to the active database.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_sqlite(db_path: str):
    if not Path(db_path).exists():
        print(f"Database file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check columns in canonical_opportunities
    cursor.execute("PRAGMA table_info(canonical_opportunities)")
    existing_cols = {col[1] for col in cursor.fetchall()}

    columns_to_add = [
        ("source_updated_at", "DATETIME"),
        ("last_checked_at", "DATETIME"),
        ("last_successful_check_at", "DATETIME"),
        ("last_verified_at", "DATETIME"),
        ("status_changed_at", "DATETIME"),
        ("closed_at", "DATETIME"),
        ("expires_at", "DATETIME"),
        ("expiry_derivation_notes", "VARCHAR(255)"),
        ("verification_status", "VARCHAR(30) DEFAULT 'UNVERIFIED'"),
        ("freshness_state", "VARCHAR(30) DEFAULT 'UNKNOWN'"),
        ("is_suppressed", "BOOLEAN DEFAULT 0"),
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            print(f"Adding column {col_name} to canonical_opportunities...")
            cursor.execute(f"ALTER TABLE canonical_opportunities ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else "rightfit_core.db"
    migrate_sqlite(db_file)

