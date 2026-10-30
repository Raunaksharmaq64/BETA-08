# Rate Limiting & Abuse Prevention Architecture

## 1. Overview & Threat Model

Authentication and public endpoints are primary targets for distributed denial-of-service (DDoS), credential stuffing, brute-force password cracking, and account enumeration attacks.

**RIGHT FIT** deploys a dual-key, sliding-window rate limiting architecture implemented in `app/services/rate_limiter.py` to mitigate abusive traffic while maintaining smooth access for legitimate candidates.

---

## 2. Sliding-Window Algorithm

Rather than crude fixed-window counters that permit burst spikes at window boundaries, RIGHT FIT utilizes a sliding timestamp log:

1. When a request arrives at key $K$, timestamps older than $t - \text{window\_seconds}$ are pruned.
2. The remaining timestamps are counted.
3. If $\text{count} \ge \text{limit}$, the request is rejected with HTTP `429 Too Many Requests`.
4. Otherwise, the current timestamp $t$ is recorded, and the request proceeds.

$$\text{Window Enforcement: } \sum_{i} [t_i \in (t - W, t)] \le L$$

---

## 3. Multi-Key Rate Limiting Strategy

Endpoints apply rate limiting across two orthogonal dimensions:

1. **IP-Level Limiting**:
   - Key: `ip:<client_ip>:<route>`
   - Protects the infrastructure against single-origin brute force, scrapers, and port scanners.
2. **Account-Level Limiting**:
   - Key: `account:<normalized_email>:<route>`
   - Protects individual user accounts against distributed botnets that rotate egress IP addresses while attacking a single victim's email address.

---

## 4. Default Limits & Configuration

Configurable via environment variables and centralized in `app/core/config.py`:

| Target Route / Action | Key Strategy | Window | Max Requests | Purpose |
|---|---|---|---|---|
| `POST /api/v1/auth/login` | IP + Account | 60 seconds | 10 | Prevents brute-force authentication. |
| `POST /api/v1/auth/register` | IP | 60 seconds | 5 | Prevents automated bot registrations. |
| `POST /api/v1/auth/forgot-password` | IP + Account | 60 seconds | 5 | Prevents email inbox bombing. |
| `POST /api/v1/auth/refresh` | IP | 60 seconds | 30 | Prevents token hammering. |
| `POST /api/v1/privacy/export` | Account | 3600 seconds | 5 | Prevents database exhaustion from repeated large exports. |
| General Protected APIs | IP + User | 60 seconds | 120 | Baseline API flood protection. |

---

## 5. HTTP 429 Response Specification

When rate limits are exceeded, Core returns a standard response:

### Headers:
- `Retry-After`: Number of seconds until the sliding window admits the next request.
- `X-RateLimit-Limit`: Maximum requests permitted per window.
- `X-RateLimit-Remaining`: `0`
- `X-RateLimit-Reset`: UTC epoch timestamp when current window fully expires.

### Body (RFC 7807 Envelope):
```json
{
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again in 48 seconds.",
  "correlation_id": "b47c0a91-497d-411f-827c-3fef2a8b9e11",
  "timestamp": "2026-10-31T01:30:00Z"
}
```

---

## 6. Dual-Storage Backend (Local & Distributed)

1. **Local / Testing Mode**:
   - In-memory `collections.deque` dictionary with automated garbage collection. Zero external dependencies required during local unit tests.
2. **Production Mode (Redis)**:
   - Evaluates a Redis sorted set (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`, `EXPIRE`) atomically via Lua script, ensuring synchronized rate limit counts across horizontally scaled Core Career Engine replicas.

