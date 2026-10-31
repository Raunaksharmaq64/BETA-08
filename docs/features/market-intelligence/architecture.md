# Architecture: Market & Compensation Intelligence

## 1. System Context & Service Boundaries
The Market & Compensation Intelligence engine resides within the Core Career Engine of RIGHT FIT. It provides empirical macro intelligence across career markets without violating architectural domain boundaries:
- **Core Career Engine Ownership**: Core owns canonical opportunity vacancies (`canonical_opportunities`), candidate profiles (`users`, `resumes`), market data sources (`market_data_sources`), skill taxonomy (`skills_taxonomy`, `skill_aliases`), demand snapshots (`skill_demand_snapshots`), compensation records (`compensation_observations`), and candidate skill gap recommendations (`candidate_skill_gap_recommendations`).
- **Satellite Independence**: LeadHunter AI and Startup Intelligence feed their opportunities into the Core aggregation pipeline via standardized adapters. Market intelligence aggregates over verified canonical postings across these streams.
- **Data Stores**: All persistent entities reside in the Core PostgreSQL database across 6 dedicated relational tables, fully indexed on query dimensions (slugs, time windows, role categories, and user IDs).

## 2. Relational Schema Topology
```mermaid
erDiagram
    MARKET_DATA_SOURCES ||--o{ COMPENSATION_OBSERVATIONS : "provides"
    SKILLS_TAXONOMY ||--o{ SKILL_ALIASES : "resolves"
    SKILLS_TAXONOMY ||--o{ SKILL_DEMAND_SNAPSHOTS : "tracks"
    SKILLS_TAXONOMY ||--o{ CANDIDATE_SKILL_GAP_RECOMMENDATIONS : "targets"
    USERS ||--o{ CANDIDATE_SKILL_GAP_RECOMMENDATIONS : "receives"
    CANONICAL_OPPORTUNITIES ||--o{ COMPENSATION_OBSERVATIONS : "corroborates"

    SKILLS_TAXONOMY {
        uuid id PK
        string canonical_name
        string slug UK
        string category
        string technology_family
        text description
        boolean is_active
    }

    SKILL_ALIASES {
        uuid id PK
        uuid skill_id FK
        string alias UK
        string source_type
        float confidence
    }

    SKILL_DEMAND_SNAPSHOTS {
        uuid id PK
        uuid skill_id FK
        string time_window
        string role_category
        string geography
        int distinct_job_count
        int sample_size
        float frequency_pct
        string trend_direction
        date snapshot_date
    }

    COMPENSATION_OBSERVATIONS {
        uuid id PK
        uuid opportunity_id FK
        uuid source_id FK
        string role_title
        string role_category
        string geography
        string experience_level
        string compensation_type
        string currency
        numeric base_salary_min
        numeric base_salary_max
        numeric total_compensation_min
        numeric total_compensation_max
        numeric hourly_rate
        numeric equity_pct_min
        numeric equity_pct_max
        timestamp observed_at
    }

    CANDIDATE_SKILL_GAP_RECOMMENDATIONS {
        uuid id PK
        uuid user_id FK
        uuid skill_id FK
        string target_role
        string gap_status
        float role_demand_frequency_pct
        int distinct_job_count
        text notes
        timestamp updated_at
    }

    MARKET_DATA_SOURCES {
        uuid id PK
        string source_key UK
        string name
        string source_type
        string ingestion_frequency
        float reliability_score
        boolean is_active
    }
```

## 3. Core Engine Components
1. **`MarketIntelligenceService`** (`backend/app/services/market_intelligence_service.py`):
   - Central orchestration service executing taxonomy lookups, deterministic alias mapping, distinct job vacancy counting, compensation percentiles calculation, and personalized skill-gap diagnostic generation.
2. **REST Endpoints Router** (`backend/app/api/v1/endpoints/market.py`):
   - High-performance, cached, and authenticated endpoints exposing market demand metrics, compensation benchmarks, and recommendation management.
3. **Next.js Frontend Architecture** (`frontend/src/app/(dashboard)/market-intelligence/*` & `/compensation`):
   - Responsive interfaces built with Tailwind CSS, supporting interactive time-window filters (`7d`, `30d`, `90d`), pay structure isolation toggles, and status progression controls.

