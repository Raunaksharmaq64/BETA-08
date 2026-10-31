# LeadHunter Dependency Audit & Compatibility Analysis

**Project:** RIGHT FIT — Freelance Intelligence Integration  
**Date:** 2026-10-31  
**Status:** COMPLETED  

---

## 1. Executive Summary

This audit compares the dependencies of the original LeadHunter backend (`ai agents/backend/requirements.txt`) with RIGHT FIT's core backend (`rightFIT/backend/requirements.txt`), identifying reused packages, required additions, and obsolete packages to drop.

All core packages—such as FastAPI, SQLAlchemy 2.0, asyncpg, Celery, Redis, Pydantic v2, and cryptography—are already pinned and active in RIGHT FIT. Only a small set of specialized libraries (e.g. `google-search-results`, `phonenumbers`, `apify-client`, `PyYAML`) need to be integrated into `rightFIT/backend/requirements.txt`.

---

## 2. Dependency Comparison Matrix

| Package Name | LeadHunter Version | RIGHT FIT Status | Decision | Purpose / Justification |
|:---|:---|:---|:---:|:---|
| `fastapi` | `>=0.110.0` | `0.115.8` (Active) | **REUSE** | Core web framework. RIGHT FIT's version is newer and fully compatible. |
| `uvicorn[standard]` | `>=0.28.0` | `0.34.0` (Active) | **REUSE** | High-performance ASGI web server. |
| `pydantic` | Transitive | `2.13.4` (Active) | **REUSE** | Data validation and schema parsing. |
| `pydantic-settings` | `>=2.2.1` | `2.7.1` (Active) | **REUSE** | Environment configuration management. |
| `sqlalchemy` | `>=2.0.0` | `2.0.38` (Active) | **REUSE** | Async ORM and database engine. |
| `asyncpg` | `>=0.29.0` | `0.30.0` (Active) | **REUSE** | Asynchronous PostgreSQL driver. |
| `psycopg2-binary` | `>=2.9.0` | `2.9.10` (Active) | **REUSE** | Synchronous PostgreSQL driver (for Alembic migrations). |
| `alembic` | `>=1.12.0` | `1.14.1` (Active) | **REUSE** | Database schema migration engine. |
| `celery` | `>=5.3.0` | `5.4.0` (Active) | **REUSE** | Distributed asynchronous task queue. |
| `redis` | `>=5.0.0` | `5.2.1` (Active) | **REUSE** | In-memory message broker and caching. |
| `cryptography` | `>=42.0.0` | `50.0.0` (Active) | **REUSE** | AES encryption for user BYOK API keys and password hashing. |
| `pyjwt` | `>=2.8.0` | `2.13.0` (Active) | **REUSE** | Secure JSON Web Token validation. |
| `httpx` | `>=0.27.0` | `0.28.1` (Active) | **REUSE** | Asynchronous HTTP client for external integrations. |
| `requests` | `2.32.3` | `2.32.3` (Active) | **REUSE** | Synchronous HTTP client used in SSRF-guarded scraping. |
| `email-validator` | `>=2.0.0` | `2.3.0` (Active) | **REUSE** | Email address syntax validation. |
| `python-multipart` | `>=0.0.9` | `0.0.32` (Active) | **REUSE** | Form data and file upload parsing. |
| `python-dotenv` | `1.1.0` | `1.1.0` (Active) | **REUSE** | `.env` environment loading. |
| `google-search-results` | `2.4.2` | Installed in env | **ADD** | Official SerpApi Python client for Google Maps business discovery. |
| `phonenumbers` | `>=8.13.0` | Installed in env (8.14.0) | **ADD** | Google's libphonenumber port for phone standardization & line classification. |
| `apify-client` | `>=1.0.0` | Installed in env (3.1.3) | **ADD** | Official client for running Apify Google Places scraper actors. |
| `PyYAML` | `>=6.0.1` | Installed in env (6.0.3) | **ADD** | YAML parser for loading outreach prompt templates. |
| `pandas` | `>=2.0.0` | Installed in env (2.2.3) | **ADD (OPTIONAL)** | Data manipulation and tabular Excel export. |
| `openpyxl` | `>=3.1.0` | Installed in env (3.1.5) | **ADD (OPTIONAL)** | Excel `.xlsx` report generation. |
| `playwright` | `>=1.40.0` | Installed in env (1.62.0) | **OPTIONAL** | Headless browser for JavaScript-heavy website email extraction. |
| `flask` & all Flask extensions | `3.1.1` | None | **DROP** | Obsolete legacy framework replaced entirely by FastAPI. |
| `flask-cors` | `5.0.1` | None | **DROP** | Replaced by `fastapi.middleware.cors.CORSMiddleware`. |
| `flask-limiter` | `>=3.5.0` | None | **DROP** | Replaced by RIGHT FIT's custom in-memory rate limiter. |
| `Flask-Caching` | `>=2.3.0` | None | **DROP** | Replaced by Redis caching. |
| `flasgger` | `0.9.7.1` | None | **DROP** | Replaced by native FastAPI OpenAPI documentation (`/docs`). |
| `flask-compress` | `>=1.15.0` | None | **DROP** | Starlette `GZipMiddleware` handles compression. |
| `pytest-flask` | `>=1.3.0` | None | **DROP** | Replaced by `httpx.AsyncClient` and `pytest-asyncio`. |

---

## 3. License and Security Considerations

1. **`google-search-results` (MIT License):** Well-maintained, zero native dependencies, safe for commercial use.
2. **`phonenumbers` (Apache 2.0 License):** Battle-tested Python port of Google's libphonenumber. Zero external dependencies.
3. **`apify-client` (Apache 2.0 License):** Maintained directly by Apify Technologies; handles actor run timeouts and dataset downloads safely.
4. **`PyYAML` (MIT License):** Safe parsing via `yaml.safe_load()` avoids any code execution risk.

---

## 4. Updates to `rightFIT/backend/requirements.txt`

The following lines will be appended to `rightFIT/backend/requirements.txt`:
```txt
# Freelance Intelligence Module & LeadHunter Integration
google-search-results==2.4.2
phonenumbers==8.14.0
apify-client==3.1.3
PyYAML==6.0.3
```
All four packages are verified installed and functional in the current Python environment.
