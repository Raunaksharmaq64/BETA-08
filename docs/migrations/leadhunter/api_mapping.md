# LeadHunter to RIGHT FIT REST API Endpoint Mapping

**Project:** RIGHT FIT — Freelance Intelligence Integration  
**Date:** 2026-10-31  
**Status:** MAPPED  

---

## 1. Overview & Architecture Transition

Previously, the RIGHT FIT Core backend invoked LeadHunter via the `LeadHunterAdapter` HTTP client targeting `http://localhost:8001`. 

In the target architecture:
1. All client requests route through the single unified RIGHT FIT Core FastAPI server (`http://localhost:8000/api/v1/freelance/...`).
2. Authentication is strictly enforced using RIGHT FIT's `get_current_user` JWT bearer dependency.
3. Service calls execute internally in-process within the Python runtime.
4. No external network hop, circuit breaker degradation, or port 8001 listener is required.

---

## 2. API Endpoint Mapping Specification

| Action / Capability | Legacy LeadHunter Path (`ai agents`) | Canonical RIGHT FIT Path (`rightFIT`) | HTTP Method | Auth Required | Request / Response Changes |
|:---|:---|:---|:---:|:---:|:---|
| **Search & Discover Leads** | `POST /api/leads/search` | `POST /api/v1/freelance/scan-leads` | POST | Yes | Payload: `{ query, city, max_results, include_with_website, deep_scan }`. Directly runs discovery and persists canonical opportunities. |
| **List Freelance Opportunities** | `GET /api/leads` | `GET /api/v1/freelance` | GET | Yes | Query params: `city`, `category`, `classification_state`, `query`, `page`, `per_page`. |
| **Get Opportunity Detail** | `GET /api/leads/{id}` | `GET /api/v1/freelance/{opportunity_id}` | GET | Yes | Returns opportunity, website audit results, contact evidence ledger, and related outreach drafts. |
| **Save / Bookmark Lead** | N/A (Auto-saved) | `POST /api/v1/freelance/{opportunity_id}/save` | POST | Yes | Saves to candidate bookmarks with optional personal notes. |
| **List Saved Opportunities** | `GET /api/leads?saved=true` | `GET /api/v1/freelance/saved/all` | GET | Yes | Scoped to current authenticated candidate. |
| **Technical Website Audit** | `POST /api/leads/{id}/audit` | `POST /api/v1/freelance/{opportunity_id}/audit` | POST | Yes | Triggers SSRF-guarded audit; updates opportunity audit data. |
| **Generate AI Pitch** | `POST /api/outreach/generate-email-ai` | `POST /api/v1/freelance/{opportunity_id}/draft` | POST | Yes | Generates grounded PAS/BAB pitch using Gemini and YAML templates; saves as `OutreachDraftRecord`. |
| **Edit Outreach Draft** | `POST /api/outreach/edit` | `PUT /api/v1/freelance/drafts/{draft_id}` | PUT | Yes | Updates message body or subject; invalidates prior approval for safety. |
| **Approve Outreach Draft** | N/A (LeadHunter had no approval gate) | `POST /api/v1/freelance/drafts/{draft_id}/approve` | POST | Yes | Explicit candidate review confirmation; records approval timestamp and body hash. |
| **Send Approved Outreach** | `POST /api/outreach/send-smtp-email` | `POST /api/v1/freelance/drafts/{draft_id}/send` | POST | Yes | Requires `is_approved = True`. Dispatches message via SMTP and records delivery log. |
| **Generate WhatsApp Link** | `POST /api/whatsapp/generate` | `POST /api/v1/freelance/{opportunity_id}/whatsapp-link` | POST | Yes | Generates compliant `wa.me` deep link with pre-filled message text. Zero auto-send. |
| **Add to Suppression List** | N/A (Manual DB) | `POST /api/v1/freelance/suppression` | POST | Yes | Adds recipient email to opt-out suppression ledger. |
| **Search History** | `GET /api/leads/history` | `GET /api/v1/freelance/history` | GET | Yes | Returns candidate's recent discovery searches. |
| **Candidate Freelance Keys** | `POST /api/config/user/keys/*` | `POST /api/v1/freelance/settings/keys` | POST | Yes | Allows candidate to configure BYOK SerpApi, Apify, or Gemini API keys. |

---

## 3. Retiring Obsolete Endpoints & Configurations

The following endpoints and configuration parameters are scheduled for deprecation and removal:

1. **`LEADHUNTER_BASE_URL`:** Removed from `backend/app/core/config.py` and `.env.example`.
2. **`GET /freelance/integration-status`:** Deprecated circuit-breaker status endpoint; updated to report native internal engine status `ONLINE`.
3. **`services/leadhunter` Directory:** Removed entirely after Phase 5.
4. **LeadHunter satellite service in `docker-compose.yml`:** Removed.
