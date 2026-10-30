# High-Level Architecture Diagram

- **Title:** RIGHT FIT Option A Hybrid Architecture Diagram
- **Purpose:** Visualizes subsystem topology, service-to-service communication paths, and isolated storage boundaries.
- **Status:** APPROVED
- **Owner:** Principal Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

```mermaid
flowchart TD
    User["User Web Browser"]
    
    subgraph IngressLayer ["Ingress & Reverse Proxy"]
        Nginx["Nginx Reverse Proxy (Port 80/443)"]
    end

    subgraph PresentationLayer ["Presentation Layer"]
        Frontend["Next.js 16 App Router (Port 3000)"]
    end

    subgraph CoreBackendLayer ["Core Career Engine (Primary Orchestrator)"]
        CoreAPI["FastAPI Core Backend (Port 8000)"]
        CoreWorker["Celery Worker (career_tasks)"]
    end

    subgraph SatelliteServicesLayer ["Independent Satellite Services (Private Mesh)"]
        LeadHunter["LeadHunter AI Service (Port 8001)"]
        StartupIntel["Startup Intelligence Service (Port 8002)"]
    end

    subgraph DataLayer ["Data & Storage Layer (Isolated Boundaries)"]
        DBCore[("PostgreSQL: career_core")]
        DBLead[("PostgreSQL: leadhunter_db")]
        DBStartup[("PostgreSQL: startup_intel_db")]
        RedisQueue[("Redis 7: Isolated Task Queues")]
        S3Bucket[("AWS S3: Encrypted Resumes")]
    end

    User --> Nginx
    Nginx -->|/| Frontend
    Nginx -->|/api/| CoreAPI
    Frontend -->|Authenticated REST| CoreAPI
    
    CoreAPI --> CoreWorker
    CoreAPI -->|Internal REST| LeadHunter
    CoreAPI -->|Internal REST| StartupIntel
    
    CoreAPI --> DBCore
    CoreAPI --> S3Bucket
    LeadHunter --> DBLead
    StartupIntel --> DBStartup
    CoreWorker --> RedisQueue
```

---

## Architectural Rules Illustrated
1. **Frontend Isolation:** Client requests enter through Nginx; web browser never connects directly to satellite services.
2. **Private Network Mesh:** LeadHunter and Startup Intelligence reside in the internal Docker network (`rightfit-network`).
3. **Database Boundary Protection:** Each service connects strictly to its own dedicated database schema.

