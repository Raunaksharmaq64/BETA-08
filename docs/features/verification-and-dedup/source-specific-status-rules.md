# Source-Specific Status Interpretation Rules

## 1. Overview

Different applicant tracking systems (ATS) signal requisition states in distinct ways. Naively checking HTTP status codes across heterogeneous systems leads to severe false positives. RIGHT FIT implements provider-aware interpretation logic for Greenhouse, Ashby, and synthetic boards.

---

## 2. Provider Evaluation Logic

### 2.1 Greenhouse (`GREENHOUSE`)

- **API Endpoint**: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}`
- **Evaluation Rules**:
  - `HTTP 200 OK`: Vacancy is actively open and accepting applications (`OPEN_CONFIRMED`).
  - `HTTP 404 Not Found`: Requisition has been unpublished, closed, or fulfilled by the employer (`CLOSED_CONFIRMED`).
  - `HTTP 429 Too Many Requests`: Rate limit reached; classify as `CHECK_FAILED`, schedule backoff. Do NOT close the vacancy.
  - `HTTP 5xx (500/502/503/504)`: Upstream outage; classify as `CHECK_FAILED`. Retain previously confirmed open status.

### 2.2 Ashby (`ASHBY`)

- **API Endpoint**: `https://api.ashbyhq.com/posting-api/job-board/{board_token}`
- **Evaluation Rules**:
  - `HTTP 200 OK` + `job_id in response.jobs`: Confirmed active (`OPEN_CONFIRMED`).
  - `HTTP 200 OK` + `job_id not in response.jobs`: Requisition removed from active feed (`CLOSED_CONFIRMED`).
  - `HTTP 5xx` or Network Timeout: Classify as `CHECK_FAILED`. Retain prior open status.

### 2.3 Synthetic Job Sources (`SYNTHETIC`)

- **Evaluation Rules**:
  - Deterministic status simulation for local offline testing, resilience validation, and contract tests.
  - URL containing `outage` or `503`: Simulates transient provider downtime (`CHECK_FAILED`).
  - URL containing `404` or `closed`: Simulates unpublishing (`CLOSED_CONFIRMED`).
  - Standard URLs: Return `OPEN_CONFIRMED`.

---

## 3. Ambiguity & False Positive Prevention

When an external link redirects to a generic careers homepage (e.g. `https://company.com/careers` instead of the specific job posting):
- Classified as `AMBIGUOUS`.
- Flags the listing for secondary verification or administrative review.
- Prevents candidates from being misled by a dead job link while preventing premature listing closure.

