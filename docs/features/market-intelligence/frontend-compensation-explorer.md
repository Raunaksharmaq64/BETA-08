# Frontend: Compensation Explorer

## 1. Overview
The Compensation Explorer located at `/compensation` allows candidates to inspect verified compensation distributions across roles, seniority levels, pay structures, and locations without synthetic distortions.

## 2. Key Screen Components
1. **Pay Structure Segmented Control**:
   - `Base Salary`: Fixed annual cash compensation.
   - `Total Comp`: Combined base, target bonuses, and guaranteed cash.
   - `Hourly / Contract`: Real-time contract rates for freelance or interim engagements.
   - `Equity`: Ownership grants (options or RSUs).
2. **Currency Selector**: Dropdown supporting `USD`, `EUR`, `GBP`, and `INR`. Calculations update dynamically in native currency.
3. **Statistical Summary Cards**:
   - **Audited Median**: Reported with exact sample size ($N$). If $N < 5$, safely reports "N/A" with explanatory sample badge.
   - **Observed Range**: Minimum to maximum observed bounds, plus 25th-75th interquartile ranges when $N \ge 5$.
   - **Sample Size ($N$)**: Total validated data points with confidence status.
   - **Unstated Salary Rate**: Percentage of postings in the segment omitting salary disclosures.
4. **Statistical Boundary Alert**: Informational alert explaining suppression of medians whenever sample size is under the 5-point threshold.
5. **Observation Table**: Granular list of individual verified salary rows showing role title, employer, compensation range, experience level, location, and source attribution.

