# Provenance, Freshness & Auditing

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

---

## 1. Raw Source Observations (`source_observations`)

To ensure auditable provenance and evidentiary integrity, every raw listing fetched from an external source is persisted in the `source_observations` table before canonical normalization.

### Observation Entity Schema
| Field | Type | Description |
|---|---|---|
| `id` | `VARCHAR(36)` | Unique observation UUID. |
| `source_id` | `VARCHAR(36)` | Foreign key referencing `job_sources.id`. |
| `external_job_id` | `VARCHAR(150)` | Native provider identifier. |
| `listing_url` | `VARCHAR(1000)` | Direct permalink or application link. |
| `observed_at` | `TIMESTAMP WITH TZ` | Ingestion timestamp when feed was retrieved. |
| `source_published_at` | `TIMESTAMP WITH TZ` | Original publication timestamp declared by employer. |
| `source_updated_at` | `TIMESTAMP WITH TZ` | Last updated timestamp from upstream provider. |
| `raw_payload_json` | `JSON` | Complete unmodified JSON payload from provider. |
| `payload_hash_sha256` | `VARCHAR(64)` | SHA-256 cryptographic hash of serialized raw payload. |
| `normalization_status` | `VARCHAR(30)` | `RAW`, `NORMALIZED`, `FAILED`, `DUPLICATE`. |
| `error_message` | `TEXT` | Parser error details if normalization failed. |
| `first_seen_at` | `TIMESTAMP WITH TZ` | First recorded observation timestamp. |
| `last_seen_at` | `TIMESTAMP WITH TZ` | Most recent observation timestamp. |

---

## 2. Ingestion Freshness & Idempotency Lifecycle

1. **Initial Ingestion:**
   - Provider returns listing with `external_id = "12345"`.
   - `SourceObservationRecord` is created (`first_seen_at = now()`, `last_seen_at = now()`).
   - `CanonicalOpportunityRecord` is inserted (`first_seen_at = now()`, `last_seen_at = now()`, `is_active = True`).
2. **Subsequent Ingestion (Still Active):**
   - The same listing is retrieved in a future run.
   - Observation record is updated with new `last_seen_at = now()` and updated `payload_hash_sha256`.
   - Canonical opportunity record is updated in-place (`last_seen_at = now()`, `is_active = True`).
   - Run log increments `records_updated` counter; `records_inserted` is 0.
3. **Cross-Source Duplicate:**
   - Another registered feed (e.g. Ashby) provides a listing with matching title, company, and location.
   - Normalizer computes matching `dedup_key_sha256`.
   - The pipeline recognizes the existing canonical record and increments `duplicates_skipped` counter, preventing duplicate listings from cluttering search results.

---

## 3. Auditing & Compliance Verification

Every `CanonicalOpportunityRecord` stores an embedded `provenance_json` attribute:

```json
{
  "source_id": "8a32d1f4-90a1-4328-bca7-81734918e11b",
  "source_key": "greenhouse-stripe",
  "provider": "greenhouse",
  "normalizer_version": "1.0.0",
  "normalized_at": "2026-10-31T02:15:30.123456+00:00",
  "original_listing_url": "https://boards.greenhouse.io/stripe/jobs/56789"
}
```

This guarantees end-to-end traceability from a candidate application link back to the exact API response that originated the job.
