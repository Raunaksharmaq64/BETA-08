# ATS Keyword Coverage & Bullet Impact Analysis

## 1. Ethical Stance & Limitations Disclosure

Applicant Tracking Systems (ATS) used across global enterprises (such as Greenhouse, Lever, Ashby, Workday, and BambooHR) employ varied, often proprietary parsing and ranking mechanisms.

**RIGHT FIT does not claim to reproduce proprietary black-box algorithms.**

Instead, RIGHT FIT provides a transparent, deterministic analysis system focusing on:
1. High-signal keyword frequency coverage between a target job description and resume text.
2. Quantified impact cues in work experience bullets (percentages, dollar amounts, multipliers, scale, and action verbs).
3. Actionable, non-fabricating improvement guidance.

---

## 2. Keyword Coverage Scoring Methodology

The `ATSAnalysisService` (`app/services/ats_service.py`) reuses the verified `ats_keyword_coverage.py` engine from Phase 0:

$$\text{Coverage Score} = \frac{|\text{Matched Keywords}|}{|\text{Top } K \text{ Job Description Keywords}|}$$

1. **Tokenization**:
   - Strips common punctuation and extracts alphanumeric tokens.
   - Filters out English stopwords (`and`, `the`, `with`, `for`, `responsible`, etc.).
2. **Frequency Ranking**:
   - Ranks the most distinctive keywords in the job description by term frequency (top 25 keywords by default).
3. **Set Intersection**:
   - Matches job keywords against the set of tokens present in the resume text.
   - Partitions results into `matched_keywords` and `missing_keywords`.

---

## 3. Quantified Bullet Impact Scoring

Work experience bullet points are analyzed for measurable outcomes and action verbs:

### Impact Cue Signatures:
- **Action Verbs**: Starting sentences with verbs such as *led*, *shipped*, *architected*, *automated*, *reduced*, *increased*, *scaled*.
- **Percentages**: Matches `\d+%$` (e.g. `25%`, `40.5%`).
- **Financial Metrics**: Matches `\$\d+[kKmMbB]?` (e.g. `$50,000`, `$1.2M`).
- **Multipliers**: Matches `\d+x\b` (e.g. `2x`, `10x`).
- **Scale Indicators**: Matches volume nouns (e.g. `100k users`, `5M requests`, `15 engineers`).

$$\text{Bullet Impact Score} = \left(\frac{\text{Strong Bullets Count}}{\text{Total Bullets Count}}\right) \times 100$$

---

## 4. No-Fabrication AI & Advisory Policy

When generating optimization suggestions:
- ❌ **AI Must Never Invent Metrics**: It is strictly forbidden to suggest adding fictional numbers (e.g. *"Say you increased speed by 40%"*).
- ❌ **AI Must Never Invent Skills**: It is strictly forbidden to instruct candidates to list skills they do not possess.
- ✅ **Advisory Guidance (HITL)**:
  - If a bullet lacks numbers: *"Your bullet mentions optimizing a database. If you have measured performance metrics (such as query latency reduction), consider adding the verified figures."*
  - If keywords are missing: *"The job description mentions Docker and Kubernetes. If you have experience with these tools, consider including them."*
  - Every suggestion is explicitly labeled as `is_advisory = True`.

