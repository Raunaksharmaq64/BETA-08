"""
RIGHT FIT — Phase 8 Unit Test Suite
Mock Interview Engine & 6-Factor Rubric Evaluation
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    User,
    MockInterviewSessionRecord,
    MockInterviewQuestionRecord,
)
from app.services.interview_intelligence_service import InterviewIntelligenceService
from contracts.applications.schemas import (
    MockSessionCreateRequest,
    MockSessionType,
    MockQuestionAnswerRequest,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        id="test-mock-user-1",
        email="mock_test@example.com",
        full_name="Mock Tester",
        password_hash="pw_hash",
        role="CANDIDATE",
        status="ACTIVE",
        is_email_verified=True,
    )
    session.add(user)
    session.commit()

    yield session

    session.close()
    engine.dispose()


def test_start_mock_session_generates_standard_questions(db_session):
    start_req = MockSessionCreateRequest(
        role_title="Senior Backend Architect",
        session_type=MockSessionType.BEHAVIORAL,
        question_count=3,
    )

    session = InterviewIntelligenceService.create_mock_session(db_session, "test-mock-user-1", start_req)
    assert session.id is not None
    assert session.role_title == "Senior Backend Architect"
    assert session.session_type == MockSessionType.BEHAVIORAL
    assert len(session.questions) >= 3

    # Every question has text and category
    for q in session.questions:
        assert q.question_text
        assert q.category


def test_rubric_evaluation_high_scoring_response(db_session):
    start_req = MockSessionCreateRequest(
        role_title="Lead Software Engineer",
        session_type=MockSessionType.BEHAVIORAL,
    )
    session = InterviewIntelligenceService.create_mock_session(db_session, "test-mock-user-1", start_req)
    target_q = session.questions[0]

    # Detailed, structured STAR response with technical keywords and quantifiable metrics
    strong_response = (
        "Situation: In my role at Netflix, our video metadata service was encountering significant latency spikes. "
        "Task: I was responsible for refactoring the caching architecture to support 50,000 queries per second with sub-10ms latency. "
        "Action: I evaluated Hazelcast vs Redis clusters, designed a non-blocking connection pool using Netty, "
        "and implemented a distributed lock mechanism with lease renewals to eliminate cache stampedes. "
        "Result: We reduced p99 latency by 85% to 6ms, achieved zero downtime during global deployment, and saved $80,000 in cluster costs."
    )

    answer_req = MockQuestionAnswerRequest(
        question_id=target_q.id,
        candidate_answer=strong_response,
    )

    evaluated_q = InterviewIntelligenceService.submit_mock_answer(
        db_session, session.id, "test-mock-user-1", answer_req
    )

    assert evaluated_q.candidate_answer == strong_response
    assert evaluated_q.rubric_evaluation is not None

    rubric = evaluated_q.rubric_evaluation
    # Verify all 6 factors are scored 0-10
    for factor in [
        rubric.relevance,
        rubric.clarity,
        rubric.structure,
        rubric.evidence,
        rubric.technical_correctness,
        rubric.communication,
    ]:
        assert 0 <= factor <= 10

    # Should achieve a high score (>= 7.0 / 10)
    assert rubric.overall_score >= 7.0
    assert len(rubric.strengths) > 0


def test_rubric_evaluation_low_scoring_response(db_session):
    start_req = MockSessionCreateRequest(
        role_title="Junior Developer",
        session_type=MockSessionType.TECHNICAL,
    )
    session = InterviewIntelligenceService.create_mock_session(db_session, "test-mock-user-1", start_req)
    target_q = session.questions[0]

    # Brief, unstructured response without metrics or specifics
    weak_response = "I basically wrote some code and it worked fine."

    answer_req = MockQuestionAnswerRequest(
        question_id=target_q.id,
        candidate_answer=weak_response,
    )

    evaluated_q = InterviewIntelligenceService.submit_mock_answer(
        db_session, session.id, "test-mock-user-1", answer_req
    )
    rubric = evaluated_q.rubric_evaluation

    # Weak response should reflect low score
    assert rubric.overall_score < 7.0
    # Must provide constructive improvement tips
    assert len(rubric.areas_for_improvement) > 0
