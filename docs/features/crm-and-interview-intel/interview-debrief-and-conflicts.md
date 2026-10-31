# Interview Debrief & Conflict Resolution

## Overview
Capturing impressions immediately after an interview round is critical. The Interview Debrief feature allows candidates to document interviewer questions, perceived friction points, strengths, and areas requiring clarification in subsequent rounds.

## Post-Round Debrief Capture
Candidates complete a rapid debrief within 2 hours of completing a round:
- **Questions Asked**: Actual technical and behavioral questions encountered.
- **Candidate Answers**: Key points and trade-offs mentioned.
- **Perceived Friction / Knowledge Gaps**: Topics where candidate felt uncertain or hesitated.
- **Interviewer Signals**: Positive or negative verbal and non-verbal cues.
- **Next Steps & Commitments**: Materials or repositories promised to send.

## Conflict Resolution & Contradiction Detection
When preparing for subsequent rounds with the same company:
- The system flags potential contradictions across rounds (e.g. telling Round 2 you are looking for pure IC work, while telling Round 3 you want to manage engineers).
- Highlights questions that were unanswered or weakly answered for targeted redemption in later rounds.

## Schema (`InterviewDebriefRecord`)
```python
class InterviewDebriefRecord(Base):
    __tablename__ = "interview_debriefs"
    id = Column(String(36), primary_key=True)
    round_id = Column(String(36), ForeignKey("interview_rounds.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("candidate_profiles.id"), nullable=False)
    self_rating = Column(Integer, nullable=False)  # 1 to 5
    questions_recalled = Column(JSON, default=list)
    perceived_strengths = Column(Text, nullable=True)
    perceived_weaknesses = Column(Text, nullable=True)
    follow_up_items = Column(JSON, default=list)
    interviewer_vibe = Column(String(64), nullable=True)  # POSITIVE, NEUTRAL, LUKEWARM, ADVERSARIAL
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
```

