# RIGHT FIT — Candidate Preferences Specification
**Version:** 1.0.0  
**Phase:** 3 — Identity, Candidate Profile & Privacy Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Overview

Candidate preferences drive the multi-stream opportunity intelligence engine. These preferences dictate how opportunities from ATS integrations, LeadHunter local business web audits, and Startup Intelligence bottlenecks are scored and matched.

---

## 2. Preference Dimensions

| Attribute | Schema Type | Description |
| :--- | :--- | :--- |
| `preferred_roles` | `List[str]` | Target job titles (e.g. `["Staff Backend Engineer", "AI Architect"]`). |
| `preferred_skills` | `List[str]` | Technologies candidate wants to utilize (e.g. `["FastAPI", "Rust"]`). |
| `preferred_industries` | `List[str]` | Business domains (e.g. `["Fintech", "Healthtech", "DevTools"]`). |
| `preferred_locations` | `List[str]` | Target metropolitan areas or geographic boundaries. |
| `remote_preference` | `RemotePreference` | `REMOTE`, `HYBRID`, `ON_SITE`, or `ANY`. |
| `min_salary` / `max_salary` | `float` | Base compensation floor and target. |
| `currency` | `string(3)` | ISO 4217 currency code (e.g. `USD`, `EUR`, `INR`). |
| `employment_types` | `List[str]` | `["Full-time", "Contract", "Freelance"]`. |
| `job_notification_frequency` | `string` | `IMMEDIATE`, `DAILY`, `WEEKLY`, or `NEVER`. |

---

## 3. Storage and Cross-User Isolation

Preferences are persisted in `candidate_preferences` with a 1-to-1 foreign key to `candidate_profiles`.

> [!IMPORTANT]
> **Strict Ownership Derivation:** Preference queries derive candidate identity strictly from the validated JWT token (`current_user.id`). User A cannot view or manipulate User B's preferences.

---

## 4. API Reference

- `GET /api/v1/candidate/preferences`: Retrieves authenticated candidate preferences.
- `PUT /api/v1/candidate/preferences`: Updates and saves career matching criteria.
