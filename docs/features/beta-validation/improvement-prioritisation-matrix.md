# Beta Improvement Prioritisation Matrix (RICE Methodology)

**Document ID:** RF-SPEC-1410  
**Phase:** 14 — Beta Testing & Product Validation  
**Status:** Approved  

---

## 1. Prioritization Methodology

To avoid haphazard feature sprawl and focus engineering bandwidth on high-leverage improvements, all candidate feedback items, architectural observations, and enhancement requests collected during Phase 14 are evaluated using the standard **RICE Framework**:

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

### Scoring Parameters:
- **Reach (1–10):** Number of beta candidates impacted over a 30-day period.
- **Impact (0.25 to 3.0):** Measurable improvement in conversion, retention, or reliability:
  - `3.0` = Massive impact (prevents abandonment).
  - `2.0` = High impact.
  - `1.0` = Medium impact.
  - `0.5` = Low impact.
  - `0.25` = Minimal impact.
- **Confidence (50% to 100%):** Confidence in estimates based on telemetry evidence.
- **Effort (Person-Days):** Estimated engineering effort required to design, implement, test, and ship.

---

## 2. Beta Evaluation Backlog & RICE Rankings

```mermaid
quadrantChart
    title Action Priority Matrix (Post-Beta Roadmap)
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Strategic Bets (Plan Carefully)
    quadrant-2 Quick Wins (Ship Immediately)
    quadrant-3 Reconsider (Low Priority)
    quadrant-4 Time Sinks (De-prioritize)
    "Automated Link Re-verification": [0.25, 0.85]
    "Enhanced Taxonomy Synonyms": [0.20, 0.75]
    "Compensation Range Normalizer": [0.40, 0.80]
    "Direct Calendar Integration": [0.80, 0.65]
    "Custom Email Ingestion": [0.75, 0.40]
```

| Item Title | Category | Reach | Impact | Confidence | Effort (Days) | RICE Score | Decision |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Automated Broken Link Re-verifier** | Data Quality | 10 | 2.5 | 90% | 2.0 | **112.5** | **Ship in Next Patch** |
| **Expanded Skill Taxonomy Synonyms** | Relevance | 9 | 2.0 | 95% | 1.5 | **114.0** | **Ship in Next Patch** |
| **Compensation Currency Normalizer** | Market Intel | 8 | 2.0 | 90% | 2.5 | **57.6** | **Scheduled Sprint 1** |
| **Direct ATS Candidate Export** | Integration | 6 | 2.5 | 80% | 4.0 | **30.0** | **Phase 15 Roadmap** |
| **Two-Way Google Calendar Sync** | Applications | 7 | 1.5 | 70% | 5.0 | **14.7** | **Phase 15 Roadmap** |
| **Dark Mode Contrast Polish** | UX | 8 | 0.5 | 100% | 0.5 | **80.0** | **Quick Win** |

