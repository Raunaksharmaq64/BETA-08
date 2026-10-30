# Configuration Directory

- **Purpose:** Central repository for shared static configurations, linter definitions, and environment profiles.
- **Status:** ACTIVE
- **Owner:** DevOps Engineer (UNASSIGNED)
- **Last Updated:** 2026-10-31

---

## Scope & Guidelines
1. **No Secrets:** This directory must never contain production credentials, JWT private keys, or API tokens.
2. **Environment Templates:** Static environment variables and schema templates should be defined here or referenced via `.env.example`.
3. **Tooling Configurations:** Linter, formatter, and build configurations (e.g. `pyrightconfig.json`, `tailwind.config.ts`) may reside here or at service roots.

