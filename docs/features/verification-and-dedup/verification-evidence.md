# Verification Evidence

## 1. Overview

RIGHT FIT establishes accountability by persisting every verification event into an immutable evidentiary ledger (`verification_evidence`). No opportunity's status can be altered without a corresponding `VerificationEvidenceRecord`.

---

## 2. Schema Specification

The `VerificationEvidenceRecord` captures:

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier of the evidence event |
| `opportunity_id` | UUID | Foreign key referencing `canonical_opportunities.id` |
| `source_id` | UUID | Foreign key referencing `job_sources.id` |
| `check_id` | UUID | Identifier for the verification execution batch or task |
| `check_timestamp` | DATETIME (UTC) | Exact moment verification probe occurred |
| `check_method` | VARCHAR(50) | `DIRECT_API`, `URL_PROBE`, or `BOARD_FEED` |
| `check_outcome` | VARCHAR(30) | `OPEN`, `CLOSED`, `NOT_FOUND`, `REDIRECT_LOOP`, `ERROR` |
| `http_status` | INTEGER | HTTP response status code (e.g. 200, 404, 503) |
| `provider_status` | VARCHAR(50) | Upstream provider status string |
| `evidence_category` | VARCHAR(50) | `PROVIDER_API_RESPONSE`, `PAGE_PROBE`, `DNS_FAILURE` |
| `evidence_reference` | VARCHAR(500) | Final target URL or API endpoint inspected |
| `safe_response_metadata_json` | JSON | Non-sensitive diagnostic headers and timings |
| `verification_rule_version` | VARCHAR(20) | Semantic version of rule evaluator (e.g. "1.0.0") |
| `confidence_category` | VARCHAR(30) | `HIGH`, `MEDIUM`, `LOW` |
| `error_category` | VARCHAR(50) | Safe error classification (e.g. `UPSTREAM_TIMEOUT`) |
| `next_eligible_check_at` | DATETIME (UTC) | Cooldown expiration before re-checking |

---

## 3. Immutability Invariant

Evidence records are **append-only**. They can never be updated or deleted during ordinary operation. Even during unmerge or re-verification operations, historical evidence remains intact to ensure complete regulatory compliance and dispute resolution.

