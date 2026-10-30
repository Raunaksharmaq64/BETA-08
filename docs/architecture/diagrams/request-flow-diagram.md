# Request Communication Flow Diagram

- **Title:** End-to-End Request Flow & Response Lifecycles
- **Purpose:** Visualizes synchronous and asynchronous request propagation from user action through Core API, satellite services, and database layers.
- **Status:** APPROVED
- **Owner:** Principal Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

```mermaid
sequenceDiagram
    autonumber
    actor User as Candidate / User
    participant Frontend as Next.js 16 Web Dashboard
    participant Nginx as Nginx Reverse Proxy
    participant CoreAPI as Core Career Engine (FastAPI)
    participant CoreDB as PostgreSQL (career_core)
    participant Satellite as Satellite Service (LeadHunter / Startup Intel)
    participant SatelliteDB as PostgreSQL (leadhunter / startup_intel)

    User->>Frontend: Click "Explore Opportunities"
    Frontend->>Nginx: HTTPS GET /api/v1/opportunities (Bearer JWT)
    Nginx->>CoreAPI: HTTP GET /api/v1/opportunities (X-Request-ID, User Context)
    
    rect rgb(240, 248, 255)
        note over CoreAPI,CoreDB: Fetching Core Job Matches
        CoreAPI->>CoreDB: SELECT * FROM career_core.job_matches WHERE user_id = :uid
        CoreDB-->>CoreAPI: Return Matched ATS Jobs
    end

    rect rgb(255, 250, 240)
        note over CoreAPI,Satellite: Brokering Satellite Opportunities
        CoreAPI->>Satellite: HTTP GET /api/v1/leads (X-Internal-Service-Key, X-Request-ID)
        Satellite->>SatelliteDB: SELECT * FROM leads WHERE is_broken_website = true
        SatelliteDB-->>Satellite: Return Leads
        Satellite-->>CoreAPI: HTTP 200 OK (JSON Payload)
    end

    note over CoreAPI: Core aggregates & normalizes unified opportunity payload
    CoreAPI-->>Nginx: HTTP 200 OK (Unified JSON Response)
    Nginx-->>Frontend: HTTP 200 OK (JSON Response)
    Frontend-->>User: Render Opportunity Grid & Fit Scores
```

