"""
Unit tests for RIGHT FIT Saved Searches, Saved Jobs & Alert Subscriptions
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    CanonicalOpportunityRecord,
    JobSourceRecord,
    SavedJobRecord,
    SavedSearchRecord,
    User,
)
from app.services.saved_search_service import SavedSearchService
from contracts.matching.schemas import AlertFrequency, SavedSearchCreateRequest, SavedSearchUpdateRequest


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed test user
    user = User(
        id="usr-test-1",
        email="candidate@example.com",
        password_hash="fakehash",
        full_name="Alice Candidate",
        role="CANDIDATE",
    )
    session.add(user)

    # Seed test job source & opportunity
    src = JobSourceRecord(
        id="src-1",
        source_key="greenhouse_test",
        display_name="Greenhouse Test",
        provider="greenhouse",
        base_url="https://api.greenhouse.io",
    )
    session.add(src)

    opp = CanonicalOpportunityRecord(
        id="opp-test-1",
        source_id="src-1",
        external_job_id="ext-101",
        dedup_key_sha256="hash101",
        title="Full Stack Engineer",
        company_name="Acme Inc",
        description_clean="Build web applications in React and FastAPI",
        workplace_type="REMOTE",
        is_remote=True,
        application_url="https://example.com/apply/101",
    )
    session.add(opp)
    session.commit()

    yield session
    session.close()


def test_saved_job_save_unsave_and_notes(in_memory_db):
    session = in_memory_db

    # Save job
    saved = SavedSearchService.save_job(
        session=session,
        user_id="usr-test-1",
        opportunity_id="opp-test-1",
        notes="Applied via referral",
    )
    assert saved.opportunity_id == "opp-test-1"
    assert saved.notes == "Applied via referral"

    # Save again idempotently updates note
    saved_again = SavedSearchService.save_job(
        session=session,
        user_id="usr-test-1",
        opportunity_id="opp-test-1",
        notes="Updated note: follow up next week",
    )
    assert saved_again.notes == "Updated note: follow up next week"

    # List saved jobs
    jobs = SavedSearchService.list_saved_jobs(session=session, user_id="usr-test-1")
    assert len(jobs) == 1
    assert jobs[0].opportunity.title == "Full Stack Engineer"

    # Unsave
    success = SavedSearchService.unsave_job(session=session, user_id="usr-test-1", identifier="opp-test-1")
    assert success is True
    assert len(SavedSearchService.list_saved_jobs(session=session, user_id="usr-test-1")) == 0


def test_saved_search_create_and_alerts(in_memory_db):
    session = in_memory_db

    req = SavedSearchCreateRequest(
        name="Remote FastAPI Roles",
        query="FastAPI",
        filters={"is_remote": True},
        alert_enabled=True,
        alert_frequency=AlertFrequency.DAILY,
    )

    created = SavedSearchService.create_saved_search(session=session, user_id="usr-test-1", req=req)
    assert created.name == "Remote FastAPI Roles"
    assert created.alert_enabled is True
    assert created.alert_frequency == AlertFrequency.DAILY

    # Process alerts
    logs = SavedSearchService.process_alerts(session=session)
    assert len(logs) == 1
    assert "opp-test-1" in logs[0].opportunity_ids
    assert logs[0].status == "DELIVERED"

    # Second run immediately is idempotent (no spam because last_notified_at was set)
    logs_second = SavedSearchService.process_alerts(session=session)
    assert len(logs_second) == 0

