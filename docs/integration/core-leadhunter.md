# RIGHT FIT — Core-to-LeadHunter Integration Contract
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Domain Overview

**LeadHunter AI** operates as an independent satellite microservice responsible for:
1. Discovering local businesses (dentists, plumbers, accountants, etc.) via map searches.
2. Crawling and diagnosing business website health (broken domains, expired SSL, slow response times, missing mobile tags).
3. Discovering owner contact information (email, phone, socials).
4. Generating automated technical freelance outreach pitches.

The **Core Career Engine** interacts with LeadHunter strictly via versioned REST APIs, translating discovered leads into canonical `OpportunityEnvelope` instances of type `OpportunityType.FREELANCE`.

---

## 2. API Endpoints

### 2.1 Trigger Discovery Scan
- **Method & Route:** `POST /api/v1/leads/discovery`
- **Request Model:** `LeadDiscoveryRequest`
- **Response Model:** `LeadDiscoveryStatus` (HTTP 202 Accepted)

#### Request Payload
```json
{
  "query": "Dentists",
  "city": "Austin, TX",
  "max_results": 20,
  "include_with_website": true,
  "deep_scan": true
}
```

#### Response Payload
```json
{
  "discovery_id": "disc_lh_9a87f1b2",
  "status": "QUEUED",
  "progress_percentage": 0,
  "total_found": 0,
  "created_at": "2026-10-31T00:45:00Z"
}
```

### 2.2 Retrieve Discovery Scan Results
- **Method & Route:** `GET /api/v1/leads/discovery/{discovery_id}`
- **Response Model:** `LeadDiscoveryResult` (HTTP 200 OK)

#### Response Payload
```json
{
  "discovery_id": "disc_lh_9a87f1b2",
  "leads": [
    {
      "lead_id": "lead_lh_001",
      "business_name": "Downtown Dental Clinic",
      "category": "Dental Clinic",
      "city": "Austin, TX",
      "website": "http://downtowndental-fake-broken.com",
      "is_broken_website": true,
      "phone": "+1-512-555-0199",
      "email": "contact@downtowndental-fake.com",
      "rating": 4.6,
      "reviews_count": 84,
      "suggested_pitch": "Your website is currently throwing a 502 Bad Gateway error."
    }
  ],
  "total_leads": 1
}
```

---

## 3. Canonical Opportunity Envelope Transformation

Core transforms each `LeadSummary` into an `OpportunityEnvelope`:

```python
OpportunityEnvelope(
    schema_version="1.0",
    opportunity_id=f"opp_lead_{lead.lead_id}",
    opportunity_type=OpportunityType.FREELANCE,
    title=f"{lead.category} Web Modernization — {lead.business_name}",
    description=lead.suggested_pitch,
    organization=OrganizationInfo(name=lead.business_name, website=lead.website),
    location=LocationInfo(city=lead.city, country="USA", remote_type=RemoteType.REMOTE),
    source=SourceProvenance(provider="leadhunter", original_url=lead.website, external_id=lead.lead_id),
    status=StatusInfo(value=VerificationStatus.VERIFIED),
    evidence=[
        EvidenceItem(
            source_url=lead.website,
            excerpt=f"Google Rating: {lead.rating} ({lead.reviews_count} reviews)."
        )
    ],
    payload=FreelanceOpportunityPayload(
        business_category=lead.category,
        website_url=lead.website,
        is_broken_website=lead.is_broken_website,
        audit_status="COMPLETED",
        detected_issues=["SSL Expired", "502 Gateway Error"],
        suggested_pitch=lead.suggested_pitch,
        contact_email=lead.email,
        contact_phone=lead.phone,
    )
)
```

---

## 4. Failure Modes & Circuit Breaking

1. **Timeout Policy:** Core calls to LeadHunter enforce a hard timeout of **5.0 seconds**.
2. **Circuit Breaking:** 3 consecutive HTTP 503 or timeout failures trip the circuit breaker for 60 seconds.
3. **Graceful Fallback:** When tripped, freelance discovery indicates "Satellite Offline (Cached results only)" without disrupting Core ATS job matching.

