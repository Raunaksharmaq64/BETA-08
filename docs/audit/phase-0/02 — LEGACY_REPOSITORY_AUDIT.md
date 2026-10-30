# Legacy Repository Audit

- **Project:** RIGHT FIT — Career Intelligence Platform
- **Document:** Legacy Source Systems Technical Audit
- **Status:** APPROVED
- **Audit Date:** 2026-10-30

---

## 1. Repository A: `agentic-career-search` (Core Career Engine)

### 1.1 Metadata & Version Control
* **Absolute Path:** `C:\Users\Sahil\Desktop\manit\agentic-career-search`
* **Git Branch:** `main`
* **Commit Hash:** `ff9767a7a31b9aa87454e1af881262659edf98ea`
* **Latest Commit Message:** `feat: PhantomEquityLiquidityGapAdvisor (#306)`
* **Git Working Tree:** Clean (0 uncommitted or modified files).

### 1.2 Technology Stack
* **Language & Runtime:** Python >= 3.11 (Executed cleanly on host Python 3.13.15).
* **Package Manager & Build System:** Hatchling / standard `pyproject.toml`.
* **Framework:** FastAPI 0.115.0, Uvicorn 0.30.6.
* **Database & ORM:** SQLAlchemy 2.0.35, Alembic 1.13.2, aiosqlite 0.20.0 (SQLite / PostgreSQL compatible).
* **Parsing & Scraping:** BeautifulSoup4 4.12.3, HTTPX 0.27.2.
* **Code Quality & Testing:** Pytest 8.3.3, Pytest-Asyncio 0.24.0, Ruff 0.6.9, Mypy 1.11.2.

### 1.3 Architecture & Entry Points
* **Main Entry Point:** `src/autoapply_agent/main.py` initializes the FastAPI application.
* **API Endpoints:**
  - `GET /health` — Service readiness and liveness checks (`src/autoapply_agent/api/routes_health.py`).
  - `POST /runs` — Schedules an asynchronous job scraping and matching run (`routes_runs.py`).
  - `GET /runs/{run_id}` — Inspects run status and metrics (`routes_runs.py`).
  - `GET /runs/{run_id}/events` — Replays persisted execution events (`routes_runs.py`).
  - `POST /runs/{run_id}/cancel` — Gracefully cancels an active scraping run (`routes_runs.py`).
  - `GET /jobs` — Lists normalized job candidates (`routes_jobs.py`).
  - `GET /source-configs`, `POST /source-configs` — Manages ATS scrapers (`routes_source_configs.py`).
* **Workers & Tasks:** `src/autoapply_agent/services/worker.py` contains the polling execution loop that ingests `Run` jobs, calls configured source adapters, scores matches, and records audit events (`RunEvent`).

### 1.4 Database Models (`src/autoapply_agent/db/models.py`)
1. `SourceConfig`: Scraper targets, base URLs, timeouts, enabled flags.
2. `Run`: Run state machine (`queued`, `running`, `completed`, `failed`, `cancelled`), query filters, timestamps.
3. `RunEvent`: Durable ordered event stream with sequence numbers for forensic run replay.
4. `Job`: Normalized job listing containing external ID, title, company, location, URL, fit score, plan steps, and raw JSON payload.

### 1.5 Source Adapters Inventory (`src/autoapply_agent/adapters/`)
Contains over 70 implemented adapters conforming to `CareerSourceAdapter`:
- **Tier 1 ATS:** Greenhouse, Lever, Ashby, Workable, Recruitee, SmartRecruiters, BambooHR, Workday, Taleo, iCIMS, Dayforce, JazzHR, BreezyHR.
- **Tech Job Boards:** BuiltIn, Dice, Wellfound/AngelList, Levels.fyi, RemoteOK, WeWorkRemotely, Himalayas, Arc.dev, AuthenticJobs.
- **Verification Evidence:** All inspected adapters implement full HTML parsing via BeautifulSoup or structured JSON endpoints with dedicated unit tests in `tests/unit/`.

### 1.6 Analytical Services Inventory (`src/autoapply_agent/services/`)
Contains over 120 specialized domain modules:
- `scoring.py`: Deterministic scoring engine with word-boundary regex matching.
- `skills_fit.py`: Tokenized candidate skills fit scorer (`fit_score` 0.0 to 1.0).
- `ats_keyword_coverage.py`: High-signal keyword extraction from JD matched against resume text.
- `salary_band.py`, `equity_vesting.py`, `rsu_refresh_cliff.py`: Compensation calculators.
- `application_stages.py`: Auditable CRM stage machine (`saved` ➔ `applied` ➔ `interview` ➔ `offer`).
- `star_story.py`, `interview_prep.py`: Interview preparation brief generators.

### 1.7 Test Suite Execution
- **Inventory:** 281 unit test files in `tests/unit/`.
- **Reproducible Test Runs:** Executed offline unit tests (`test_scoring.py`, `test_adapters.py`, `test_ats_keyword_coverage.py`, `test_application_stages.py`). **100% passed (51/51 tests passing in < 2 seconds).**

### 1.8 Security Observations
- No hardcoded secrets detected in source code.
- Strict input validation via Pydantic models.
- **Missing Capability:** Has **NO user authentication, NO multi-tenant isolation, and NO binary PDF/DOCX resume file parser**.

---

## 2. Repository B: `ai agents` (LeadHunter AI)

### 2.1 Metadata & Version Control
* **Absolute Path:** `C:\Users\Sahil\Desktop\manit\ai agents`
* **Git Branch:** `main`
* **Commit Hash:** `30d569580c2bd5d4a10f90931df48a5edd96d70d`
* **Latest Commit Message:** `feat: add FastAPI subscription and billing webhook routes with signature verification`
* **Git Working Tree:** 2 pre-existing untracked files (`Complete_Project_Documentation.pdf`, `generate_pdf.py`).

### 2.2 Technology Stack
* **Backend:** Python 3.11+, FastAPI 0.110.0, SQLModel 0.0.16, SQLAlchemy 2.0+, asyncpg 0.29.0, Celery 5.3.0, Redis 5.0.0.
* **Frontend:** Next.js 16.2.10 (App Router), React 19.2.4, Tailwind CSS v4, TypeScript 5.
* **External Scrapers:** `google-search-results` (SerpApi), `apify-client`, `playwright`.
* **Testing:** Pytest 8.0+, Pytest-Asyncio, 20 security test suites.

### 2.3 Architecture & Entry Points
* **Backend Entry Point:** `backend/app_fastapi.py` initialized on port 8000.
* **Worker Entry Point:** `backend/celery_worker.py` handling asynchronous Google Maps searches and IMAP email reply sync.
* **Frontend Entry Point:** `frontend/src/app/page.tsx` with authenticated dashboard layout at `src/app/(dashboard)/layout.tsx`.
* **FastAPI Routers (`backend/routes_fastapi/`):**
  - `auth.py`: Complete user registration, login, JWT token issuance, HTTP-only cookie management, OTP verification, and account lockout tracking.
  - `api_leads.py`: Local business search, bulk scan progress rehydration, lead notes, lead status transitions.
  - `api_outreach.py`: AI sales pitch generation and SMTP outbound delivery.
  - `dashboard.py`: Conversion metrics, funnel analytics, and lead volume charts.
  - `api_subscription.py`: Billing webhook handling and tier limits.

### 2.4 Database Models (`backend/models/models_async.py`)
- `UserModel`: Full user authentication profile with hashed passwords (`werkzeug.security`).
- `LeadModel`: Local business entity with fields for address, website, rating, priority, contact details, `is_broken_website`, `pipeline_stage`, and `audit_data`.
- `SearchHistoryModel`, `BulkScanJobModel`, `ScanJobModel`: State persistence ensuring bulk scans continue and rehydrate if the user refreshes their browser.
- `ImapSettingsModel`, `SmtpSettingsModel`: User-configured email integration profiles.

### 2.5 Test Suite Execution
- **Inventory:** 20 comprehensive security test files in `backend/tests/`.
- **Reproducible Test Runs:** Executed `tests/test_jwt_authentication.py` covering algorithm 'none' defense, signature verification, token expiration, and role dependencies. **100% passed (20/20 tests passed in 1.75s).**

### 2.6 Security Observations
- Mature authentication controls: High-entropy secret key enforcement, rate limiting, and brute-force lockout tracking.
- Celery configuration is hardened against pickle deserialization attacks (`accept_content=['json']`).
- **Billing Risk:** Uncapped bulk scans with SerpApi / Apify could incur significant third-party API fees if user quotas are not strictly enforced.

---

## 3. Repository C: `Startups-problrms-hunter` (Startup Intelligence)

### 3.1 Metadata & Version Control
* **Absolute Path:** `C:\Users\Sahil\Desktop\manit\Startups-problrms-hunter`
* **Git Branch:** `main`
* **Commit Hash:** `693c32fb18386784427b72f2570fb551af5d707d`
* **Latest Commit Message:** `feat: add environment configurations and initialize front-end lead dashboard with scraper integration`
* **Git Working Tree:** Pre-existing modified `.pyc` files and `package-lock.json`.

### 3.2 Technology Stack
* **Language & Framework:** Python 3.11+, FastAPI, Uvicorn.
* **Scraping & Feeds:** `beautifulsoup4`, `lxml`, `duckduckgo-search`, `httpx`, `dnspython`.
* **AI Engine:** `google-generativeai` (Google Gemini API, default model `gemini-2.0-flash`).
* **Frontend:** Static HTML5 / CSS3 / Vanilla JavaScript served from `public/`.
* **Persistence:** Native JSON files (`data/leads.json`, `data/settings.json`).

### 3.3 Architecture & Entry Points
* **Main Entry Point:** `main.py` running Uvicorn server on port 8000.
* **Key Modules:**
  - `scraper.py`: Multi-source crawler extracting developer signals from Reddit (`r/saas`, `r/startups`, `r/SideProject`), GitHub (issues labeled `help wanted`), Hacker News, Dev.to, Product Hunt RSS, and Google News RSS.
  - `ai_agent.py`: Uses Google Gemini 2.0 Flash to analyze raw post text, extract startup name, diagnose the technical pain point, and generate a tailored 150-word sales pitch.
  - `email_verifier.py`: Resolves DNS MX records and initiates SMTP `HELO`/`RCPT TO` handshakes to verify email deliverability.

### 3.4 Test Suite & Quality Audit
* **Test Inventory:** **0 automated test files found.**
* **Persistence Evaluation:** All leads are stored in a single flat file (`data/leads.json`). File is read and overwritten synchronously via `json.dump()`.
* **Concurrency Risk:** Multiple simultaneous scans or users will overwrite or corrupt `leads.json`.

### 3.5 Security Observations
* **Direct SMTP Verification:** `email_verifier.py` connects directly to target mail servers. Repeated verification attempts can get the host IP blacklisted by spam filters (Spamhaus, Barracuda).
* **No Authentication:** API endpoints have no authorization layer; any network client can trigger scraping or delete leads.

