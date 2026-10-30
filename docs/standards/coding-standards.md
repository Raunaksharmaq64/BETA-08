# Coding Standards & Code Quality

- **Title:** RIGHT FIT Code Quality & Style Standards
- **Purpose:** Establishes syntactic, architectural, and quality rules for Python and TypeScript/React codebases.
- **Status:** APPROVED
- **Owner:** Principal Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Python Standards (Backend & Services)
- **Language Level:** Python 3.11+.
- **Formatter & Linter:** Ruff (`line-length = 100`, rule sets: `E`, `F`, `I`, `B`, `UP`).
- **Type Annotations:** Mandatory complete type hints for all function arguments, return types, and class attributes.
- **Data Validation:** Pydantic v2 `BaseModel` with strict validation.
- **Async Hygiene:** Do not mix blocking I/O calls (e.g. `requests.get()`, `time.sleep()`) inside `async def` endpoints. Use `httpx.AsyncClient` and `asyncio.sleep()`.
- **Exception Handling:** Never use bare `except:`. Catch specific exceptions and re-raise custom domain exceptions (`app.core.exceptions`).

## 2. TypeScript & React Standards (Frontend)
- **Framework:** Next.js 16 (App Router), React 19.
- **Type Checking:** Strict mode enabled (`"strict": true` in `tsconfig.json`). Zero usage of `any`.
- **Component Design:** Prefer React Server Components (RSC) by default; use `'use client'` only when client-side hooks, state, or event listeners are required.
- **Styling:** Tailwind CSS utility classes paired with shadcn/ui design tokens. Avoid ad-hoc inline styles.
- **State Management:** URL search params for bookmarkable filter state; React Context for scoped UI state (e.g., toast alerts).

## 3. General Clean Code Rules
- **DRY with Discipline:** Avoid duplicated business logic across modules.
- **Explicit over Implicit:** Avoid magic numbers, strings, or undocumented side effects.
- **No Sensitive Logging:** Never log passwords, API tokens, Authorization headers, or PII.

## 4. Open Questions & TBDs
- [TBD] Setting maximum cyclomatic complexity threshold (target: <= 10).

