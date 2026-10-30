# Deduplication Engine & Tiered Matching

## 1. Overview

Job vacancies are frequently republished across multiple job boards, aggregator feeds, and direct ATS URLs. Unchecked deduplication either causes duplicate clutter or erroneously collapses distinct roles into one.

RIGHT FIT implements a deterministic **4-Tier Deduplication Strategy** implemented in `backend/app/services/deduplication_service.py`.

---

## 2. Match Tiers

| Tier | Category | Matching Criteria | Confidence Score | Action |
|---|---|---|---|---|
| **Tier 1** | `TIER_1_EXACT` | Same SHA-256 deduplication key OR same normalized requisition ID from matching company. | `1.0` (100%) | Automated merge / Single Canonical Record |
| **Tier 2** | `TIER_2_STRONG` | Same company + identical normalized title + matching location/remote modality + published within 45 days. | `0.95 - 0.98` | High-confidence Candidate Pair / Automated Merge |
| **Tier 3** | `TIER_3_PROBABLE` | High text similarity on title (>80%) + same company + overlapping keywords, but slight phrasing or date difference. | `0.70 - 0.89` | Proposed Candidate for Human Administrative Review |
| **Tier 4** | `TIER_4_DISTINCT` | Distinct company, different seniority level (e.g. Senior vs Junior), or similarity < 70%. | `< 0.70` | Kept separate as distinct canonical listings |

---

## 3. Duplicate Detection Routine

Administrators can trigger automated candidate pair detection via `POST /api/v1/duplicates/detect?lookback_days=60`.

The routine scans all unsuppressed canonical opportunities, compares them pairwise across normalized attributes, and generates `DuplicateCandidateRecord` rows in `PROPOSED` status for review on the Duplicate Review Workbench.

