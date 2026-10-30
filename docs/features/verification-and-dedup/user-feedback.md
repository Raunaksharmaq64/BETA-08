# User Listing Feedback & Rate Limiting

## 1. Overview

Candidates often discover broken links or filled positions before scheduled verification probes occur. RIGHT FIT provides a rate-limited feedback pipeline allowing candidates to report inaccuracies.

---

## 2. Feedback Categories

Candidates can report an issue under one of 5 categories:

- `BROKEN_LINK`: 404, 502, or dead application URL.
- `ALREADY_CLOSED`: Employer has closed the opening on their external site.
- `INCORRECT_DETAILS`: Title, salary, location, or seniority is inaccurate.
- `DUPLICATE_LISTING`: Listing is an identical duplicate of another role on the platform.
- `OTHER`: General user feedback.

---

## 3. Rate Limiting Defense

To prevent spamming or denial-of-service against external job boards:

- Submissions are restricted by a sliding-window rate limiter (`FeedbackRateLimiter`) to **maximum 5 reports per minute per IP / user**.
- Submissions exceeding this threshold are rejected with HTTP 429 Too Many Requests.
- User IP addresses are hashed with SHA-256 for privacy protection.

---

## 4. Evidentiary Re-Verification Trigger

When a user reports `BROKEN_LINK` or `ALREADY_CLOSED`:
- The system automatically initiates an evidentiary probe via `VerificationService`.
- **Crucial Invariant**: User reports DO NOT immediately mark a job closed! The system only updates the listing status if the evidentiary probe confirms the closure or 404.

