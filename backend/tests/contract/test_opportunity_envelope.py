"""
Contract Tests: Canonical Opportunity Envelope and Typed Payloads
Version: 1.0.0
"""

import pytest
from pydantic import ValidationError

from contracts.opportunities.models import (
    EvidenceItem,
    FreelanceOpportunityPayload,
    JobOpportunityPayload,
    LocationInfo,
    OpportunityEnvelope,
    OpportunityType,
    OrganizationInfo,
    RemoteType,
    SourceProvenance,
    StartupProblemPayload,
    StatusInfo,
    VerificationStatus,
)


def create_base_envelope_kwargs():
    return {
        "opportunity_id": "opp-test-123",
        "title": "Senior Python Backend Engineer",
        "description": "Building high-performance microservices and AI agent gateways.",
        "organization": OrganizationInfo(name="Acme Corp", website="https://acme.example.com"),
        "location": LocationInfo(city="San Francisco", state="CA", country="USA", remote_type=RemoteType.HYBRID),
        "source": SourceProvenance(provider="greenhouse", original_url="https://jobs.acme.example.com/123"),
        "status": StatusInfo(value=VerificationStatus.VERIFIED),
        "evidence": [
            EvidenceItem(
                source_url="https://jobs.acme.example.com/123",
                excerpt="Looking for 5+ years with FastAPI and PostgreSQL.",
            )
        ],
    }


def test_job_opportunity_envelope_valid():
    """Verifies that a JOB opportunity envelope validates and serializes correctly."""
    job_payload = JobOpportunityPayload(
        salary_min=140000,
        salary_max=180000,
        salary_currency="USD",
        fit_score=0.92,
        matched_skills=["Python", "FastAPI", "PostgreSQL"],
        missing_skills=["Kubernetes"],
        ats_provider="greenhouse",
        application_url="https://jobs.acme.example.com/apply/123",
    )

    envelope = OpportunityEnvelope(
        **create_base_envelope_kwargs(),
        opportunity_type=OpportunityType.JOB,
        payload=job_payload,
    )

    assert envelope.opportunity_id == "opp-test-123"
    assert envelope.opportunity_type == OpportunityType.JOB
    assert isinstance(envelope.payload, JobOpportunityPayload)
    assert envelope.payload.fit_score == 0.92
    assert envelope.location.remote_type == RemoteType.HYBRID

    # Round-trip JSON serialization
    serialized = envelope.model_dump(mode="json")
    deserialized = OpportunityEnvelope.model_validate(serialized)
    assert deserialized.opportunity_id == envelope.opportunity_id
    assert isinstance(deserialized.payload, JobOpportunityPayload)


def test_freelance_opportunity_envelope_valid():
    """Verifies that a FREELANCE opportunity envelope validates correctly."""
    kwargs = create_base_envelope_kwargs()
    kwargs["title"] = "Local Dental Clinic Website Redesign"
    kwargs["description"] = "Website broken on mobile and lacks SSL."
    kwargs["source"] = SourceProvenance(provider="leadhunter_crawler", original_url="https://bhopaldental.example.com")

    freelance_payload = FreelanceOpportunityPayload(
        business_category="Dental Clinic",
        website_url="https://bhopaldental.example.com",
        is_broken_website=True,
        audit_status="COMPLETED",
        detected_issues=["SSL Certificate Expired", "Mobile Viewport Broken"],
        suggested_pitch="Hi Dr. Sharma, I noticed your appointment page fails on smartphones...",
        contact_email="contact@bhopaldental.example.com",
        contact_phone="+91-9876543210",
    )

    envelope = OpportunityEnvelope(
        **kwargs,
        opportunity_type=OpportunityType.FREELANCE,
        payload=freelance_payload,
    )

    assert envelope.opportunity_type == OpportunityType.FREELANCE
    assert isinstance(envelope.payload, FreelanceOpportunityPayload)
    assert envelope.payload.is_broken_website is True
    assert len(envelope.payload.detected_issues) == 2


def test_startup_problem_envelope_valid():
    """Verifies that a STARTUP_PROBLEM opportunity envelope validates correctly."""
    kwargs = create_base_envelope_kwargs()
    kwargs["title"] = "Postgres Query Latency Bottleneck under High Concurrency"
    kwargs["description"] = "Founder reporting connection pooling timeouts in production."
    kwargs["source"] = SourceProvenance(provider="reddit_saas", original_url="https://reddit.com/r/saas/comments/xyz123")

    startup_payload = StartupProblemPayload(
        target_startup="DataPulse",
        pain_point_summary="Database connection pool exhausts when batch sync runs.",
        problem_category="Database",
        community_source="Reddit r/saas",
        author="u/saas_founder_42",
        tech_stack_detected=["PostgreSQL", "FastAPI", "SQLAlchemy"],
        urgency_score=9,
        recommended_solution="Introduce PgBouncer connection pooling and add composite index on tenant_id.",
    )

    envelope = OpportunityEnvelope(
        **kwargs,
        opportunity_type=OpportunityType.STARTUP_PROBLEM,
        payload=startup_payload,
    )

    assert envelope.opportunity_type == OpportunityType.STARTUP_PROBLEM
    assert isinstance(envelope.payload, StartupProblemPayload)
    assert envelope.payload.urgency_score == 9
    assert envelope.payload.target_startup == "DataPulse"


def test_payload_mismatch_raises_validation_error():
    """Enforces that opportunity_type and payload type mismatch raises ValidationError."""
    job_payload = JobOpportunityPayload(
        ats_provider="lever",
        application_url="https://jobs.example.com",
    )

    # Type is FREELANCE but payload is JobOpportunityPayload
    with pytest.raises(ValidationError) as exc_info:
        OpportunityEnvelope(
            **create_base_envelope_kwargs(),
            opportunity_type=OpportunityType.FREELANCE,
            payload=job_payload,
        )
    assert "Payload must be of type FreelanceOpportunityPayload" in str(exc_info.value)

    # Type is STARTUP_PROBLEM but payload is JobOpportunityPayload
    with pytest.raises(ValidationError) as exc_info:
        OpportunityEnvelope(
            **create_base_envelope_kwargs(),
            opportunity_type=OpportunityType.STARTUP_PROBLEM,
            payload=job_payload,
        )
    assert "Payload must be of type StartupProblemPayload" in str(exc_info.value)


def test_fit_score_bounds_validation():
    """Verifies that fit_score must be between 0.0 and 1.0."""
    with pytest.raises(ValidationError):
        JobOpportunityPayload(
            fit_score=1.5,  # Exceeds max 1.0
            ats_provider="greenhouse",
            application_url="https://jobs.example.com",
        )

    with pytest.raises(ValidationError):
        JobOpportunityPayload(
            fit_score=-0.1,  # Below min 0.0
            ats_provider="greenhouse",
            application_url="https://jobs.example.com",
        )


def test_freelance_and_startup_payload_personalized_fit_fields():
    """Verifies that Freelance and Startup problem payloads support personalized candidate fit metadata."""
    freelance_payload = FreelanceOpportunityPayload(
        business_category="Marketing Agency",
        website_url="https://growthagency.example.com",
        fit_score=0.88,
        matched_skills=["SEO", "Content Marketing"],
        missing_skills=["HubSpot CRM"],
    )
    assert freelance_payload.fit_score == 0.88
    assert freelance_payload.matched_skills == ["SEO", "Content Marketing"]
    assert freelance_payload.missing_skills == ["HubSpot CRM"]

    startup_payload = StartupProblemPayload(
        target_startup="OmniFlow Growth",
        pain_point_summary="GA4 Multi-touch attribution tracking failure",
        problem_category="Marketing",
        community_source="Reddit",
        fit_score=0.94,
        matched_skills=["Google Analytics", "Data Tracking"],
        missing_skills=["Mixpanel"],
    )
    assert startup_payload.fit_score == 0.94
    assert startup_payload.matched_skills == ["Google Analytics", "Data Tracking"]
    assert startup_payload.missing_skills == ["Mixpanel"]


