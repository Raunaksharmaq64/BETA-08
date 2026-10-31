# Candidate Relevance Feedback System

## 1. Feedback Loop
Candidates can submit feedback on any opportunity type using `POST /api/v1/opportunities/{type}/{id}/feedback`.

### Supported Feedback Categories
- `IRRELEVANT`: Not aligned with candidate career preferences or target industry.
- `ALREADY_APPLIED`: Candidate already submitted an application or contacted the client.
- `INCORRECT_SKILLS`: Skills requirement mismatch.
- `WRONG_LOCATION`: Geographic or time-zone incompatibility.
- `OTHER`: Candidate-supplied custom explanation.

## 2. Storage Model
Feedback is recorded in `candidate_opportunity_feedback` (`CandidateOpportunityFeedbackRecord`):
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to `users.id`)
- `opportunity_id`: String
- `opportunity_type`: String (`JOB`, `FREELANCE`, `STARTUP_PAIN_POINT`)
- `feedback_category`: String
- `explanation`: Text (nullable)
- `created_at`: DateTime (UTC)

## 3. Strict Boundary Rule
Candidate feedback:
- **DOES NOT** suppress the opportunity for other candidates.
- **DOES NOT** modify `verification_status` or freshness state on the opportunity.
- **DOES NOT** mutate source corroboration or evidence data.
- **ONLY** tunes personalized recommendations for the submitting candidate.

