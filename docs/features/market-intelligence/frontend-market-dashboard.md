# Frontend: Market Demand Dashboard & Skill Profile

## 1. Overview
The Market Demand frontend provides candidates with an intuitive, responsive, and empirically grounded dashboard located at `/market-intelligence` and individual skill pages at `/market-intelligence/skills/[skillId]`.

## 2. Key Screen Components

### `/market-intelligence` (Dashboard)
1. **Interactive Time-Window Toggle**: Seamlessly switch between `7d`, `30d`, and `90d` rolling aggregation windows.
2. **Track & Geography Filters**: Filter demand by role disciplines (`Software Engineering`, `Data & AI`, `Product`, `Design`, `DevOps`) and geographic work arrangements (`Global`, `US Remote`, `US Onsite`, `EU Remote`, `India`).
3. **Audit Sample Disclosures**: Top banner showing collection period, total sample size ($N$), distinct employer count, and statistical confidence grade.
4. **Demand Card Grid**: Displays canonical skill name, category, distinct vacancy count, market penetration %, and period-over-period trend badge (`RISING`, `STEADY`, `FALLING`).
5. **Quick Navigation Links**: Direct action buttons to Candidate Skill-Gap Diagnostics, Compensation Explorer, and Sources Registry.

### `/market-intelligence/skills/[skillId]` (Skill Profile)
1. **Canonical Header**: Displays verified canonical title, slug, taxonomy category, and technology family.
2. **Synonyms & Aliases**: Tag cloud showing all colloquial abbreviations and query strings that resolve to this skill node.
3. **Multi-Window Demand Snapshots**: Side-by-side cards comparing observed distinct vacancies across `7d`, `30d`, and `90d` horizons.
4. **Governance Invariants**: Detailed methodology box confirming anti-duplication rules and sample thresholds.

