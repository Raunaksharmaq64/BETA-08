# External Providers & AI Integrations

- **Title:** External Third-Party APIs & AI Gateway Specification
- **Purpose:** Documents external API quotas, fallbacks, authentication keys, and failure resilience.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. External Third-Party APIs Inventory

| Provider | Purpose | Primary Consumer | Fallback Mechanism |
| :--- | :--- | :--- | :--- |
| **Google Gemini API** | Resume parsing, pitch drafting, STAR interview generation | Core API & Satellites | Local deterministic templates / OpenAI fallback |
| **SerpApi** | Google Maps local business data scraping | LeadHunter | Apify Google Maps actor fallback |
| **Apify** | Web & Maps scraping alternative | LeadHunter | SerpApi / Direct crawler fallback |
| **Serper.dev** | Web and Google organic search queries | Startup Intelligence | DuckDuckGo with Yahoo Search fallback |
| **Tomba.io / Hunter.io** | B2B verified email lookups for business owners | Startup Intelligence | Domain MX heuristic & scraping fallback |

## 2. AI Provider Gateway Design
- All AI calls are routed through an abstract provider interface (`backend/app/integrations/ai_providers/`).
- Prevents vendor lock-in and allows runtime swapping between Google Gemini, Anthropic Claude, and OpenAI without altering business logic.

## 3. Circuit Breaking & Quota Guards
- System monitors `429 Too Many Requests` responses.
- When an API key reaches its monthly quota, the system switches to graceful fallback mode and notifies the administrator via structured error logs.

## 4. Open Questions & TBDs
- [TBD] Dedicated proxy rotation provider (BrightData / ScrapingBee) if scraper blocks increase.

