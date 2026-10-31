# Demand Aggregation Rules

## 1. Distinct Vacancy Counting Rule
A core anti-manipulation invariant of the RIGHT FIT Career Intelligence Platform is that **market demand measures distinct hiring opportunities, not keyword frequency within prose**.

### Invariant:
$$\text{DistinctJobCount}(S) = \left| \{ O \in \text{Opportunities} \mid S \in \text{Skills}(O) \} \right|$$

- If an employer repeats "Python" 12 times in a single job description (e.g. in the header, responsibilities, requirements, qualifications, and benefits), `DistinctJobCount("Python")` increments by **exactly 1**.
- This completely prevents keyword stuffing, SEO gaming, and inflated skill weightings.

## 2. Aggregation Time Windows
The demand aggregation engine operates across three fixed rolling windows:
- **`7d` (7 Days)**: High-velocity market pulse identifying immediate hiring spikes and emergent tools.
- **`30d` (30 Days)**: Standard benchmark window for monthly reporting, candidate skill-gap scoring, and primary dashboard cards.
- **`90d` (90 Days)**: Macro quarterly perspective establishing baseline technology adoption and seasonal cyclicality.

## 3. Market Frequency Computation
For any given time window $W$ and role category $R$:
1. Determine total verified sample size $N_{W, R}$:
   $$N_{W, R} = \left| \{ O \in \text{Opportunities} \mid \text{window}(O) = W \land \text{category}(O) = R \} \right|$$
2. Determine distinct count for skill $S$, $C_{S, W, R}$.
3. Calculate percentage penetration:
   $$\text{FrequencyPct}(S, W, R) = \begin{cases} 
   \text{round}\left(\frac{C_{S, W, R}}{N_{W, R}} \times 100, 1\right), & \text{if } N_{W, R} > 0 \\
   0.0, & \text{otherwise}
   \end{cases}$$

## 4. Distinct Employer Tracking
Along with vacancy count, the snapshot aggregates the number of unique employers (`distinct_employers`). If 50 Python postings originate from only 1 staffing agency, the distinct employer count ($E=1$) alerts candidates to hiring concentration risks.

