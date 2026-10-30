# API & Dependency Inventory

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Comprehensive API, Dependency & Infrastructure Catalog
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. External Third-Party API Providers

| Provider | Owning Repository | Purpose | Implementation Location | Authentication Method | Usage Pattern | Known Quotas | Billing Category | Retry & Resilience | Verification Status | Operational Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Gemini API** | `Startups-problrms-hunter` / `agentic-career-search` | Raw post analysis, pain-point extraction, pitch drafting | `ai_agent.py`, `services/llm_enrichment.py` | API Key (`GEMINI_API_KEY`) | On-demand per lead | Free tier: 15 RPM / 1M TPM (Paid tier varies) | Free / Pay-per-token | Fallback to deterministic template when key is absent or exhausted | VERIFIED | Quota exhaustion leads to graceful fallback; cost scales with volume |
| **SerpApi** | `ai agents` (LeadHunter) | Google Maps local business data extraction | `backend/services/search_service.py` | API Key (`SERPAPI_KEY`) | Batch per user search query | Free tier: 100 searches/mo | Paid after free limit ($50-$250/mo) | Automatic fallback to Apify if configured | VERIFIED | High risk of unexpected API bills during automated bulk scans |
| **Apify** | `ai agents` (LeadHunter) | Alternative Google Maps scraper actor | `backend/services/search_service.py` | API Token (`APIFY_API_TOKEN`) | Batch scraper execution | Free tier: $5 monthly credit | Pay-per-usage | Fallback to SerpApi | VERIFIED | Platform actor breaking changes; scraping concurrency limits |
| **Serper.dev** | `Startups-problrms-hunter` | Organic Google Search for startup lookups | `scraper.py:37` | API Key (`SERPER_API_KEY`) | On-demand search fallback | 2,500 free queries | Paid after free limit | Automatic fallback to DuckDuckGo / Yahoo | VERIFIED | Low cost; graceful fallback exists |
| **DuckDuckGo** | `Startups-problrms-hunter` | Web search and signal discovery | `scraper.py:53` | Public Web (No key required) | Batch queries via `duckduckgo-search` | UNKNOWN (Aggressive bot rate limiting) | Free | Automatic fallback to Yahoo Search HTML scraping | VERIFIED | Captcha challenge blocks scraper; fallback to Yahoo works |
| **GitHub REST API** | `Startups-problrms-hunter` | Search issues labeled "help wanted" | `scraper.py:396` | Public Unauthenticated (Optional PAT) | Periodic feed queries | Unauthenticated: 60 req/hr; Auth: 5,000 req/hr | Free | Standard HTTP error catching | VERIFIED | Low rate limit (60 req/hr) without personal access token |
| **Reddit RSS/JSON** | `Startups-problrms-hunter` | Ingest posts from `/r/saas`, `/r/startups` | `scraper.py:787` | Custom User-Agent header (Public) | Periodic subreddit queries | ~60 req/min with unique User-Agent | Free | Retry with exponential backoff | VERIFIED | Reddit aggressive IP blocking if User-Agent is generic |
| **Tomba.io / Hunter.io** | `Startups-problrms-hunter` | Founder email and contact discovery | `scraper.py:640` | API Key (`TOMBA_KEY`, `HUNTER_API_KEY`) | Per-lead domain lookup | Free tier: 25-50 requests/mo | Paid | Skip enrichment on failure | PARTIAL | Exhausted quickly on bulk runs |

---

## 2. Internal Service API Endpoints

### 2.1 `agentic-career-search` (FastAPI, Port 8000)
- `GET  /health` — Liveness & readiness probes.
- `POST /runs` — Enqueue asynchronous job scraping & analysis run.
- `GET  /runs/{run_id}` — Retrieve status of run.
- `GET  /runs/{run_id}/events` — Retrieve event stream for debugging.
- `POST /runs/{run_id}/cancel` — Cancel active run.
- `GET  /jobs` — Query normalized job listings.
- `GET  /source-configs` — List configured ATS endpoints.
- `POST /source-configs` — Register new ATS endpoint.

### 2.2 `ai agents` (LeadHunter FastAPI, Port 8000)
- `POST /api/auth/login` — User authentication and cookie issuance.
- `POST /api/auth/signup` — User registration.
- `GET  /api/auth/me` — Current user context.
- `GET  /api/leads` — List qualified business leads with pagination and filters.
- `POST /api/leads/search` — Trigger Google Maps local business scraper.
- `GET  /api/leads/{id}/audit` — Retrieve technical website audit data.
- `POST /api/outreach/send` — Dispatch SMTP proposal email.
- `GET  /api/dashboard/stats` — Funnel conversion metrics.

### 2.3 `Startups-problrms-hunter` (FastAPI, Port 8000)
- `GET  /api/leads` — Returns array of startup pain-point leads.
- `POST /api/scan` — Initiates multi-source scraping run across Reddit, GitHub, etc.
- `POST /api/leads/{id}/pitch` — Generates Gemini pitch draft.
- `POST /api/audit` — Audits target website speed and SEO tags.
- `GET  /api/settings`, `POST /api/settings` — Reads/writes local JSON configuration.

---

## 3. Environment Variables Catalog (Names Only — Zero Secrets)

### Core Career Engine (`agentic-career-search`)
- `APP_ENV`
- `DATABASE_URL`
- `LOG_LEVEL`
- `DEFAULT_TIMEOUT_SECONDS`
- `MAX_CONCURRENT_REQUESTS`

### LeadHunter AI (`ai agents`)
- `SECRET_KEY`
- `FLASK_SECRET_KEY`
- `APP_URL`
- `NEXT_PUBLIC_API_URL`
- `FRONTEND_URL`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL`
- `POSTGRES_PASSWORD`
- `DB_SSL_MODE`
- `CELERY_ENABLED`
- `REDIS_PASSWORD`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `MAPS_PROVIDER`
- `SERPAPI_KEY`
- `APIFY_API_TOKEN`
- `SYSTEM_SMTP_HOST`
- `SYSTEM_SMTP_PORT`
- `SYSTEM_SMTP_EMAIL`
- `SYSTEM_SMTP_PASSWORD`
- `SYSTEM_SMTP_USE_SSL`

### Startup Intelligence (`Startups-problrms-hunter`)
- `GEMINI_API_KEY`
- `SERPER_API_KEY`
- `TOMBA_KEY`
- `TOMBA_SECRET`
- `HUNTER_API_KEY`
- `PAGESPEED_API_KEY`

---

## 4. Software Dependencies & Libraries

### Python Libraries (Shared / Core)
- `fastapi` (0.110.0 - 0.115.0)
- `uvicorn` (0.28.0 - 0.30.6)
- `pydantic` / `pydantic-settings` (v2.x)
- `httpx` (0.27.0 - 0.27.2)
- `beautifulsoup4` (4.12.3)
- `sqlalchemy` (2.0.35)
- `alembic` (1.13.2)
- `pytest` (8.0.0 - 9.1.0)
- `pytest-asyncio` (0.23.0 - 0.24.0)
- `ruff` (0.6.9)

### LeadHunter-Specific Python Dependencies
- `sqlmodel` (0.0.16)
- `asyncpg` (0.29.0)
- `celery` (5.3.0)
- `redis` (5.0.0)
- `pyjwt` (2.8.0)
- `google-search-results` (2.4.2)
- `apify-client` (1.0.0)
- `playwright` (1.40.0)
- `phonenumbers` (8.13.0)

### Frontend Dependencies (`ai agents/frontend`)
- `next` (16.2.10)
- `react` (19.2.4)
- `react-dom` (19.2.4)
- `tailwindcss` (4.0)
- `typescript` (5.x)
- `eslint` (9.x)

---

## 5. Storage, Caching & Queue Topology

| Component | Technology | Target Queue / Table | Owning System | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Relational DB** | PostgreSQL 16 | `core.*` schemas | Core Career Engine | ACTIVE |
| **Relational DB** | PostgreSQL 16 | `leadhunter.*` schema | LeadHunter Service | ACTIVE |
| **Document Store** | Flat File JSON (`leads.json`) | N/A | Startup Intelligence | BROKEN / LEGACY |
| **Cache & Broker** | Redis 7 | `career_tasks` queue | Core Career Engine | PLANNED |
| **Cache & Broker** | Redis 7 | `leadhunter_worker` queue | LeadHunter Service | ACTIVE |
| **Object Storage** | AWS S3 / MinIO | `resumes/`, `audit-pdfs/` | Core Engine & LeadHunter | PLANNED |
| **Outbound Email** | SMTP (TLS 587/465) | Transactional & Pitch Delivery | LeadHunter Service | ACTIVE |
| **Inbound Email** | IMAP (SSL 993) | Inbox Reply Tracking | LeadHunter Service | ACTIVE |

