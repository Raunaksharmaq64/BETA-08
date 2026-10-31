import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine
from app.db.models import CandidateSkillRecord, CandidateProfile, User

async def main():
    print("Connecting to live database...")
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'candidate_skills'"))
        existing = {r[0]: r[1] for r in res.fetchall()}
        print(f"Existing columns on candidate_skills ({len(existing)}):")
        for k, v in existing.items():
            print(f"  - {k} ({v})")
        
        for col_name, col in CandidateSkillRecord.__table__.columns.items():
            if col_name not in existing:
                col_type = col.type.compile(engine.dialect)
                print(f"--> MISSING COLUMN detected: {col_name} ({col_type})")
                sql = f"ALTER TABLE candidate_skills ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                print(f"    Executing: {sql}")
                await conn.execute(text(sql))
                print(f"    Added {col_name} successfully.")

        # Also let's check candidate_profiles columns
        res_p = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'candidate_profiles'"))
        existing_p = {r[0] for r in res_p.fetchall()}
        for col_name, col in CandidateProfile.__table__.columns.items():
            if col_name not in existing_p:
                col_type = col.type.compile(engine.dialect)
                print(f"--> MISSING COLUMN on candidate_profiles: {col_name} ({col_type})")
                sql = f"ALTER TABLE candidate_profiles ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                print(f"    Executing: {sql}")
                await conn.execute(text(sql))
                print(f"    Added {col_name} to candidate_profiles.")

    print("\nAll database schema alignments completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())

