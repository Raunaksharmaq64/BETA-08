# Core Career Engine Integration Specification

- **Title:** Integration Specification for Career Engine
- **Purpose:** Specifies how the Core Career Engine incorporates legacy capabilities from `agentic-career-search`.
- **Status:** APPROVED
- **Owner:** Backend Lead (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Scope & Legacy Source
- **Legacy Source:** Prototype codebase located at `../agentic-career-search`.
- **Role in RIGHT FIT:** Functions as the foundational core of `backend/app/modules/`.

## 2. Capabilities Slated for Porting / Modular Reuse
1. **50+ ATS Adapters:** (Ashby, Greenhouse, Lever, Workday, BambooHR, ADP, Dice, BuiltIn, etc.). Reused inside `backend/app/integrations/job_sources/`.
2. **Deterministic Decision Engine:** `fit_score` calculation with explicit matched/missing skill rationale. Ported to `backend/app/modules/matching/`.
3. **Compensation & Benefits Estimator:** Base salary, equity vest schedules, signing bonus clawbacks, severance Cobra top-ups. Ported to `backend/app/modules/compensation/`.
4. **Application CRM State Machine:** Pipeline state transitions (`saved`, `applied`, `interview`, `offer`). Ported to `backend/app/modules/applications/`.
5. **Interview Prep Intelligence:** STAR story prompts, technical brief generation, schedule conflict detection. Ported to `backend/app/modules/interviews/`.

## 3. Human-in-the-Loop Directives
- **Zero Auto-Submission:** Ported adapters must be strictly restricted to data ingestion and job discovery. The system must never execute automated submission payloads on external applicant tracking systems without user confirmation.

## 4. Open Questions & TBDs
- [TBD] Mapping legacy Pydantic v1 models to Pydantic v2 in Phase 1.

