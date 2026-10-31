# Hybrid Aggregation Architecture & System Boundaries

## 1. Architectural Strategy: Option A (Hybrid Architecture)
RIGHT FIT maintains a strict boundary between the central **Core Career Engine** and specialized satellite services (**LeadHunter AI** and **Startups-problems-hunter**).

```
                      +---------------------------------------+
                      |       Next.js Web Frontend            |
                      | (/dashboard, /opportunities, /saved)  |
                      +-------------------+-------------------+
                                          |
                                          | HTTP REST (Bearer / HttpOnly Cookie)
                                          v
                      +---------------------------------------+
                      |         RIGHT FIT Core Engine         |
                      |  - UnifiedOpportunityService          |
                      |  - Common Envelope Formatter (v1.0)   |
                      |  - Candidate CRM & Feedback Store     |
                      +---+-------------------------------+---+
                          |                               |
          Read Ingested   |                               | Read Ingested
          Records via DB  |                               | Records via DB
                          v                               v
            +---------------------------+   +---------------------------+
            |  freelance_opportunities  |   |   startup_opportunities   |
            +-------------^-------------+   +-------------^-------------+
                          |                               |
                 Ingested |                      Ingested |
                 Leads    |                      Leads    |
            +-------------+-------------+   +-------------+-------------+
            |    LeadHunter Adapter     |   | Startup Intelligence      |
            |     (Circuit Breaker)     |   | Adapter (Circuit Breaker) |
            +-------------^-------------+   +-------------^-------------+
                          |                               |
             REST API Sync|                  REST API Sync|
                          v                               v
            +---------------------------+   +---------------------------+
            |     LeadHunter AI         |   | Startups-problems-hunter  |
            |     (Independent API)     |   |    (Independent API)      |
            +---------------------------+   +---------------------------+
```

## 2. Core Responsibilities
- **Ownership of Aggregation**: Core owns aggregation queries across canonical jobs, freelance leads, and startup signals.
- **Envelope Formatting**: Transforms specialized database schemas into a unified, versioned `OpportunityEnvelope` v1.0.
- **Candidate Privacy & Isolation**: Bookmarks and feedback belong exclusively to candidate profiles. Satellite evidence is immutable.
- **Zero Opaque Universal Scores**: Skill fit, business ratings, and pain point urgency remain distinctly typed fields. They are NEVER synthesized into a single misleading universal rank.

