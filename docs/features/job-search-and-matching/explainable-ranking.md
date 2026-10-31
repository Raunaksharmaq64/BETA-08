# Explainable Multi-Dimensional Ranking

## 1. Transparency Principle

RIGHT FIT forbids opaque composite black-box algorithms, hidden sponsored job placements, and pay-to-win candidate rankings. Every recommendation and sorting weight is auditable and visible to the candidate.

---

## 2. Ranking Score Formulation

The composite ranking score $[0.0 - 100.0]$ combines distinct evaluation dimensions:

| Dimension | Maximum Weight | Criteria & Score Breakdown |
| :--- | :--- | :--- |
| **Skill Fit** | 40% | Derived directly from `fit_score` $[0 - 100] \times 0.40$. |
| **Mandatory Eligibility** | 25% | `MEETS_REQUIREMENTS` = 25 pts<br>`UNKNOWN` = 15 pts<br>`NEEDS_REVIEW` = 10 pts<br>`DOES_NOT_MEET_REQUIREMENTS` = 0 pts |
| **Trust & Verification** | 15% | `OPEN_CONFIRMED` / `VERIFIED` = 15 pts<br>`UNVERIFIED` = 8 pts<br>`CLOSED` / `EXPIRED` = 0 pts |
| **Freshness State** | 10% | `FRESH` (< 24h) = 10 pts<br>`RECENT` (< 7d) = 7 pts<br>`STALE` = 2 pts<br>`UNKNOWN` = 0 pts |
| **Preference Alignment** | 10% | Alignment with remote work and target compensation. |

---

## 3. Candidate Sorting Options

Candidates maintain full autonomy to override the default ranking:
1. **Best Fit (`BEST_FIT`)**: Sorts by the multi-dimensional composite ranking score, prioritizing confirmed open jobs with highest skill match and satisfied eligibility.
2. **Most Recent (`MOST_RECENT`)**: Pure chronological sorting based on `first_seen_at` or `source_published_at`.
3. **Highest Compensation (`HIGHEST_SALARY`)**: Sorts by maximum or minimum compensation in descending order.
4. **Skill Match % (`SKILL_MATCH`)**: Sorts purely by technical skill overlap percentage without eligibility penalties.

