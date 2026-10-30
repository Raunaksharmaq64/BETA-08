# Privacy Settings Architecture & Enforcement

## 1. Overview

In **RIGHT FIT**, privacy is not an afterthought; it is implemented as a first-class citizen embedded directly into domain data models, API authorization filters, and agent orchestration.

Every candidate user in the platform possesses a dedicated `PrivacySettingsRecord` linked 1-to-1 with their account. The candidate retains fine-grained control over how their personal data, profile attributes, and job-search intent are processed and shared.

---

## 2. Privacy Settings Dimensions

The `PrivacySettingsRecord` and contract `PrivacySettingsResponse` govern the following explicit switches:

| Dimension / Field | Type | Default | Description |
|---|---|---|---|
| `profile_visibility` | String (`"PUBLIC"`, `"SEMI_PRIVATE"`, `"PRIVATE"`) | `"SEMI_PRIVATE"` | Determines whether satellite search agents, recruiters, or public endpoints can view profile details. In `PRIVATE`, the candidate is hidden from discovery queries. |
| `allow_ai_profile_analysis` | Boolean | `True` | Authorizes the Core Career Engine to run NLP and embedding pipelines against resume text and experience history to generate role matches. |
| `allow_opportunity_matching` | Boolean | `True` | Controls whether LeadHunter AI or startup matchmaking agents can propose outbound leads and opportunities to the candidate. |
| `allow_third_party_sharing` | Boolean | `False` | Opt-in flag required before profile summaries or contact details can be syndicated to external ATS systems or partner job boards. |
| `allow_research_analytics` | Boolean | `False` | Authorizes aggregated, anonymized profile data to be used in macroeconomic hiring trend analysis. |

---

## 3. Storage and Data Model

Privacy settings are persisted in PostgreSQL table `privacy_settings`:

```sql
CREATE TABLE privacy_settings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    profile_visibility VARCHAR(32) NOT NULL DEFAULT 'SEMI_PRIVATE',
    allow_ai_profile_analysis BOOLEAN NOT NULL DEFAULT TRUE,
    allow_opportunity_matching BOOLEAN NOT NULL DEFAULT TRUE,
    allow_third_party_sharing BOOLEAN NOT NULL DEFAULT FALSE,
    allow_research_analytics BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Auto-Initialization
When a user completes registration via `auth_service.register_user`, a default `PrivacySettingsRecord` is atomically committed along with the initial `CandidateProfileRecord`. At no point can a user exist without privacy settings.

---

## 4. API Endpoints

Privacy settings are managed via REST endpoints exposed under `/api/v1/privacy/settings`:

1. **`GET /api/v1/privacy/settings`**:
   - Headers: `Authorization: Bearer <access_token>`
   - Response: `200 OK` with `PrivacySettingsResponse` payload.
2. **`PUT /api/v1/privacy/settings`**:
   - Headers: `Authorization: Bearer <access_token>`
   - Body: `PrivacySettingsUpdate` with updated toggle values.
   - Behavior:
     - Updates record timestamps.
     - Logs `PRIVACY_SETTINGS_UPDATED` security audit event with sanitized delta.
     - Returns updated `PrivacySettingsResponse`.

---

## 5. Downstream Enforcement

1. **Satellite Isolation**:
   - Satellite services (`LeadHunter AI`, `Startup Problems Hunter`) NEVER query the candidate privacy table directly.
   - When satellite agents request candidate opportunities via Core API contracts, Core filters out candidates where `allow_opportunity_matching == False` or `profile_visibility == 'PRIVATE'`.
2. **AI Execution Boundaries**:
   - Background tasks evaluating skill gaps or generating personalized pitches check `allow_ai_profile_analysis`. If disabled, automated processing halts and returns standard generic templates.
