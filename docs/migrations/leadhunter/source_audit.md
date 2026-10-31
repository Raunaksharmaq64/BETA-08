# LeadHunter Source Code Audit & Feature Inventory

**Project Source:** `C:\Users\Sahil\Desktop\manit\ai agents`  
**Target Destination:** `C:\Users\Sahil\Desktop\manit\rightFIT`  
**Date:** 2026-10-31  
**Author:** Senior Software Architect & Integration Engineer  

---

## 1. Executive Summary

The LeadHunter repository (`ai agents`) provides an end-to-end local business lead discovery and AI outreach engine. It was initially designed as an autonomous service running on port 8001 with both FastAPI/Flask backends, Celery workers, and a Next.js frontend. 

The objective of this migration is to integrate all valuable LeadHunter business logic, collectors, qualification, auditing, AI pitching, and outreach management directly into the **RIGHT FIT platform** as an internal **Freelance Intelligence module**, eliminating the satellite architecture, external HTTP coupling, port 8001 dependencies, and runtime reliance on the `ai agents` folder.

---

## 2. Source Code Inventory & Classification

Every file in the original LeadHunter source has been inspected and categorized into one of four classifications:
- **REUSE:** Useful code adapted directly into the RIGHT FIT Freelance Intelligence module.
- **REWRITE:** Functionality preserved and adapted to RIGHT FIT conventions (e.g., SQLAlchemy Async models, core user isolation, core logging).
- **DROP:** Unnecessary, duplicate, obsolete, unsafe, or Flask-specific legacy code.
- **INVESTIGATE:** Requires deeper verification of external dependencies or security posture.

---

### 2.1 Backend Core & Architecture

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `backend/app_fastapi.py` | FastAPI server entrypoint, middleware, lifespan | **REWRITE** | `backend/app/main.py` | RIGHT FIT already has its main FastAPI app. Routing and startup tasks will be registered in `app/main.py` and `app/api/v1/router.py`. |
| `backend/config.py` | Pydantic settings, environment variables | **REWRITE** | `backend/app/core/config.py` | LeadHunter settings (SerpApi, Apify, Gemini, Brevo/Resend) are folded into RIGHT FIT's `Settings`. |
| `backend/constants.py` | Constants, timeouts, priority mappings | **REUSE** | `backend/app/modules/freelance/constants.py` | Useful scraping timeouts and priority constants. |
| `backend/database_async.py` | SQLModel/SQLAlchemy async engine setup | **DROP** | None | RIGHT FIT already owns `backend/app/core/database.py` with SQLAlchemy async session management. |
| `backend/celery_worker.py` | Celery app and worker task definitions | **REWRITE** | `backend/app/workers/tasks/freelance_tasks.py` | Move Celery tasks into RIGHT FIT's `app.workers.celery_app` using the existing `lead_tasks` queue. |

---

### 2.2 Data Collectors & Scrapers

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `backend/collectors/base_collector.py` | Abstract BaseCollector and Lead dataclass | **REUSE** | `backend/app/modules/freelance/collectors/base_collector.py` | Clean abstract interface for multi-platform business collectors. |
| `backend/collectors/serpapi_collector.py` | Google Maps scraper via SerpApi | **REUSE** | `backend/app/modules/freelance/collectors/serpapi_collector.py` | Reliable Maps discovery collector; includes pagination and coordinate logic. |
| `backend/collectors/apify_collector.py` | Google Maps scraper via Apify Google Places actor | **REUSE** | `backend/app/modules/freelance/collectors/apify_collector.py` | Alternative search provider when SerpApi quota is depleted. |
| `backend/utils/email_scraper.py` | Public email extraction with Playwright fallback | **REWRITE** | `backend/app/modules/freelance/utils/email_scraper.py` | Preserve robust regex, obfuscation decoding, and contact-page spidering. Enforce SSRF protection. |
| `backend/utils/website_auditor.py` | HTML parser, speed, SEO, mobile, SSL audit | **REUSE** | `backend/app/modules/freelance/utils/website_auditor.py` | Comprehensive technical website audit scorecard generator. |

---

### 2.3 Business Logic & Services

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `backend/services/search_service.py` | Discovery orchestration, quota checks, filtering | **REWRITE** | `backend/app/modules/freelance/services/freelance_discovery_service.py` | Unify with Core `FreelanceService` and direct Core database repositories. |
| `backend/services/audit_service.py` | Website audit execution and scorecarding | **REUSE** | `backend/app/modules/freelance/services/audit_service.py` | Audits prospect websites for broken SSL, meta tags, and mobile layout. |
| `backend/services/mockup_service.py` | Dynamic SVG preview generation | **REUSE** | `backend/app/modules/freelance/services/mockup_service.py` | Generates proof-of-concept visual mockups for client outreach. |
| `backend/services/outreach_service.py` | WhatsApp and AI email generation, sending | **REWRITE** | `backend/app/modules/freelance/services/freelance_outreach_service.py` | Integrate with Core `FreelanceService`, mandatory approval state machine, suppression list, and delivery auditing. |
| `backend/utils/ai_writer.py` | Gemini LLM pitch generator with PAS/BAB frameworks | **REUSE** | `backend/app/modules/freelance/utils/ai_writer.py` | Context-aware pitch generation with anti-hallucination guardrails and prompt sanitization. |
| `backend/prompts/outreach_pitches.yaml` | System prompt templates for outreach | **REUSE** | `backend/app/modules/freelance/prompts/outreach_pitches.yaml` | Structured prompt definitions for various tones, languages, and business scenarios. |
| `backend/utils/data_cleaner.py` | Deduplication, phone standardization, health checks | **REUSE** | `backend/app/modules/freelance/utils/data_cleaner.py` | Standardizes phone numbers using `phonenumbers` and categorizes mobile vs landline. |
| `backend/utils/ssrf_guard.py` | SSRF mitigation, IP pinning, DNS rebinding defense | **REUSE** | `backend/app/core/ssrf_guard.py` / `modules/freelance/utils/ssrf_guard.py` | Critical security layer for all external HTTP requests. |
| `backend/utils/whatsapp.py` | WhatsApp click-to-chat URL generator | **REUSE** | `backend/app/modules/freelance/utils/whatsapp.py` | Generates compliant `https://wa.me/` deep links with pre-filled message bodies. |

---

### 2.4 Outreach & Delivery Utilities

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `backend/utils/email_sender.py` | SMTP outbound dispatcher with tracking | **REWRITE** | `backend/app/modules/freelance/utils/email_sender.py` | Enforces explicit approval checks before sending; records delivery evidence. |
| `backend/utils/brevo_email.py` | Brevo API transactional delivery | **REUSE** | `backend/app/modules/freelance/utils/brevo_email.py` | Secondary email delivery provider. |
| `backend/utils/resend_email.py` | Resend API transactional delivery | **REUSE** | `backend/app/modules/freelance/utils/resend_email.py` | Modern developer email provider. |
| `backend/utils/drip_scheduler.py` | Automated drip sequence scheduler | **REWRITE** | `backend/app/modules/freelance/tasks/drip_tasks.py` | Must require explicit candidate consent/initiation; no automated sending without user opt-in. |
| `backend/utils/imap_reader.py` | IMAP reply monitoring & sentiment analysis | **REWRITE** | `backend/app/modules/freelance/services/inbox_service.py` | Monitors candidate's connected inbox for client replies. |

---

### 2.5 Database & Repositories

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `backend/models/models_async.py` | SQLModel entities (`LeadModel`, `SearchHistoryModel`, `MessageLogModel`, `SmtpSettingsModel`, etc.) | **REWRITE** | `backend/app/db/models.py` | Adapt into RIGHT FIT canonical models (`FreelanceOpportunityRecord`, `ContactEvidenceRecord`, `OutreachDraftRecord`, `FreelanceLeadSettingRecord`). |
| `backend/repositories/lead_repository_async.py` | Lead CRUD, filtering, pagination | **REWRITE** | `backend/app/modules/freelance/repositories/freelance_repository.py` | Implements async SQLAlchemy 2.0 query patterns with UUID user IDs. |
| `backend/repositories/config_repository_async.py` | System settings & BYOK keys storage | **REWRITE** | `backend/app/modules/freelance/repositories/setting_repository.py` | Stores encrypted provider keys per user. |
| `backend/repositories/message_repository_async.py` | Outreach draft logs and delivery tracking | **REWRITE** | `backend/app/modules/freelance/repositories/outreach_repository.py` | Maps to Core outreach draft and delivery log records. |
| `backend/repositories/user_repository_async.py` | User management | **DROP** | None | Core user account management and JWT auth are already handled by Core `User`. |

---

### 2.6 FastAPI Route Handlers

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `backend/routes_fastapi/api_leads.py` | Search, list, filter, reminders, bulk scan | **REWRITE** | `backend/app/api/v1/endpoints/freelance.py` | Integrate with Core authentication (`get_current_user`), tenant isolation, and Core services. |
| `backend/routes_fastapi/api_outreach.py` | Pitch generation, draft approval, SMTP dispatch | **REWRITE** | `backend/app/api/v1/endpoints/freelance.py` | Full candidate governance: no auto-send, cryptographic approval hash, suppression list checks. |
| `backend/routes_fastapi/api_config.py` | BYOK keys (SerpApi/Apify/Gemini), export data | **REWRITE** | `backend/app/api/v1/endpoints/freelance.py` | Secure BYOK management with AES encryption. |
| `backend/routes_fastapi/api_subscription.py` | Stripe billing / plan limits | **DROP** | None | RIGHT FIT platform has its own unified tier/quota architecture. |
| `backend/routes_fastapi/auth.py` | Login, signup, password reset | **DROP** | None | Duplicate. RIGHT FIT's `app/api/v1/endpoints/auth.py` is the single source of truth. |
| `backend/routes_fastapi/dashboard.py` | Jinja2 template redirects | **DROP** | None | Obsolete server-side rendered templates; Next.js frontend is used. |

---

### 2.7 Frontend Assets & Pages

| Source Path | Primary Functionality | Classification | Target Location in RIGHT FIT | Rationale / Notes |
|:---|:---|:---:|:---|:---|
| `frontend/src/app/(dashboard)/leads/page.tsx` | Lead listing, filters, search bar, lead cards | **REWRITE** | `frontend/src/app/(dashboard)/freelance/page.tsx` | Upgrade existing Freelance page to provide complete discovery, filtering, and lead management. |
| `frontend/src/components/InteractiveLeadStudio.tsx` | Pitch generation modal and outreach workbench | **REWRITE** | `frontend/src/app/(dashboard)/freelance/[opportunityId]/draft/page.tsx` | Seamless in-app pitch editor with copy, preview, approve, and send controls. |
| `frontend/src/components/WebsiteHealthTester.tsx` | Live website audit visualization | **REUSE** | `frontend/src/components/freelance/WebsiteHealthTester.tsx` | Interactive diagnostic card displaying site performance, speed, and SSL status. |
| `frontend/src/app/(dashboard)/settings/page.tsx` | BYOK key management & SMTP setup | **REWRITE** | `frontend/src/app/(dashboard)/settings/freelance/page.tsx` | Allow candidates to configure SerpApi/Apify/Gemini keys and custom email inboxes safely. |
| `frontend/src/app/(dashboard)/billing/page.tsx` | Stripe payment pricing tables | **DROP** | None | Excluded from Freelance Intelligence module scope. |

---

### 2.8 Obsolete / Legacy Files Dropped

| Source Path | Classification | Detailed Rationale |
|:---|:---:|:---|
| `scratch/legacy_flask_backup/*` | **DROP** | Deprecated Flask routes replaced by FastAPI. |
| `backend/Dockerfile.legacy` | **DROP** | Legacy Docker configuration. |
| `backend/templates/*` | **DROP** | Obsolete Jinja2 server-rendered HTML templates. |
| `ngrok-v3-stable-windows-amd64/*` | **DROP** | Local tunneling binary not needed in production. |
| `redis/*` (Windows binaries) | **DROP** | Development local executables. Docker or system Redis is used. |
| `backups/*` | **DROP** | Old SQL dumps preserved in source repository; not copied into RIGHT FIT. |

---

## 3. Audit Verification Conclusion

The LeadHunter codebase contains high-quality, battle-tested business logic for:
1. Google Maps multi-provider discovery (SerpApi + Apify fallback).
2. Contact extraction, phone categorization (`phonenumbers`), and SSRF-hardened scraping.
3. Automated technical website audits (speed, SEO, SSL, mobile responsiveness).
4. Grounded AI pitch copywriting via Google Gemini using proven sales frameworks (PAS, BAB).
5. Safe outreach workflows with strict candidate approval gating.

All relevant features can be cleanly encapsulated inside a modular structure under `backend/app/modules/freelance/` and exposed via RIGHT FIT's `app/api/v1/endpoints/freelance.py`, while eliminating all external network hops to port 8001.
