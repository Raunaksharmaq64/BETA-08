# Trend Analysis Methodology

## 1. Objective
Market signals change over time as new engineering paradigms, frameworks, and infrastructure tools gain or lose adoption. RIGHT FIT provides directional indicators (`RISING`, `STEADY`, `FALLING`) based strictly on audited period-over-period delta calculations.

## 2. Directional Thresholds
Let:
- $F_{\text{current}}$ be the skill frequency in the most recent observation window (e.g. current 30-day period).
- $F_{\text{prior}}$ be the skill frequency in the preceding equivalent observation window (e.g. prior 30-day period).
- Relative change percentage:
  $$\Delta = \frac{F_{\text{current}} - F_{\text{prior}}}{F_{\text{prior}}} \times 100$$

### Classification Rules:
- **`RISING`**: $\Delta \ge +10.0\%$ (Demonstrating measurable hiring acceleration).
- **`FALLING`**: $\Delta \le -10.0\%$ (Demonstrating measurable contraction in postings).
- **`STEADY`**: $-10.0\% < \Delta < +10.0\%$ (Stable market equilibrium).

## 3. Sample Size Threshold for Trend Reporting
To prevent erratic oscillation caused by small denominator noise:
- If current period sample $N_{\text{current}} < 10$ or prior period sample $N_{\text{prior}} < 10$, directional trends are marked as `STEADY` or flagged with low-confidence annotations.
- A skill moving from 1 posting to 2 postings in a sample of 5 is not reported as "+100% Growth" to avoid misleading candidates.

