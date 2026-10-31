"""
RIGHT FIT — Phase 8 Unit Test Suite
Reminders, IANA Timezone Conversions & Conflict Detection
"""

import pytest
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    User,
    ApplicationRecord,
    ReminderRecord,
    InterviewPlanRecord,
    InterviewRoundRecord,
)
from app.services.reminder_service import ReminderService
from contracts.applications.schemas import (
    ReminderCreateRequest,
    ReminderType,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        id="test-tz-user-1",
        email="tz_tester@example.com",
        full_name="Timezone Tester",
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


def test_reminder_stored_in_utc_and_formatted_in_iana_timezone(db_session):
    # Candidate creates a reminder at 2:00 PM IST (UTC+5:30)
    ist_tz = ZoneInfo("Asia/Kolkata")
    dt_ist = datetime(2026, 11, 15, 14, 0, 0, tzinfo=ist_tz)
    # Corresponding UTC is 8:30 AM
    dt_utc = dt_ist.astimezone(timezone.utc)

    req = ReminderCreateRequest(
        title="Follow up on status",
        due_at_utc=dt_utc,
        timezone="Asia/Kolkata",
        reminder_type=ReminderType.FOLLOW_UP,
    )
    reminder = ReminderService.create_reminder(db_session, "test-tz-user-1", req)

    assert reminder.title == "Follow up on status"
    # Ensure UTC in DB
    assert reminder.due_at_utc.hour == 8
    assert reminder.due_at_utc.minute == 30

    # Retrieve calendar events formatted in Asia/Kolkata
    events = ReminderService.get_calendar_events(
        db_session,
        "test-tz-user-1",
        start_utc=dt_utc - timedelta(days=1),
        end_utc=dt_utc + timedelta(days=1),
        candidate_timezone="Asia/Kolkata",
    )

    assert len(events) == 1
    ev = events[0]
    assert ev.event_type == "REMINDER"
    assert "Follow up on status" in ev.title
    assert ev.candidate_timezone == "Asia/Kolkata"


def test_daylight_saving_transition_handling(db_session):
    # America/New_York DST transition check
    # EDT (UTC-4) in summer vs EST (UTC-5) in winter
    ny_tz = ZoneInfo("America/New_York")
    summer_dt = datetime(2026, 7, 10, 10, 0, 0, tzinfo=ny_tz)
    winter_dt = datetime(2026, 12, 10, 10, 0, 0, tzinfo=ny_tz)

    # In summer EDT, 10:00 AM EDT is 14:00 UTC
    assert summer_dt.astimezone(timezone.utc).hour == 14

    # In winter EST, 10:00 AM EST is 15:00 UTC
    assert winter_dt.astimezone(timezone.utc).hour == 15

    # Create summer reminder
    req_summer = ReminderCreateRequest(
        title="Summer Review",
        due_at_utc=summer_dt.astimezone(timezone.utc),
        timezone="America/New_York",
        reminder_type=ReminderType.ASSESSMENT_DEADLINE,
    )
    rem = ReminderService.create_reminder(db_session, "test-tz-user-1", req_summer)
    assert rem.due_at_utc.hour == 14


def test_schedule_conflict_detection(db_session):
    now_utc = datetime.now(timezone.utc)

    # Create application record first
    app_rec = ApplicationRecord(
        id="app-conflict-1",
        user_id="test-tz-user-1",
        company_name="Acme Corp",
        job_title="Platform Engineer",
        status="INTERVIEW",
    )
    db_session.add(app_rec)
    db_session.flush()

    # Create an interview plan with a round at 15:00 UTC
    plan = InterviewPlanRecord(
        id="plan-conflict-1",
        application_id="app-conflict-1",
        user_id="test-tz-user-1",
        title="Acme Interview Plan",
        company_name="Acme Corp",
        role_title="Platform Engineer",
    )
    db_session.add(plan)
    db_session.flush()

    round_event = InterviewRoundRecord(
        id="round-conflict-1",
        plan_id=plan.id,
        round_number=1,
        round_name="Architecture Round",
        scheduled_at_utc=now_utc + timedelta(hours=2),
    )
    db_session.add(round_event)
    db_session.commit()

    # Conflict check for overlapping time window (within 60 minutes)
    check = ReminderService.check_schedule_conflicts(
        db_session,
        "test-tz-user-1",
        target_time_utc=now_utc + timedelta(hours=2, minutes=15),
        duration_minutes=30,
    )

    assert check.has_conflicts is True
    assert len(check.conflicting_events) > 0
