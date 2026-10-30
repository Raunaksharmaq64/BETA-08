# Field Provenance & Profile Confidence Standards

## 1. Overview & Purpose

In the **RIGHT FIT — Career Intelligence Platform**, candidate profile data originates from multiple distinct sources:
1. Candidate direct entry (forms, modals, onboarding).
2. Automated resume parsing and text extraction engines.
3. Machine learning recommendations and generative agent suggestions.
4. Third-party integrations (LinkedIn, GitHub).
5. Formal verification checkpoints.

Because automated extraction and AI models can introduce hallucinations, formatting artifacts, or inaccurate inferences, **RIGHT FIT** enforces strict field-level provenance tracking. Every profile entity and collection item tracks its origin and confidence score.

---

## 2. Provenance Taxonomy (`FieldProvenance`)

The Core Career Engine standardizes provenance under the `FieldProvenance` enumeration in `contracts/profile/schemas.py`:

| Provenance Level | Description | Trust Tier | Overwrite Authority |
|---|---|---|---|
| `USER_PROVIDED` | Explicitly entered or revised by the candidate via UI or verified API call. | High | Cannot be overridden by automated pipelines without candidate consent. |
| `RESUME_EXTRACTED` | Extracted from structured or unstructured candidate resume documents. | Medium | Can populate empty fields; cannot overwrite `USER_PROVIDED` or `VERIFIED`. |
| `AI_SUGGESTED` | Inferred, synthesized, or suggested by agentic analysis or skill extractors. | Low–Medium | Stored as candidate suggestions; requires user acceptance to promote. |
| `IMPORTED` | Ingested via external third-party OAuth integrations (e.g., GitHub, portfolio). | Medium | Treated according to provider confidence. |
| `VERIFIED` | Validated through assessment, credential check, or explicit user verification. | Highest | Immutable except by explicit re-verification or candidate override. |

---

## 3. Data Model Integration

Every profile item tracks:
- `provenance`: `FieldProvenance` enum string (e.g. `"USER_PROVIDED"`).
- `confidence_score`: Float between `0.0` and `1.0` indicating source confidence.

### Supported Entities
1. **Core Candidate Profile (`CandidateProfile`)**:
   - `headline`, `summary`, `years_of_experience`, `current_title` track default profile provenance and aggregate confidence.
2. **Education Records (`EducationRecord`)**:
   - Each academic degree or credential retains independent provenance (e.g., `RESUME_EXTRACTED` vs `USER_PROVIDED`).
3. **Experience Records (`ExperienceRecord`)**:
   - Work histories maintain provenance and confidence metrics.
4. **Candidate Skills (`CandidateSkillRecord`)**:
   - Skills distinguish user-claimed proficiencies (`USER_PROVIDED`) from inferred capabilities (`AI_SUGGESTED`) or assessed proficiencies (`VERIFIED`).

---

## 4. Conflict Resolution & Overwrite Rules

When background processes (such as resume ingestion or career intelligence analyzers) process candidate data:

1. **Hierarchy of Truth**:
   $$\text{VERIFIED} \ge \text{USER\_PROVIDED} > \text{IMPORTED} \ge \text{RESUME\_EXTRACTED} > \text{AI\_SUGGESTED}$$
2. **Non-Destructive Augmentation**:
   - Automated workers may **fill blank/null fields**.
   - Automated workers **must never silently overwrite** existing values marked `USER_PROVIDED` or `VERIFIED`.
   - If an AI inference discovers conflicting information (e.g., an updated job title or missing skills), it must present a pending diff or proposal to the candidate rather than mutating the active record.
3. **Candidate Promotion**:
   - When a candidate edits or accepts an `AI_SUGGESTED` or `RESUME_EXTRACTED` item via the dashboard, its provenance transitions to `USER_PROVIDED` and its `confidence_score` is elevated to `1.0`.

---

## 5. Auditability and Transparency

All provenance modifications are persisted in PostgreSQL with audit timestamps. In the unified Next.js dashboard, candidate profile fields display transparent origin badges (e.g. "Self-reported", "Extracted from Resume", "AI Suggested") so candidates always understand why their profile looks the way it does and retain absolute agency over their data.
