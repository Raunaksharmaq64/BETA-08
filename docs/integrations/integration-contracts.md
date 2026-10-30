# Integration Contracts & Data Boundary Standards

- **Title:** Inter-Service Contract Governance
- **Purpose:** Mandates schema definitions, versioning rules, and DTO validation for cross-service payloads.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Schema Authority
All payloads transferred between Core Backend, LeadHunter, and Startup Intelligence must have explicit schemas maintained in `contracts/`:
- `contracts/leads/lead_schema.json`: Schema for local business leads and audit metrics.
- `contracts/pain_points/pain_point_schema.json`: Schema for startup issues and developer signals.
- `contracts/common/envelope_schema.json`: Standard envelope, pagination, and error structures.

## 2. Backward Compatibility Guarantee
- Field additions are always optional (`Optional[T] = None`).
- Existing fields cannot be renamed or removed within the same API version.
- Upstream parsers must ignore unknown keys (Pydantic `extra = "ignore"`).

## 3. Open Questions & TBDs
- [TBD] Automated schema compatibility checks in GitHub Actions CI using OpenAPI diff.

