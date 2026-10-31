# Candidate Isolation & Data Privacy Architecture

## 1. Principles of Candidate Isolation
RIGHT FIT treats candidate interactions as strictly confidential. No candidate's search patterns, bookmarks, application status, or feedback may ever leak into global datasets, universal ranking algorithms, or employer-facing records.

## 2. Enforcement Mechanisms
1. **User Scoping in SQL**:
   Every query for saved opportunities or feedback strictly enforces `WHERE user_id = :current_user_id`.
2. **Read-Only Ingestion Records**:
   Core ingestion records (`canonical_opportunities`, `freelance_opportunities`, `startup_opportunities`) are immutable from candidate client sessions. Candidates can only create relations in isolated join tables.
3. **No Cross-Candidate Contamination**:
   A candidate marking an opportunity as "Irrelevant" creates a single record in `candidate_opportunity_feedback` referencing only their `user_id`. It has zero effect on other candidates' search feeds.
4. **GDPR / Privacy Compliance**:
   Under Account Deletion (Phase 3), deleting a user cascades to remove all associated `SavedJobRecord`, `SavedFreelanceOpportunityRecord`, `SavedStartupOpportunityRecord`, and `CandidateOpportunityFeedbackRecord` rows.

