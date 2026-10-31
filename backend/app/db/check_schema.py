import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load rightFIT/.env explicitly
root = Path(__file__).resolve().parent.parent.parent.parent
env_file = root / ".env"
load_dotenv(dotenv_path=env_file, override=True)

sys.path.insert(0, str(root / "backend"))
sys.path.insert(0, str(root))

from app.core.database import engine
from sqlalchemy import text

async def check_and_fix():
    print("Database URL:", engine.url)
    is_sqlite = "sqlite" in str(engine.url)

    async with engine.begin() as conn:
        if is_sqlite:
            res = await conn.execute(text("PRAGMA table_info(startup_opportunities)"))
            existing_cols = {r[1] for r in res.fetchall()}
        else:
            res = await conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'startup_opportunities'
            """))
            existing_cols = {r[0] for r in res.fetchall()}
        
        print(f"Existing columns in startup_opportunities: {len(existing_cols)}")

        # Check required columns
        required_cols = {
            "validation_state": "VARCHAR(50) DEFAULT 'OBSERVED_PROBLEM' NOT NULL",
            "corroboration_count": "INTEGER DEFAULT 1 NOT NULL",
            "has_conflicting_evidence": "BOOLEAN DEFAULT FALSE NOT NULL",
            "problem_explanation": "TEXT",
            "how_to_solve_strategy": "TEXT",
            "ai_insight": "TEXT",
            "ai_opportunity": "TEXT",
            "ai_pitch_idea": "TEXT",
            "ai_model": "VARCHAR(50)",
            "ai_generated_at": "TIMESTAMPTZ" if not is_sqlite else "DATETIME",
            "published_at": "TIMESTAMPTZ" if not is_sqlite else "DATETIME",
            "retrieved_at": "TIMESTAMPTZ" if not is_sqlite else "DATETIME",
            "first_seen_at": "TIMESTAMPTZ DEFAULT NOW() NOT NULL" if not is_sqlite else "DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL",
            "last_checked_at": "TIMESTAMPTZ DEFAULT NOW() NOT NULL" if not is_sqlite else "DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL",
            "score_explanation": "TEXT",
            "domain": "VARCHAR(150)",
            "website_url": "VARCHAR(500)",
            "source_url": "VARCHAR(500)",
            "service_record_id": "VARCHAR(64)",
        }

        for col, col_def in required_cols.items():
            if col not in existing_cols:
                print(f"Adding missing column to startup_opportunities: {col} {col_def}")
                try:
                    await conn.execute(text(f"ALTER TABLE startup_opportunities ADD COLUMN {col} {col_def}"))
                except Exception as e:
                    print(f"Error adding {col}: {e}")

        # Freelance checks
        if is_sqlite:
            res_freelance = await conn.execute(text("PRAGMA table_info(freelance_opportunities)"))
            freelance_cols = {r[1] for r in res_freelance.fetchall()}
        else:
            res_freelance = await conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'freelance_opportunities'
            """))
            freelance_cols = {r[0] for r in res_freelance.fetchall()}

        print(f"Existing columns in freelance_opportunities: {len(freelance_cols)}")

        freelance_req = {
            "is_broken_website": "BOOLEAN DEFAULT FALSE NOT NULL",
            "last_verified_at": "TIMESTAMPTZ" if not is_sqlite else "DATETIME",
            "relevance_score": "INTEGER DEFAULT 70 NOT NULL",
            "classification_reason": "TEXT",
            "place_id": "VARCHAR(100)",
            "leadhunter_lead_id": "VARCHAR(100)",
            "rating": "FLOAT DEFAULT 0.0 NOT NULL",
            "reviews_count": "INTEGER DEFAULT 0 NOT NULL",
            "location": "VARCHAR(255)",
            "original_source_url": "VARCHAR(500)",
        }
        for col, col_def in freelance_req.items():
            if col not in freelance_cols:
                print(f"Adding missing column to freelance_opportunities: {col} {col_def}")
                try:
                    await conn.execute(text(f"ALTER TABLE freelance_opportunities ADD COLUMN {col} {col_def}"))
                except Exception as e:
                    print(f"Error adding {col}: {e}")

    print("Schema alignment successfully finished!")

if __name__ == "__main__":
    asyncio.run(check_and_fix())
