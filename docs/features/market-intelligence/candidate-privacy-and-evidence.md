# Candidate Privacy and Evidence Invariants

## 1. Absolute Non-Mutation Invariant
A foundational standard in RIGHT FIT is that **AI services and diagnostic recommendations never mutate candidate data without explicit user action**:
- The Skill-Gap Engine generates recommendations in `candidate_skill_gap_recommendations`.
- It **NEVER** automatically writes new skills into `resumes`, `resume_skills`, or `users` profile tables.
- Candidate resumes remain an uncorrupted historical record of verified experience.

## 2. No Synthetic Qualification Inventions
- The platform never fabricates or hallucinates candidate skills to artificially inflate matching scores.
- Recommendations are clearly labeled as market observations ("Observed in 14 recent Software Engineer vacancies"), not candidate assertions.

## 3. Privacy & Access Control
- All candidate skill-gap diagnostic endpoints (`/api/v1/market/skill-gaps`) require valid authenticated candidate sessions.
- Candidate diagnostics are isolated strictly to `WHERE user_id = current_user.id`.
- No employer, recruiter, or third party has access to a candidate's private learning statuses or identified gaps.

