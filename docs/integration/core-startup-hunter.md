# RIGHT FIT — Core-to-Startup Hunter Integration Contract
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Domain Overview

**Startup Intelligence** operates as an independent satellite microservice responsible for:
1. Scanning developer and startup discussion communities (Reddit `r/saas`, `r/webdev`, Hacker News, GitHub Issues, Product Hunt).
2. Identifying urgent technical pain points expressed by startup founders (database exhaustion, high AWS bills, frontend bundle latency, slow queries).
3. Extracting technical context, tech stacks, and urgency scores (1-10).
4. Generating tailored technical solution pitches for independent engineers and agencies.

The **Core Career Engine** interacts with Startup Intelligence via versioned REST APIs, translating detected pain points into canonical `OpportunityEnvelope` instances of type `OpportunityType.STARTUP_PROBLEM`.

---

## 2. API Endpoints

### 2.1 Trigger Discovery Scan
- **Method & Route:** `POST /api/v1/startups/discovery`
- **Request Model:** `StartupDiscoveryRequest`
- **Response Model:** `StartupDiscoveryStatus` (HTTP 202 Accepted)

#### Request Payload
```json
{
  "sources": ["reddit", "hackernews"],
  "keywords": ["Postgres", "slow", "Next.js"],
  "categories": ["Database", "Performance"],
  "max_signals": 25
}
```

#### Response Payload
```json
{
  "discovery_id": "disc_si_0f31c2a8",
  "status": "QUEUED",
  "progress_percentage": 0,
  "total_signals_analyzed": 0,
  "total_opportunities_found": 0,
  "created_at": "2026-10-31T00:46:00Z"
}
```

### 2.2 Retrieve Discovery Results
- **Method & Route:** `GET /api/v1/startups/discovery/{discovery_id}`
- **Response Model:** `StartupDiscoveryResult` (HTTP 200 OK)

#### Response Payload
```json
{
  "discovery_id": "disc_si_0f31c2a8",
  "problems": [
    {
      "signal_id": "sig_si_001",
      "startup_name": "CloudMetric SaaS",
      "category": "Database",
      "pain_point": "PostgreSQL connection pool exhaustions causing 504 timeouts during daily sync spikes.",
      "detected_signal": "Founder asking for help optimizing asyncpg pool on Reddit r/saas",
      "community_source": "Reddit r/saas",
      "source_url": "https://reddit.com/r/saas/comments/mock_post_1",
      "tech_stack": ["FastAPI", "PostgreSQL", "SQLAlchemy"],
      "urgency_score": 8,
      "suggested_pitch": "Hi team, I noticed your post regarding PostgreSQL pool exhaustion."
    }
  ],
  "total_count": 1
}
```

---

## 3. Canonical Opportunity Envelope Transformation

Core transforms each `StartupProblemSummary` into an `OpportunityEnvelope`:

```python
OpportunityEnvelope(
    schema_version="1.0",
    opportunity_id=f"opp_startup_{prob.signal_id}",
    opportunity_type=OpportunityType.STARTUP_PROBLEM,
    title=f"Fix {prob.category} Bottleneck: {prob.startup_name}",
    description=prob.pain_point,
    organization=OrganizationInfo(name=prob.startup_name),
    location=LocationInfo(country="Global", remote_type=RemoteType.REMOTE),
    source=SourceProvenance(provider="startup_intelligence", original_url=prob.source_url, external_id=prob.signal_id),
    status=StatusInfo(value=VerificationStatus.VERIFIED),
    evidence=[
        EvidenceItem(
            source_url=prob.source_url,
            excerpt=prob.detected_signal
        )
    ],
    payload=StartupProblemPayload(
        target_startup=prob.startup_name,
        pain_point_summary=prob.pain_point,
        problem_category=prob.category,
        community_source=prob.community_source,
        author="Founder",
        tech_stack_detected=prob.tech_stack,
        urgency_score=prob.urgency_score,
        recommended_solution=prob.suggested_pitch,
    )
)
```

---

## 4. Failure Modes & Circuit Breaking

1. **Timeout Policy:** Core calls to Startup Intelligence enforce a hard timeout of **5.0 seconds**.
2. **Circuit Breaking:** 3 consecutive failures trip the circuit breaker for 60 seconds.
3. **Graceful Fallback:** When tripped, startup pain-point discovery yields an empty list with `retryable: true` without failing Core user sessions.

