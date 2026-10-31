import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def migrate():
    async with AsyncSessionLocal() as session:
        print("Adding priority column to freelance_opportunities...")
        await session.execute(text(
            "ALTER TABLE freelance_opportunities ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'MEDIUM' NOT NULL;"
        ))
        await session.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_freelance_opportunities_priority ON freelance_opportunities (priority);"
        ))
        await session.commit()
        print("Column added successfully!")

        print("Backfilling priority on existing records...")
        await session.execute(text("""
            UPDATE freelance_opportunities
            SET priority = CASE
                WHEN website IS NOT NULL AND website != '' AND is_broken_website = FALSE THEN 'LOW'
                WHEN is_broken_website = TRUE AND phone IS NOT NULL AND reviews_count < 50 THEN 'HIGH'
                WHEN is_broken_website = TRUE AND phone IS NOT NULL AND reviews_count <= 200 THEN 'MEDIUM'
                WHEN is_broken_website = TRUE AND phone IS NULL THEN 'MEDIUM'
                WHEN is_broken_website = TRUE THEN 'HIGH'
                WHEN phone IS NOT NULL AND reviews_count < 50 THEN 'HIGH'
                WHEN phone IS NOT NULL AND reviews_count <= 200 THEN 'MEDIUM'
                ELSE 'LOW'
            END;
        """))
        await session.commit()
        print("Backfill complete!")

        # Verify
        res = await session.execute(text(
            "SELECT priority, count(*) FROM freelance_opportunities GROUP BY priority;"
        ))
        counts = res.fetchall()
        print("Priority counts in DB:", counts)

if __name__ == "__main__":
    asyncio.run(migrate())
