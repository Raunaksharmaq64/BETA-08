# Evidence-Based Skill Fit Engine

## 1. Grounded Matching Rules

The Skill Fit Engine operates under strict ethical and transparency principles:
1. **Zero Hallucination Guarantee**: The system will never invent, guess, or extrapolate candidate skills, certifications, or experience.
2. **Provenance Traceability**: Every matched skill links directly to an auditable excerpt from the candidate's reviewed resume or candidate-entered profile skills.
3. **Review Status Transparency**: Skills extracted from a resume that have not yet been approved by the candidate are classified as `unconfirmed_skills` and visually flagged.

---

## 2. Skill Normalization & Canonical Aliases

Technical skills are matched via canonical token normalization and alias mapping:
| Raw Skill Input | Canonical Normalized Token |
| :--- | :--- |
| `React.js`, `reactjs` | `react` |
| `NextJS`, `next.js` | `next.js` |
| `Py`, `Python3` | `python` |
| `Golang` | `go` |
| `K8s` | `kubernetes` |
| `Postgres`, `psql` | `postgresql` |
| `TS`, `Typescript` | `typescript` |
| `JS`, `Javascript` | `javascript` |
| `AWS` | `amazon web services` |

---

## 3. Fit Score Calculation Formula

The skill fit percentage is computed transparently:
- **Required Skills Weight**: 80%
- **Preferred Skills Weight**: 20%

$$\text{Fit Score} = \left( \frac{\text{Matched Required}}{\text{Total Required}} \times 80.0 \right) + \left( \frac{\text{Matched Preferred}}{\text{Total Preferred}} \times 20.0 \right)$$

If a job posting does not specify preferred skills:
$$\text{Fit Score} = \frac{\text{Matched Required}}{\text{Total Required}} \times 100.0$$

If no required or preferred skills are documented, the baseline fit defaults to 100.0% so the candidate is not penalized for an under-specified job post.

