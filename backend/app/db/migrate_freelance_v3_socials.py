"""
RIGHT FIT Core — Freelance Socials & Contact Enrichment Migration v3
Adds social profile columns (instagram, facebook, linkedin, twitter) to freelance_opportunities table.
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine
from sqlalchemy import text


async def run_migration():
    print("Running migration v3: Adding social columns to freelance_opportunities...")
    columns_to_add = [
        ("instagram", "VARCHAR(500)"),
        ("facebook", "VARCHAR(500)"),
        ("linkedin", "VARCHAR(500)"),
        ("twitter", "VARCHAR(500)"),
    ]

    async with engine.begin() as conn:
        for col_name, col_type in columns_to_add:
            try:
                await conn.execute(
                    text(f"ALTER TABLE freelance_opportunities ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                )
                print(f" Column {col_name} checked/added successfully.")
            except Exception as e:
                print(f" Note for column {col_name}: {e}")

    print("Freelance Intelligence v3 migration complete.")


if __name__ == "__main__":
    asyncio.run(run_migration())

