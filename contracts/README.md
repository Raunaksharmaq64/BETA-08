# Integration Contracts & Data Schemas

- **Title:** RIGHT FIT Inter-Service API Contracts
- **Purpose:** Central repository for shared JSON schemas and Pydantic contract models used across Core Backend, LeadHunter, and Startup Intelligence.
- **Status:** DRAFT / ARCHITECTURE SETUP
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

## Contract Organization
- `common/`: Standard response wrappers, pagination schemas, and error objects.
- `auth/`: Token and authentication payloads.
- `users/`: User profile and preference schemas.
- `resumes/`: Parsed resume structures and skill token schemas.
- `jobs/`: Normalized job opportunity schemas from 50+ ATS sources.
- `opportunities/`: Generic aggregated opportunity abstraction.
- `applications/`: CRM stage transition contracts.
- `leads/`: Local business and website audit schemas (LeadHunter).
- `pain_points/`: Startup community technical issue schemas (Startup Intelligence).

