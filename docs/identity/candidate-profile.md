# RIGHT FIT — Candidate Profile Specification
**Version:** 1.0.0  
**Phase:** 3 — Identity, Candidate Profile & Privacy Foundation  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Domain Ownership

The candidate profile is owned exclusively by the Core Career Engine (`career_core.candidate_profiles`). Satellite services consume normalized opportunity signals but must never create parallel candidate profile repositories.

---

## 2. Profile Data Model

```
                    ┌───────────────────────────┐
                    │     CandidateProfile      │
                    │ (headline, summary, city) │
                    └─────────────┬─────────────┘
                                  │
     ┌────────────────────────────┼────────────────────────────┐
     ▼                            ▼                            ▼
[ Education ]              [ Experience ]               [ CandidateSkill ]
 (degree, institution,      (company, role, skills,      (name, category,
  dates, provenance)         employment_type)             proficiency, years)
```

### 2.1 Sub-Entities
1. **Education Credentials (`educations`):**
   - Degree, institution, field of study, date range, current status, and provenance.
2. **Professional Experience (`experiences`):**
   - Company, role, employment type, start/end dates, description, tags, and provenance.
3. **Skills & Competencies (`candidate_skills`):**
   - Skill name, category (e.g. Backend, AI, Cloud), proficiency level (Beginner, Intermediate, Expert), years of experience.

---

## 3. Profile Completeness Metric

To guide candidate onboarding and optimize machine learning match fidelity, Core computes a transparent profile completeness score ($0-100\%$):

| Section | Weight | Criteria |
| :--- | :--- | :--- |
| **Basic Information** | 20% | Non-empty headline and professional summary. |
| **Education Credentials** | 20% | At least 1 verified or user-provided degree entry. |
| **Professional Experience**| 20% | At least 1 employment record with role description. |
| **Skills & Competencies** | 20% | At least 3 tagged technical skills. |
| **Career Preferences** | 20% | At least 1 preferred job title and remote preference. |

Endpoint: `GET /api/v1/candidate/profile/completeness` returns the numerical score and lists missing sections to guide users.

---

## 4. API Reference

- `GET /api/v1/candidate/profile`: Returns full profile with nested collections.
- `PUT /api/v1/candidate/profile`: Updates headline, summary, and location.
- `POST /api/v1/candidate/education`: Appends education entry.
- `DELETE /api/v1/candidate/education/{edu_id}`: Removes education entry (verifies ownership).
- `POST /api/v1/candidate/experience`: Appends experience record.
- `DELETE /api/v1/candidate/experience/{exp_id}`: Removes experience record.
- `POST /api/v1/candidate/skills`: Appends skill.
- `DELETE /api/v1/candidate/skills/{skill_id}`: Removes skill.
