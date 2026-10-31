# Mandatory Eligibility Engine

## 1. Separation of Eligibility from Skill Fit

A candidate may have 100% skill match for a role but be ineligible due to:
- Work location / country legal restrictions
- Minimum years of professional experience
- Formal degree requirements (e.g. Master's or PhD)

RIGHT FIT evaluates and presents **Mandatory Eligibility** independently from **Skill Fit**. Skill fit indicates technical alignment; Mandatory Eligibility evaluates legal and non-negotiable prerequisites.

---

## 2. Evaluation Status States

| Status | Definition |
| :--- | :--- |
| `MEETS_REQUIREMENTS` | All documented mandatory criteria are verified and satisfied by candidate records. |
| `DOES_NOT_MEET_REQUIREMENTS` | One or more mandatory criteria are explicitly not satisfied (e.g. candidate is located in UK, but job requires on-site in Tokyo). |
| `UNKNOWN` | Candidate profile data is incomplete (e.g. no education or experience entries recorded yet). |
| `NEEDS_REVIEW` | Criteria requires human or recruiter verification (e.g. security clearance, portfolio review). |

> [!IMPORTANT]
> **No False Rejections on Missing Data**: Missing candidate data must **never** be treated as a rejection. The engine returns `UNKNOWN` with actionable guidance prompting the candidate to complete their profile.

---

## 3. Evaluated Constraints

### A. Location & Remote Arrangement
- Fully remote positions evaluate to `SATISFIED`.
- On-site or hybrid roles compare candidate city/country with the job posting location. If candidate location is omitted from their profile, it evaluates to `UNKNOWN`.

### B. Minimum Experience Years
- Years required are parsed from the job title and description (e.g., regex `(\d+)\+? years of experience` or title tiers like "Senior" -> 5 years).
- Total experience duration is calculated from candidate profile entries.
- If candidate has no experience entries recorded, status is `UNKNOWN`.

### C. Degree & Education
- Post-secondary degree requirements (Bachelor's, Master's, PhD) are checked against candidate education records.
- If required degree is held, status is `SATISFIED`.
- If candidate has not entered education history, status is `UNKNOWN`.

