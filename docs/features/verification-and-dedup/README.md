# RIGHT FIT — Verification, Deduplication, Freshness & Data Quality Intelligence

## 1. Executive Summary

Phase 6 introduces a production-grade verification, deduplication, freshness tracking, and data quality intelligence architecture to the **RIGHT FIT Core Career Engine**.

Online job boards and ATS scrapers are notoriously plagued by expired ghost jobs, broken external links, spam reposts, and fabricated information. RIGHT FIT addresses these foundational issues by treating job verification as an evidentiary discipline:

1. **Independent Lifecycle Timestamps**: Decoupling the original job posting date, platform observation timestamps, check attempts, and verification confirmations.
2. **Evidentiary Verification State Machine**: Requiring concrete proof from direct APIs, HTTP response metadata, or safe URL probes before asserting that a job is open or closed.
3. **Bounded URL Checker with Strict SSRF Defense**: Blocking loopback, private RFC 1918 networks, and cloud instance metadata before making external HTTP requests.
4. **Source-Specific Status Rules**: Custom interpretation logic for Greenhouse, Ashby, and synthetic feeds, with retry-aware handling to prevent transient provider outages from falsely closing active opportunities.
5. **Tiered Deduplication & Reversible Merge/Unmerge**: High-precision matching across 4 tiers (Exact, Strong Multi-Attribute, Probable Similarity, Distinct), preserving distinct source mappings and enabling auditable, reversible unmerge operations.
6. **Freshness Policies & Candidate Feedback**: Clear, unambiguous candidate-facing status badges backed by rate-limited user reporting that triggers evidentiary re-checks.
7. **Operational Data Quality Dashboard**: Live visibility into freshness rates, verification coverage, confirmed open rates, and per-source circuit breaker health.

---

## 2. Architecture Overview

```
                      +-----------------------------+
                      |   Direct ATS API / HTTP     |
                      |  (Greenhouse, Ashby, Feeds) |
                      +--------------+--------------+
                                     |
                         [Safe URL / SSRF Filter]
                                     |
                                     v
                       +---------------------------+
                       |    VerificationService    |
                       +-------------+-------------+
                                     |
         +---------------------------+---------------------------+
         |                                                       |
         v                                                       v
+-------------------------------+                     +-------------------------------+
|   VerificationEvidenceRecord  |                     |  CanonicalOpportunityRecord   |
|   (Immutable Evidence Log)    |                     |  - independent timestamps     |
+-------------------------------+                     |  - verification_status        |
                                                      |  - freshness_state            |
                                                      |  - is_suppressed              |
                                                      +---------------+---------------+
                                                                      |
                                                                      v
                                                      +-------------------------------+
                                                      |     DeduplicationService      |
                                                      |  - Tier 1: Exact Hash/Req ID  |
                                                      |  - Tier 2: Strong Multi-Attr  |
                                                      |  - Tier 3: Probable Similarity|
                                                      |  - Tier 4: Distinct           |
                                                      +---------------+---------------+
                                                                      |
                                       +------------------------------+------------------------------+
                                       |                                                             |
                                       v                                                             v
                        +------------------------------+                              +------------------------------+
                        |  DuplicateCandidateRecord    |                              |  OpportunitySourceMapping    |
                        |  (Review Workbench)          |                              |  (Auditable Source Links)    |
                        +------------------------------+                              +------------------------------+
```

---

## 3. Documentation Index

- [Verification State Machine](./verification-state-machine.md)
- [Verification Evidence](./verification-evidence.md)
- [Source-Specific Status Rules](./source-specific-status-rules.md)
- [Freshness Policy](./freshness-policy.md)
- [Deduplication Engine](./deduplication-engine.md)
- [Source Mapping](./source-mapping.md)
- [Merge & Unmerge Audit](./merge-unmerge-audit.md)
- [User Feedback](./user-feedback.md)
- [Data Quality Metrics](./quality-metrics.md)
- [Frontend Guide](./frontend-guide.md)

