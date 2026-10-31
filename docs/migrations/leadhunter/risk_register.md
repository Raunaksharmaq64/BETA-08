# Freelance Intelligence Migration — Risk Register & Mitigation Strategy

**Project:** RIGHT FIT — LeadHunter Migration  
**Date:** 2026-10-31  
**Status:** ACTIVE GOVERNANCE  

---

## 1. Risk Matrix

| Risk ID | Risk Description | Severity | Likelihood | Impact Area | Mitigation Strategy |
|:---:|:---|:---:|:---:|:---:|:---|
| **R-01** | **Server-Side Request Forgery (SSRF)** during website health checks and email scraping. | **HIGH** | Medium | Security | Enforce centralized `ssrf_guard.py` on all outbound HTTP calls. Block loopback, RFC 1918 private IPs, cloud metadata endpoints (`169.254.169.254`), and pin resolved DNS IPs to prevent DNS rebinding. |
| **R-02** | **Accidental Automated Email Transmission** violating CAN-SPAM or candidate intent. | **HIGH** | Low | Compliance / Trust | Strictly enforce candidate approval state machine. System cannot dispatch emails unless `is_approved = True`. Any edit resets approval. Mandatory suppression list checks. |
| **R-03** | **Search Provider Quota Depletion** (SerpApi / Apify). | **MEDIUM** | High | Availability | Dual-provider support (SerpApi with Apify fallback), persistent search history caching, and candidate BYOK API key vault in settings. |
| **R-04** | **Hallucinated or Invented Information** in AI pitch generation. | **MEDIUM** | Medium | Quality / Reputational | Grounded prompt design (PAS/BAB frameworks) injecting only verified scraped details (Maps rating, review counts, verified website status). Strict banned-phrase filters. |
| **R-05** | **Duplicate Opportunity Ingestion** cluttering candidate feeds. | **MEDIUM** | High | Data Quality | Multi-signal deduplication query matching on `place_id`, `leadhunter_lead_id`, and `LOWER(business_name) + LOWER(city)`. Updates metadata idempotently without creating duplicates. |
| **R-06** | **Cross-User Data Leakage / IDOR** in freelance leads or drafts. | **HIGH** | Low | Privacy / Security | Explicit user scoping on all queries using Core JWT `current_user.id`. Cascade deletion on account removal. |
| **R-07** | **Regression of Existing Platform Modules** (Jobs, Resumes, Startups). | **HIGH** | Low | Reliability | Keep all freelance domain logic isolated within `backend/app/modules/freelance/`. Preserve API contract. Continuous execution of 235 existing automated test cases. |
| **R-08** | **Celery / Redis Outage in Local Development**. | **LOW** | Medium | Developer DX | Provide synchronous background task runner fallback (`BackgroundTasks`) when Celery/Redis is unavailable. |

---

## 2. Security & Compliance Checklist

- [x] SSRF guard blocks `127.0.0.1`, `localhost`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`.
- [x] Response payload size limited to 5MB to prevent zip bombs / memory exhaustion.
- [x] Redirect limit capped at 5 hops.
- [x] Prompt injection filter neutralizes `[INST]`, `<<SYS>>`, `system override`, and hidden HTML comments.
- [x] Candidate BYOK secrets encrypted at rest using AES-GCM cryptography.
- [x] Outreach draft approval strictly invalidated on any content modification.
- [x] Unsubscribe suppression list checked before any outbound email dispatch.
- [x] Zero hardcoded API keys or external secrets in source control.
