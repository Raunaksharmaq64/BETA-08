import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

root = Path(__file__).resolve().parent.parent.parent.parent
env_file = root / ".env"
load_dotenv(dotenv_path=env_file, override=True)

sys.path.insert(0, str(root / "backend"))
sys.path.insert(0, str(root))

from app.core.database import AsyncSessionLocal
from app.services.market_intelligence_service import MarketIntelligenceService

async def seed_market():
    async with AsyncSessionLocal() as session:
        print("Seeding baseline market intelligence...")
        await MarketIntelligenceService.ensure_baseline_seeded(session)
        await session.commit()
        print("Market intelligence baseline successfully seeded and committed!")

if __name__ == "__main__":
    asyncio.run(seed_market())
