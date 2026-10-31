"""
RIGHT FIT — Phase 8 Unit Test Suite
Interview Intelligence Grounding, Missing Metrics & 48-Hour Sprint
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    User,
    ApplicationRecord,
    InterviewPlanRecord,
    STARAnswerRecord,
)
from app.services.interview_intelligence_service import InterviewIntelligenceService
from contracts.applications.schemas import (
    InterviewPlanCreate,
    STARAnswerCreate,
    InterviewDebriefCreate,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        id="test-intel-user-1",
        email="intel_test@example.com",
        full_name="Intelligence Tester",
        password_hash="pw_hash",
        role="CANDIDATE",
        status="ACTIVE",
        is_email_verified=True,
    )
    session.add(user)

    app_rec = ApplicationRecord(
        id="app-intel-1",
        user_id="test-intel-user-1",
        company_name="Datadog",
        job_title="Distributed Systems Engineer",
        status="INTERVIEW",
    )
    session.add(app_rec)
    session.commit()

    yield session

    session.close()
    engine.dispose()


def test_star_answer_with_quantifiable_metrics(db_session):
    req = STARAnswerCreate(
        question="Tell me about migrating monolith payments to microservices",
        category="SYSTEM_DESIGN",
        situation="Payment processing latency was spiking to 1200ms on peak sales days.",
        task="Architect an idempotent event-driven settlement worker.",
        action="Designed Redis distributed locks with exponential backoff and dual-write shadow verification.",
        result="Reduced p99 latency by 72% to 45ms, supported 30,000 RPS, and cut cloud server costs by $45,000 annually.",
        supporting_evidence_reference="Resume Section: Staff Backend Engineer at FinTech Corp",
    )

    ans = InterviewIntelligenceService.create_star_answer(db_session, "test-intel-user-1", req)
    assert ans.id is not None
    assert ans.question == "Tell me about migrating monolith payments to microservices"
    # When numbers/percentages are present, no missing information notes
    assert ans.missing_information_notes is None
    assert ans.supporting_evidence_reference == "Resume Section: Staff Backend Engineer at FinTech Corp"


def test_star_answer_missing_metrics_flagged_not_hallucinated(db_session):
    # Candidate provides vague qualitative Result without any numbers/percentages
    req = STARAnswerCreate(
        question="Describe how you improved the team's review workflow",
        category="LEADERSHIP",
        situation="Team members were waiting several days for pull request reviews.",
        task="Create a better review culture.",
        action="Introduced PR templates and scheduled daily triage office hours.",
        result="The team was much happier and code reviews felt faster and more collaborative.",
    )

    ans = InterviewIntelligenceService.create_star_answer(db_session, "test-intel-user-1", req)
    assert ans.id is not None
    # Crucial: Must flag missing quantifiable metrics rather than fabricating numbers
    assert ans.missing_information_notes is not None
    assert "Adding quantifiable metrics" in ans.missing_information_notes


def test_48_hour_sprint_blocks_synthesis(db_session):
    plan_req = InterviewPlanCreate(
        application_id="app-intel-1",
        title="Datadog Sprint Plan",
        company_name="Datadog",
        role_title="Distributed Systems Engineer",
    )
    plan = InterviewIntelligenceService.create_plan(db_session, "test-intel-user-1", plan_req)

    sprint = InterviewIntelligenceService.generate_48_hour_prep(db_session, plan.id, "test-intel-user-1")
    assert sprint.company_name == "Datadog"
    assert sprint.role_title == "Distributed Systems Engineer"
    assert len(sprint.prioritized_milestones) >= 3

    # Verify milestones prioritize technical deep dive and STAR stories
    actions = [m.action for m in sprint.prioritized_milestones]
    assert any("Deep-Dive" in a for a in actions)
    assert any("STAR" in a for a in actions)


def test_interview_debrief_logging(db_session):
    now_utc = datetime.now(timezone.utc)
    debrief_req = InterviewDebriefCreate(
        application_id="app-intel-1",
        round_name="Architecture Round",
        interview_date=now_utc,
        questions_asked=[
            "How do you handle split-brain in Raft?",
            "Tell me about a time you made a wrong architectural decision.",
        ],
        topics_discussed="Distributed systems consensus and fault tolerance",
        candidate_reflections="Strong communication and clear explanations.",
        strengths="Clear system design diagrams and failure analysis.",
        areas_to_improve="Could have discussed tombstone garbage collection earlier.",
        recruiter_commitments="Recruiter promised final decision by Friday 4 PM.",
        next_step="Follow up next week",
    )

    deb = InterviewIntelligenceService.record_debrief(db_session, "test-intel-user-1", debrief_req)
    assert deb.id is not None
    assert deb.round_name == "Architecture Round"
    assert len(deb.questions_asked) == 2
    assert "Friday 4 PM" in deb.recruiter_commitments
