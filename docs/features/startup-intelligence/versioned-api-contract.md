# Startup Intelligence — Versioned API Contract
## Workstream B Specification

- **Module:** `startup-intelligence`
- **Protocol:** HTTP REST / JSON
- **Version:** `1.0.0`
- **Service Port:** `8002` (Configurable via `PORT` environment variable)

---

## 1. Service Identification & Security Headers

Every request from RIGHT FIT Core to Startup Intelligence carries mandatory service authentication headers:

```http
Authorization: Bearer <INTERNAL_SERVICE_KEY>
X-Internal-Service-Key: <INTERNAL_SERVICE_KEY>
X-Service-Name: rightfit-core
X-Correlation-ID: <UUID-v4>
Accept: application/json
Content-Type: application/json
```

---

## 2. API Endpoints

### 2.1 Health Check
- **URI:** `GET /health`
- **Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "startup-intelligence",
  "version": "1.0.0",
  "storage": "json",
  "records_count": 598,
  "timestamp": "2026-10-31T05:50:00.000Z"
}
```

### 2.2 List Leads
- **URI:** `GET /api/leads`
- **Query Parameters:**
  - `category` (optional string): 'Development', 'Performance', 'UI/UX', 'SEO', 'AI'
  - `min_score` (optional integer): 1 to 10
  - `source` (optional string): Case-insensitive source name match
  - `limit` (optional integer): Max items to return
  - `offset` (optional integer): Offset for pagination
- **Response (200 OK):**
```json
[
  {
    "id": "662e18c1-d5da-45cd-8dcb-05c860acddf0",
    "startup_name": "Growth Stage Startup",
    "category": "UI/UX",
    "detected_signal": "General startup feedback or launch: Onboarding drop-offs",
    "insight": "New launches need clean onboarding flows to convert traffic into signups.",
    "opportunity": "UX/UI Landing Page Audit & Redesign.",
    "pitch_idea": "Hi there! I noticed minor signup flow issues...",
    "score": 7,
    "score_explanation": "Preliminary rating based on feed signal keywords.",
    "source": "Reddit RSS (/r/saas)",
    "url": "https://example.com",
    "contact_info": {
      "author": "reddit_user",
      "email": "",
      "twitter": "",
      "linkedin": ""
    },
    "status": "New",
    "created_at": "2026-10-30T20:22:37.000Z",
    "analyzed": true,
    "raw_text": "Full text of the original post...",
    "matched_skills": ["React", "Next.js"],
    "match_percentage": 90,
    "tech_audit": {
      "seo_score": 85,
      "performance_score": 62,
      "mobile_score": 78,
      "tech_stack": ["React", "Next.js", "Vercel"],
      "issues": ["Large uncompressed assets", "Missing viewport meta tag"]
    }
  }
]
```

### 2.3 Get Lead by ID
- **URI:** `GET /api/leads/{id}`
- **Response (200 OK):** Detailed lead object or `404 Not Found`.

### 2.4 Trigger Feed Scraper
- **URI:** `POST /api/scrape/feeds`
- **Response (200 OK):**
```json
{
  "success": true,
  "new_leads_count": 12,
  "skipped_count": 48,
  "logs": [
    "Discovered 60 total raw signals in target feeds.",
    "Scraping completed. Added 12 new leads, skipped 48 duplicates."
  ]
}
```

### 2.5 Analyze Lead
- **URI:** `POST /api/leads/analyze`
- **Body:** `{"id": "662e18c1-d5da-45cd-8dcb-05c860acddf0"}`
- **Response (200 OK):** Updated lead object enriched with website audit metrics and Gemini AI opportunity mapping.

