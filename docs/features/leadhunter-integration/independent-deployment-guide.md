# Independent LeadHunter Deployment Guide

## Architecture Independence
LeadHunter AI runs as an isolated microservice on Port 8001 (or separate container).
It maintains its own database, scrapers, and Redis queue.

## Required Environment Variables (`ai agents/.env`)
```env
PORT=8001
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/leadhunter_db
REDIS_URL=redis://redis-host:6379/1
SECRET_KEY=leadhunter_secure_signing_key_min_32_chars!
SERPAPI_KEY=your_serpapi_key_here
APIFY_API_TOKEN=your_apify_token_here
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

## Running LeadHunter Independently
```bash
cd "c:\Users\Sahil\Desktop\manit\ai agents"
pip install -r backend/requirements.txt
python -m uvicorn app_fastapi:app --app-dir backend --host 127.0.0.1 --port 8001 --reload
```

## Health Verification
Query the health check endpoint:
```bash
curl http://127.0.0.1:8001/health
# Response: {"status": "healthy", "database": "healthy", "service": "leadhunter-api"}
```

