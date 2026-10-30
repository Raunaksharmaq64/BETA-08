# Data Ownership Diagram

- **Title:** Relational Schema & Queue Ownership Diagram
- **Purpose:** Visualizes data ownership boundaries, schema isolation, and Redis queue allocations.
- **Status:** APPROVED
- **Owner:** Database Architect (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

```mermaid
flowchart TD
    subgraph Services ["Application Services"]
        CoreAPI["Core Career Engine"]
        LeadHunter["LeadHunter AI"]
        StartupIntel["Startup Intelligence"]
    end

    subgraph DatabaseEngine ["PostgreSQL 16 Engine"]
        subgraph SchemaCore ["career_core (Managed by Core Alembic)"]
            T1["users"]
            T2["profiles"]
            T3["resumes"]
            T4["jobs"]
            T5["job_matches"]
            T6["applications"]
        end

        subgraph SchemaLead ["leadhunter_db (Managed by LeadHunter)"]
            T7["businesses"]
            T8["website_audits"]
            T9["leads"]
            T10["outreach_logs"]
        end

        subgraph SchemaStartup ["startup_intel_db (Managed by Startup Intel)"]
            T11["startups"]
            T12["pain_points"]
            T13["evidence"]
            T14["pitch_drafts"]
        end
    end

    subgraph RedisBroker ["Redis 7 In-Memory Broker"]
        Q1["career_tasks"]
        Q2["lead_tasks"]
        Q3["startup_tasks"]
        Q4["notification_tasks"]
    end

    CoreAPI ===|Owns & Migrates| SchemaCore
    LeadHunter ===|Owns & Migrates| SchemaLead
    StartupIntel ===|Owns & Migrates| SchemaStartup

    CoreAPI -.->|Enqueues / Consumes| Q1
    CoreAPI -.->|Enqueues / Consumes| Q4
    LeadHunter -.->|Enqueues / Consumes| Q2
    StartupIntel -.->|Enqueues / Consumes| Q3
```

---

## Data Boundary Directives
* Direct queries across schemas are strictly prohibited.
* Data exchange between schemas occurs exclusively via authenticated REST API endpoints.

