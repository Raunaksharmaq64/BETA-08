# API Versioning Policy

- **Title:** API Lifecycle & Versioning Policy
- **Purpose:** Governs version deprecation, URL path routing, and backward-compatibility rules.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Versioning Strategy
- **URI Path Versioning:** All endpoints are explicitly prefixed with `/api/v{major}/` (e.g., `/api/v1/jobs`).
- **Minor / Patch Changes:** Non-breaking changes (adding optional fields, adding new endpoints) do not change the version path.
- **Major Breaking Changes:** Removing fields, renaming resources, or altering authentication workflows require a new major version route (`/api/v2/`).

## 2. Deprecation Schedule
- When an API version is deprecated, it is supported for a minimum of 90 days.
- Deprecated responses include standard headers:
  - `Deprecation: true`
  - `Sunset: Wed, 11 Nov 2026 00:00:00 GMT`
  - `Link: <https://api.rightfit.com/docs/v2>; rel="successor-version"`

## 3. Open Questions & TBDs
- [TBD] Semantic version header fallback support.

