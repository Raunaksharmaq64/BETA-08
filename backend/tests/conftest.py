"""
Pytest configuration for RIGHT FIT test suite.
Ensures project root and backend root are on sys.path.
Initializes a clean, isolated database and resets rate limits before each test.
"""

import os
import sys
from pathlib import Path
import pytest

# Ensure testing environment uses an isolated local SQLite database
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_core.db"
os.environ["APP_ENV"] = "testing"

# Project root: c:\Users\Sahil\Desktop\manit\rightFIT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(autouse=True)
async def test_lifecycle_setup():
    """Drops and recreates all tables, and resets rate limiter state before every test."""
    print("\n--- TEST LIFECYCLE SETUP CALLED ---")
    from app.core.database import Base, engine
    import app.db.models  # noqa: F401 - ensure all models registered on Base.metadata
    from app.services.rate_limiter import rate_limiter

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn, checkfirst=True))
        await conn.run_sync(Base.metadata.create_all)

    rate_limiter.reset()
    yield
    rate_limiter.reset()
