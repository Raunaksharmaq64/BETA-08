"""
Unit Tests: Opportunity Normalization & Provenance
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

import pytest

from app.db.models import JobSourceRecord
from app.services.connectors.base import RawJobPayload
from app.services.normalization_service import NormalizationService
from contracts.sources.schemas import EmploymentType, WorkplaceType


def test_html_cleaning():
    """Strips tags, resolves entities, and standardizes spacing."""
    raw = "<div><h1>Senior Python Engineer</h1><p>We are hiring! &amp; growing fast.</p><br/><ul><li>FastAPI</li><li>PostgreSQL</li></ul></div>"
    clean = NormalizationService.clean_html(raw)

    assert "<" not in clean
    assert ">" not in clean
    assert "&amp;" not in clean
    assert "Senior Python Engineer" in clean
    assert "We are hiring! & growing fast." in clean
    assert "FastAPI" in clean


def test_dedup_key_stability():
    """Identical parameters produce identical SHA-256 keys, ignoring case and excess whitespace."""
    k1 = NormalizationService.compute_dedup_key("Stripe", "Senior Backend Engineer", "San Francisco, CA")
    k2 = NormalizationService.compute_dedup_key("stripe  ", "  Senior  Backend Engineer", "san francisco, ca ")
    k3 = NormalizationService.compute_dedup_key("Stripe", "Staff Backend Engineer", "San Francisco, CA")

    assert k1 == k2
    assert len(k1) == 64
    assert k1 != k3


def test_workplace_and_remote_classification():
    """Accurately classifies remote, hybrid, and onsite workplace modes."""
    # Remote from title
    wt1, is_r1 = NormalizationService.classify_workplace(title="Software Engineer (Remote)")
    assert wt1 == WorkplaceType.REMOTE
    assert is_r1 is True

    # Hybrid from location
    wt2, is_r2 = NormalizationService.classify_workplace(title="Product Designer", location="Austin, TX (Hybrid)")
    assert wt2 == WorkplaceType.HYBRID
    assert is_r2 is False

    # Onsite
    wt3, is_r3 = NormalizationService.classify_workplace(title="DevOps Lead", location="New York, NY (On-site)")
    assert wt3 == WorkplaceType.ON_SITE
    assert is_r3 is False

    # Explicit flag override
    wt4, is_r4 = NormalizationService.classify_workplace(title="Backend Engineer", is_remote_flag=True)
    assert wt4 == WorkplaceType.REMOTE
    assert is_r4 is True


def test_employment_type_classification():
    """Infers full-time, contract, internship types."""
    assert NormalizationService.classify_employment_type("Software Engineer Contractor") == EmploymentType.CONTRACT
    assert NormalizationService.classify_employment_type("Backend Engineering Intern") == EmploymentType.INTERNSHIP
    assert NormalizationService.classify_employment_type("Staff Machine Learning Engineer") == EmploymentType.FULL_TIME


def test_skill_extraction():
    """Extracts known technical keywords with boundary precision."""
    title = "Senior Python Engineer"
    desc = "We build high-performance APIs using FastAPI, Docker, and PostgreSQL. Familiarity with React and Kubernetes preferred."

    skills = NormalizationService.extract_skills(title, desc)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills
    assert "PostgreSQL" in skills
    assert "React" in skills
    assert "Kubernetes" in skills
    assert "Java" not in skills


def test_grounded_compensation_never_fabricated():
    """Verifies that missing compensation is recorded as None and is_salary_estimated is False."""
    dummy_source = JobSourceRecord(
        id="src-test-01",
        source_key="test-synthetic",
        display_name="Acme Corp Board",
        provider="synthetic",
        base_url="synthetic://test",
    )

    # Payload with NO compensation
    raw_job = RawJobPayload(
        external_job_id="job-no-salary",
        listing_url="https://example.com/jobs/1",
        raw_payload={
            "title": "Frontend Engineer",
            "content": "<p>Build UI components.</p>",
            "location": "Remote",
            "is_remote": True,
            "salary": None,  # No compensation
        }
    )

    norm = NormalizationService.normalize_record(raw_job, dummy_source)

    assert norm["min_salary"] is None
    assert norm["max_salary"] is None
    assert norm["is_salary_estimated"] is False  # STRICT: never fabricated!
    assert norm["company_name"] == "Acme Corp"
    assert norm["is_remote"] is True
