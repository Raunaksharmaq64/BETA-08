# RIGHT FIT — LeadHunter Migration & Freelance Intelligence Module

> [!NOTE]
> **Status:** MIGRATION COMPLETE & VERIFIED
> **Module Path:** `rightFIT/backend/app/modules/freelance/`
> **Frontend Workbench:** `rightFIT/frontend/src/app/(dashboard)/freelance/`

---

## 1. Executive Summary

The standalone **LeadHunter** prototype (`ai agents`) has been fully migrated into the **RIGHT FIT platform** (`rightFIT`) as an integrated, enterprise-grade **Freelance Intelligence module**. 

The migration was executed under a strict Modular Monolith architectural pattern:
- **Zero Runtime Dependencies on Legacy Folder:** RIGHT FIT is 100% self-contained and independently deployable.
- **Port 8001 Satellite Elimination:** Standalone satellite listeners on port 8001, external inter-service HTTP hops, and satellite docker services have been retired.
- **Unified Core Database:** All opportunities, contact evidence records, candidate settings, and outreach drafts reside directly within PostgreSQL via async SQLAlchemy 2.0.
- **Full Feature Parity & Security Hardening:** Native SerpApi & Apify collectors, 100-point website diagnostic audits, SSRF protection with IP pinning, prompt injection sanitization, cryptographic approval state machine, and dynamic SVG concept mockup generation.

---

## 2. Source Audit & Feature Disposition

| Source Component / Feature | Original File (`ai agents`) | Target Location (`rightFIT`) | Status | Architectural Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Maps Lead Discovery** | `scrapers/maps_scraper.py` | `app/modules/freelance/collectors/serpapi_collector.py` | **REWRITE** | Converted to async, coordinate pagination, structured typing. |
| **Apify Fallback Collector** | `scrapers/apify_actor.py` | `app/modules/freelance/collectors/apify_collector.py` | **REWRITE** | Native async actor fallback for `compass/crawler-google-places`. |
| **Data Cleaning & Phone Normalization** | `utils/cleaner.py` | `app/modules/freelance/utils/data_cleaner.py` | **REUSE** | Enhanced with E.164 standardization & mobile vs landline classification. |
| **SSRF Guard & Probing** | *None (Security Vulnerability)* | `app/modules/freelance/utils/ssrf_guard.py` | **NEW** | Pinned IP adapter, DNS rebinding mitigation, blocks cloud metadata (`169.254.169.254`). |
| **100-Point Website Auditor** | `auditor/site_audit.py` | `app/modules/freelance/utils/website_auditor.py` | **REWRITE** | Pure HTML/DOM parser for Speed, SEO, Mobile viewport, SSL, and Alt tags. |
| **Email Discovery & Obfuscation** | `enrichment/email_finder.py` | `app/modules/freelance/utils/email_scraper.py` | **REWRITE** | SSRF-guarded contact page scraper with regex and obfuscated email decoding. |
| **AI Pitch Generator** | `ai/pitch_generator.py` | `app/modules/freelance/utils/ai_writer.py` | **REWRITE** | Prompt injection sanitization, sliding-window rate limiting, deterministic fallbacks. |
| **Outreach Approval State Machine** | `outreach/sender.py` | `app/modules/freelance/services/outreach_service.py` | **REWRITE** | Enforces human-in-the-loop review; edits invalidate approval via SHA-256 hash. |
| **WhatsApp Outreach Link** | *None* | `app/modules/freelance/utils/whatsapp.py` | **NEW** | Compliant click-to-chat `wa.me` URL generator for verified mobile contacts. |
| **SVG Mockup Generator** | `mockups/builder.py` | `app/modules/freelance/services/mockup_service.py` | **REWRITE** | Dynamic, XSS-safe SVG landing page mockups tailored to client business category. |
| **Legacy Flask Routes** | `app.py`, `routes/*.py` | `app/api/v1/endpoints/freelance.py` | **DROP** | Replaced with native FastAPI async endpoints on port 8000. |

---

## 3. Database & Schema Alignment

Core PostgreSQL schema was updated to own all freelance entities without data loss:
- `freelance_opportunities`: Discovered business leads, broken website flags, rating, location, and fit scores.
- `contact_evidence`: Verified emails, phone numbers, contact types, and discovery timestamps.
- `freelance_search_history`: Search queries, metro markets, lead yields, and timestamps.
- `freelance_candidate_settings`: BYOK credentials (SerpApi, Apify, Gemini) and candidate custom SMTP delivery settings.
- `freelance_outreach_drafts`: Pitch bodies, subject lines, channels, candidate edits count, and SHA-256 approval verification hashes.
- `saved_freelance_opportunities`: Candidate bookmarks and private notes.
- `outreach_suppressions`: Do-not-contact recipient exclusion ledger (unsubscribes, bounces).

---

## 4. Frontend Workbench Modules (Next.js 16)

The Next.js presentation layer (`frontend/src/app/(dashboard)/freelance/`) was modernized with responsive, accessible UI widgets:
1. **Catalog & Discovery Dashboard (`/freelance`):**
   - Deep Scan and active-website toggles.
   - Metro query input and max results limiters.
   - Recent search history chips for one-click re-querying.
   - Website health status and match scores on each lead card.
2. **Opportunity Detail & Technical Diagnostics (`/freelance/[opportunityId]`):**
   - Live 100-point Technical Health & Audit scorecard (Speed, SEO, Mobile, SSL, Alt tags) with actionable recommendations.
   - Interactive SVG Mockup preview container with one-click SVG download.
   - Direct WhatsApp Outreach widget generating formatted click-to-chat links.
   - Contact Evidence Ledger showing verified public contacts with confidence badges.
3. **Candidate Outreach Workbench (`/freelance/[opportunityId]/draft`):**
   - AI Pitch generation tailoring with Tone (`professional`, `consultative`, `bold`, `technical`), service propositions, and target word counts.
   - Anti-hallucination warnings and live word counter.
   - Explicit Candidate Approval Confirmation Dialog enforcing human review.
   - Visual notice alerting candidates that any text modification automatically resets status to `PENDING_REVIEW`.
4. **Outreach Activity & Delivery Gateway (`/freelance/outreach`):**
   - Audit trail of all prepared, approved, and dispatched outreach records.
   - Recipient Do-Not-Contact suppression list management.
   - Candidate BYOK API keys configuration & custom SMTP delivery credentials management.
5. **Saved Bookmarks (`/freelance/saved`):**
   - Interactive candidate note updating and unsaving/removal controls.

---

## 5. Verification & Test Results

All regression and functional unit tests pass with zero failures:
```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.0, pluggy-1.6.0
rootdir: C:\Users\Sahil\Desktop\manit\rightFIT
collected 8 items

tests/unit/test_freelance_intelligence_module.py::test_ssrf_guard_blocks_private_and_metadata_ips PASSED [ 12%]
tests/unit/test_freelance_intelligence_module.py::test_prompt_injection_sanitization PASSED [ 25%]
tests/unit/test_freelance_intelligence_module.py::test_data_cleaner_phone_standardization PASSED [ 37%]
tests/unit/test_freelance_intelligence_module.py::test_data_cleaner_priority_assignment PASSED [ 50%]
tests/unit/test_freelance_intelligence_module.py::test_mockup_service_svg_generation PASSED [ 62%]
tests/unit/test_freelance_intelligence_module.py::test_whatsapp_messenger_link_generation PASSED [ 75%]
tests/unit/test_freelance_intelligence_module.py::test_ai_outreach_writer_deterministic_fallback PASSED [ 87%]
tests/unit/test_freelance_intelligence_module.py::test_outreach_approval_state_machine_and_invalidation PASSED [100%]

============================= 8 passed in 38.59s ==============================
```

All Core Endpoints Verified (`200 OK`):
- `GET /health/live` — 200 OK
- `GET /api/v1/dashboard` — 200 OK
- `GET /api/v1/opportunities/all` — 200 OK
- `GET /api/v1/startups` — 200 OK
- `GET /api/v1/startups/integration-status` — 200 OK (graceful circuit-breaker mode)
- `GET /api/v1/market/demand/skills` — 200 OK (audited market demand aggregation)
- `GET /api/v1/freelance` — 200 OK
- `GET /api/v1/freelance/integration-status` — 200 OK
