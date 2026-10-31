"""
RIGHT FIT — Phase 8 Unit Test Suite
Notification Preferences, Category Filtering & Deduplication Suppression
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    User,
    NotificationRecord,
    NotificationPreferencesRecord,
)
from app.services.notification_service import NotificationService
from contracts.applications.schemas import (
    NotificationPreferencesUpdate,
    NotificationCategory,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        id="test-notif-user-1",
        email="notif_test@example.com",
        full_name="Notification Tester",
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


def test_notification_creation_and_read_state(db_session):
    notif = NotificationService.create_notification(
        db_session,
        user_id="test-notif-user-1",
        category=NotificationCategory.APPLICATION_FOLLOW_UP,
        title="Application Status Updated",
        message="Your application to Acme Corp moved to INTERVIEW.",
        reference_link="/applications/app-1",
    )

    assert notif is not None
    assert notif.id is not None
    assert notif.is_read is False

    # Mark as read
    updated = NotificationService.mark_as_read(db_session, notif.id, "test-notif-user-1")
    assert updated is True


def test_category_preference_suppression(db_session):
    # Disable interview reminders in preferences
    pref_req = NotificationPreferencesUpdate(
        interview_reminders=False,
        application_follow_ups=True,
        assessment_deadlines=True,
        prep_milestones=True,
    )
    NotificationService.update_preferences(db_session, "test-notif-user-1", pref_req)

    # Attempt to create an INTERVIEW_REMINDER notification
    suppressed_notif = NotificationService.create_notification(
        db_session,
        user_id="test-notif-user-1",
        category=NotificationCategory.INTERVIEW_REMINDER,
        title="Prep Task Due",
        message="Review system design notes.",
    )

    # Must be suppressed (returns None)
    assert suppressed_notif is None

    # But APPLICATION_FOLLOW_UP should be allowed
    allowed_notif = NotificationService.create_notification(
        db_session,
        user_id="test-notif-user-1",
        category=NotificationCategory.APPLICATION_FOLLOW_UP,
        title="New Recruiter Note",
        message="A recruiter replied to your message.",
    )
    assert allowed_notif is not None
    assert allowed_notif.title == "New Recruiter Note"


def test_duplicate_notification_suppression_window(db_session):
    # Create first notification
    notif1 = NotificationService.create_notification(
        db_session,
        user_id="test-notif-user-1",
        category=NotificationCategory.INTERVIEW_REMINDER,
        title="Upcoming Interview Reminder",
        message="Your interview with Datadog starts in 2 hours.",
    )
    assert notif1 is not None

    # Attempt to send the exact same notification immediately after (< 10 minutes)
    notif2 = NotificationService.create_notification(
        db_session,
        user_id="test-notif-user-1",
        category=NotificationCategory.INTERVIEW_REMINDER,
        title="Upcoming Interview Reminder",
        message="Your interview with Datadog starts in 2 hours.",
    )

    # Must be suppressed within 10-minute duplicate window (returns None)
    assert notif2 is None

    # Verify total notifications count in DB is still 1
    all_notifs = NotificationService.list_notifications(db_session, "test-notif-user-1")
    assert len(all_notifs) == 1
