# Dashboard Summary Metrics & Reconciliation Rules

## 1. Metric Calculation Formulae
The dashboard guarantees strict mathematical consistency across all reported metrics.

### Formula 1: Total Opportunities Reconciliation
$$\text{Total Opportunities} = \text{Total Jobs} + \text{Total Freelance} + \text{Total Startups}$$

Under no circumstances may `total_opportunities` diverge from the direct sum of the underlying table records.

### Formula 2: Total Saved Bookmarks
$$\text{Total Saved} = \text{Saved Jobs} + \text{Saved Freelance} + \text{Saved Startups}$$

### Formula 3: New Ingestions This Week
$$\text{New This Week} = \text{Jobs}_{t \ge 7d} + \text{Freelance}_{t \ge 7d} + \text{Startups}_{t \ge 7d}$$

Where $t \ge 7d$ represents records discovered or ingested within the past 7 days (`utc_now() - timedelta(days=7)`).

## 2. Active Application Tracking
Candidates actively applying to jobs or pitching clients have their records tracked in `applications` (`ApplicationRecord`). The dashboard reports `active_applications` by querying non-terminal application statuses (`APPLIED`, `INTERVIEWING`, `OFFER`).

## 3. High-Urgency Signals
Startups with `urgency_score >= 8` represent immediate founder pain points and are singled out as high-conviction actionable leads.

