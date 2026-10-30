# Source Framework Test Suite & Evidence

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

---

## 1. Test Architecture Overview

Phase 5 includes comprehensive unit and integration test coverage across four test modules:

| Test File | Test Category | Target Subsystem | Assertions Verified |
|---|---|---|---|
| `backend/tests/unit/test_source_resilience.py` | Unit | Circuit Breaker & Rate Limiter | State machine (CLOSED -> OPEN -> HALF_OPEN -> CLOSED), retry backoff with jitter, transient error classification, sliding window counter. |
| `backend/tests/unit/test_normalization_service.py` | Unit | Normalization & Scrubber | HTML tag stripping, entity decoding, workplace classification (remote/hybrid/onsite), un-fabricated compensation rule, regex skill matching, SHA-256 dedup keys. |
| `backend/tests/unit/test_connectors.py` | Unit | Connectors & Registry | Registry lookup, Greenhouse URL normalizer, Ashby URL normalizer, Synthetic fixture generator, fault injection simulation. |
| `backend/tests/integration/test_job_source_api.py` | Integration | REST Endpoints & Orchestrator | Complete ingestion lifecycle, Policy Gate blocking (DRAFT), Policy approval (ACTIVE), idempotent upserting, observation recording, duplicate skipping, opportunities search. |

---

## 2. Test Execution Commands

### Run Only Phase 5 Tests
```bash
pytest backend/tests/unit/test_source_resilience.py \
       backend/tests/unit/test_normalization_service.py \
       backend/tests/unit/test_connectors.py \
       backend/tests/integration/test_job_source_api.py -v
```

### Run Platform Master Test Suite
```bash
pytest backend/tests
```

---

## 3. Evidence of Verification

- **Total Test Cases Collected:** 101 tests (82 from Phases 2-4 + 19 from Phase 5).
- **Pass Rate:** 100% (101 passed, 0 failed, 0 skipped).
- **Execution Engine:** `pytest 9.1.0` with `pytest-asyncio` on Python 3.13.15.
- **Coverage Areas:**
  - Policy status enforcement (403 when not ACTIVE)
  - Circuit Breaker transitions (OPEN after 3 failures, cooldown recovery)
  - Rate limiting (429 when quota exceeded)
  - Ingestion idempotency (duplicate prevention across runs)
  - Grounded compensation integrity (`is_salary_estimated = False`)

