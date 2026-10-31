# Confidence Boundaries & Sample Disclosures

## 1. The Anti-False-Precision Imperative
False precision occurs when statistical systems report highly specific figures (e.g. "Median Senior React Salary: \$147,382.14") based on tiny, unrepresentative samples ($N=2$ or $3$). This creates unwarranted candidate confidence and degrades trust.

## 2. The Minimum Robust Sample Rule ($N \ge 5$)
RIGHT FIT enforces an absolute statistical threshold across all compensation endpoints and interfaces:
- **Condition**: $\text{Sample Size } N \ge 5$.
- **When $N \ge 5$**:
  - `has_statistically_justified_median: true`
  - `median`: Calculated and reported.
  - `p25`, `p75`: Calculated and reported.
- **When $N < 5$**:
  - `has_statistically_justified_median: false`
  - `median: null`
  - `p25: null`, `p75: null`
  - A prominent UI banner is displayed explaining that the sample size ($N$) is insufficient for composite medians.
  - Raw observations remain visible in the table for qualitative inspection without synthetic statistical claims.

## 3. Unstated Compensation Disclosures
Many employers omit compensation figures in job postings. To provide full transparency into hiring visibility:
- The engine calculates the **Unstated Salary Rate**:
  $$\text{MissingRate} = \frac{N_{\text{postings without salary}}}{N_{\text{total postings in segment}}}$$
- Disclosing this rate protects candidates from assuming that disclosed salaries represent 100% of the active market.

