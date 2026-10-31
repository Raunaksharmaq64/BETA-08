"""
RIGHT FIT — Phase 8 Unit Test Suite
CRM Application State Machine & Transition Logic
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    User,
    ApplicationRecord,
    ApplicationStatusHistoryRecord,
)
from app.services.crm_service import CRMService
from contracts.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationTransitionRequest,
    ApplicationStatus,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        id="test-crm-user-1",
        email="crm_test@example.com",
        full_name="CRM Tester",
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


def test_create_application_defaults_to_saved(db_session):
    req = ApplicationCreateRequest(
        company_name="Acme Corp",
        job_title="Senior Engineer",
        status=ApplicationStatus.SAVED,
    )
    app = CRMService.create_application(db_session, "test-crm-user-1", req)

    assert app.id is not None
    assert app.status == ApplicationStatus.SAVED
    assert app.company_name == "Acme Corp"
    assert app.job_title == "Senior Engineer"
    assert app.is_submission_confirmed is False
    assert len(app.status_history) == 1
    assert app.status_history[0].to_status == ApplicationStatus.SAVED.value


def test_open_apply_link_transitions_saved_to_planning(db_session):
    req = ApplicationCreateRequest(
        company_name="Google",
        job_title="Software Engineer",
        application_url="https://careers.google.com/jobs/123",
        status=ApplicationStatus.SAVED,
    )
    app = CRMService.create_application(db_session, "test-crm-user-1", req)
    assert app.status == ApplicationStatus.SAVED

    # Open apply link
    updated = CRMService.record_apply_link_opened(db_session, app.id, "test-crm-user-1")
    assert updated.apply_link_opened_at is not None
    assert updated.status == ApplicationStatus.PLANNING_TO_APPLY
    # CRITICAL: External link open must NEVER automatically mark as APPLIED
    assert updated.status != ApplicationStatus.APPLIED
    assert updated.is_submission_confirmed is False


def test_transition_to_applied_requires_confirmation(db_session):
    req = ApplicationCreateRequest(
        company_name="Stripe",
        job_title="Infrastructure Engineer",
        status=ApplicationStatus.SAVED,
    )
    app = CRMService.create_application(db_session, "test-crm-user-1", req)

    # Attempt to transition to APPLIED without confirmation
    with pytest.raises(ValueError, match="Candidate must explicitly confirm submission"):
        CRMService.transition_status(
            db_session,
            app.id,
            "test-crm-user-1",
            ApplicationTransitionRequest(
                to_status=ApplicationStatus.APPLIED,
                confirm_submission=False,
            ),
        )

    # Now transition with confirmation
    confirmed_app = CRMService.transition_status(
        db_session,
        app.id,
        "test-crm-user-1",
        ApplicationTransitionRequest(
            to_status=ApplicationStatus.APPLIED,
            reason="Submitted through Stripe careers portal",
            confirm_submission=True,
        ),
    )
    assert confirmed_app.status == ApplicationStatus.APPLIED
    assert confirmed_app.is_submission_confirmed is True
    assert confirmed_app.applied_at is not None


def test_invalid_state_transition_is_blocked(db_session):
    req = ApplicationCreateRequest(
        company_name="Meta",
        job_title="Production Engineer",
        status=ApplicationStatus.SAVED,
    )
    app = CRMService.create_application(db_session, "test-crm-user-1", req)

    # Cannot transition directly from SAVED to OFFER
    with pytest.raises(ValueError, match="Invalid transition from"):
        CRMService.transition_status(
            db_session,
            app.id,
            "test-crm-user-1",
            ApplicationTransitionRequest(to_status=ApplicationStatus.OFFER),
        )


def test_auditable_status_history_trail(db_session):
    req = ApplicationCreateRequest(
        company_name="Apple",
        job_title="CoreOS Engineer",
        status=ApplicationStatus.SAVED,
    )
    app = CRMService.create_application(db_session, "test-crm-user-1", req)

    # Transition to PLANNING_TO_APPLY
    CRMService.transition_status(
        db_session,
        app.id,
        "test-crm-user-1",
        ApplicationTransitionRequest(
            to_status=ApplicationStatus.PLANNING_TO_APPLY, reason="Preparing resume"
        ),
    )

    # Transition to APPLIED
    CRMService.transition_status(
        db_session,
        app.id,
        "test-crm-user-1",
        ApplicationTransitionRequest(
            to_status=ApplicationStatus.APPLIED,
            reason="Applied on portal",
            confirm_submission=True,
        ),
    )

    # Transition to INTERVIEW
    final_app = CRMService.transition_status(
        db_session,
        app.id,
        "test-crm-user-1",
        ApplicationTransitionRequest(
            to_status=ApplicationStatus.INTERVIEW, reason="Recruiter scheduled round 1"
        ),
    )

    assert len(final_app.status_history) == 4
    statuses = [h.to_status for h in final_app.status_history]
    assert list(reversed(statuses)) == ["SAVED", "PLANNING_TO_APPLY", "APPLIED", "INTERVIEW"]
