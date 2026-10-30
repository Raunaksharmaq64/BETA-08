# Service Communication Standards

- **Title:** Inter-Service & External Communication Protocols
- **Purpose:** Governs protocol standards, serialization, retry strategies, and circuit breaking for service-to-service communication.
- **Status:** APPROVED
- **Owner:** Principal Architect / Backend Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Transport & Protocol Standards
- **Protocol:** HTTP/1.1 (Internal Service Mesh) / HTTPS (Public Ingress).
- **Format:** Strict JSON serialized via Pydantic schemas.
- **Headers Required:**
  - `X-Request-ID`: Distributed correlation UUID propagated across all downstream calls.
  - `X-Service-Source`: Originating service identifier (`rightfit-core`, `rightfit-frontend`).
  - `Authorization`: Bearer token for client requests or pre-shared internal HMAC token for service-to-service calls.

## 2. Resilience, Timeouts & Retries
- **Internal Service Timeouts:**
  - Standard REST calls: 5.0 seconds maximum.
  - Bulk scan creation / long-running job dispatch: 3.0 seconds (returns job ticket ID immediately).
- **Retry Strategy:**
  - Max 3 retries with exponential backoff and full jitter:
    $$\text{Backoff} = 2^{\text{attempt}} \times 0.5\text{s} + \text{random\_jitter}$$
  - Retries permitted ONLY on idempotent requests (GET, PUT) and transient 502/503/504 errors. Never retry on 4xx client errors.

## 3. Circuit Breaker Policy
- If outbound requests to a satellite service experience > 50% failure rate over a 1-minute window, trip circuit breaker for 30 seconds.
- Provide graceful degradation: Core returns active cache or returns an empty list with an alert banner rather than crashing.

## 4. Open Questions & TBDs
- [TBD] Evaluation of gRPC for future high-volume internal services in Phase 4.

