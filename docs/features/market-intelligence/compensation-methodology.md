# Compensation Methodology

## 1. Core Principles
The Compensation Intelligence engine adheres to four scientific and ethical commitments:
1. **Pay Structure Isolation**: Base salary, variable bonuses, equity incentives, and freelance hourly rates are distinct financial instruments. They are never conflated into an opaque composite number.
2. **Audited Evidence Grounding**: Every data point corresponds to an authenticated job posting disclosure, statutory regulatory filing, or verified candidate pay stub.
3. **Statistically Justified Central Tendency**: Medians and percentiles are computed only when sample size meets minimum robustness requirements ($N \ge 5$).
4. **Range Transparency**: Both lower and upper bounds of disclosed compensation ranges are audited and reported.

## 2. Table Definition: `compensation_observations`
```sql
CREATE TABLE compensation_observations (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES canonical_opportunities(id) ON DELETE SET NULL,
    source_id UUID NOT NULL REFERENCES market_data_sources(id),
    role_title VARCHAR(256) NOT NULL,
    role_category VARCHAR(64) NOT NULL,
    geography VARCHAR(128) NOT NULL,
    experience_level VARCHAR(64) NOT NULL,
    compensation_type VARCHAR(64) NOT NULL,
    currency VARCHAR(8) NOT NULL,
    base_salary_min NUMERIC(14, 2),
    base_salary_max NUMERIC(14, 2),
    total_compensation_min NUMERIC(14, 2),
    total_compensation_max NUMERIC(14, 2),
    hourly_rate NUMERIC(10, 2),
    equity_pct_min NUMERIC(6, 4),
    equity_pct_max NUMERIC(6, 4),
    is_verified BOOLEAN DEFAULT TRUE,
    observed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 3. Percentile Computation
Given an ordered list of observed compensation values $X = [x_1, x_2, \dots, x_N]$ where $N \ge 5$:
- **Median ($P_{50}$)**:
  $$\tilde{x} = \begin{cases} 
  x_{(N+1)/2}, & \text{if } N \text{ is odd} \\
  \frac{x_{N/2} + x_{N/2 + 1}}{2}, & \text{if } N \text{ is even}
  \end{cases}$$
- **25th Percentile ($P_{25}$)**: The value below which 25% of the verified observations fall.
- **75th Percentile ($P_{75}$)**: The value below which 75% of the verified observations fall.
- **Observed Range**: $[\min(X), \max(X)]$.

