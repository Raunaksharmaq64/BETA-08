"""
Unit tests for Phase 5 — Job-Specific Resume Matching & Portfolio Alignment.
Verifies PortfolioProjectMatcher algorithm migrated from agentic-career-search
and ResumeJobMatcher multi-attribute fit scoring.
"""

import pytest
from app.services.resume_job_matcher import (
    PortfolioMatchResult,
    PortfolioProjectMatcher,
    ResumeJobMatcher,
    resume_job_matcher,
)


def test_portfolio_matcher_blank_bullets_raise():
    """Empty or whitespace-only portfolio bullets raise ValueError."""
    matcher = PortfolioProjectMatcher()
    with pytest.raises(ValueError, match="portfolio_bullets"):
        matcher.match(portfolio_bullets=[], jd_themes=["kubernetes"])
    with pytest.raises(ValueError, match="portfolio_bullets"):
        matcher.match(portfolio_bullets=["   ", ""], jd_themes=["kubernetes"])


def test_portfolio_matcher_blank_themes_raise():
    """Empty or whitespace-only JD themes raise ValueError."""
    matcher = PortfolioProjectMatcher()
    with pytest.raises(ValueError, match="jd_themes"):
        matcher.match(portfolio_bullets=["Built a Python API"], jd_themes=[])
    with pytest.raises(ValueError, match="jd_themes"):
        matcher.match(portfolio_bullets=["Built a Python API"], jd_themes=["   "])


def test_portfolio_matcher_token_overlap_and_human_review():
    """Verifies token overlap calculation and invariant requires_human_review=True."""
    matcher = PortfolioProjectMatcher()
    results = matcher.match(
        portfolio_bullets=[
            "Built scalable FastAPI microservices with Kubernetes deployments.",
            "Designed reactive React frontend dashboards for real-time telemetry.",
            "Engineered PostgreSQL database sharding and Redis caching pipelines."
        ],
        jd_themes=["Kubernetes microservices", "React telemetry", "Golang distributed systems"]
    )
    assert len(results) == 3
    theme_map = {r.jd_theme: r for r in results}

    k8s = theme_map["Kubernetes microservices"]
    assert "Built scalable FastAPI microservices with Kubernetes deployments." in k8s.matched_bullets
    assert 0.0 < k8s.score <= 1.0
    assert k8s.requires_human_review is True

    react = theme_map["React telemetry"]
    assert "Designed reactive React frontend dashboards for real-time telemetry." in react.matched_bullets
    assert 0.0 < react.score <= 1.0
    assert react.requires_human_review is True

    go = theme_map["Golang distributed systems"]
    assert len(go.matched_bullets) == 0
    assert go.score == 0.0
    assert go.requires_human_review is True


def test_portfolio_matcher_full_coverage_scores_one():
    """Bullet that covers all tokens of the theme scores exactly 1.0."""
    matcher = PortfolioProjectMatcher()
    results = matcher.match(
        portfolio_bullets=["Architected Python FastAPI microservices on AWS"],
        jd_themes=["Python FastAPI AWS"]
    )
    assert len(results) == 1
    assert results[0].score == 1.0
    assert results[0].requires_human_review is True


def test_job_matcher_required_vs_preferred_breakdown():
    """Verifies clear breakdown between hard requirements and nice-to-have skills."""
    jd_title = "Senior Python Engineer"
    jd_desc = """
    Required Qualifications:
    - 5+ years of software engineering experience in Python
    - Production experience with FastAPI, Docker, and PostgreSQL
    - Strong database optimization skills

    Preferred Qualifications:
    - Experience with Kafka message queues and Kubernetes
    - Familiarity with TypeScript and React
    """

    resume_text = """
    Jane Doe - Staff Engineer
    Skills: Python, FastAPI, Docker, PostgreSQL, Redis
    Experience: 6 years building high-load APIs and microservices.
    """

    extractions = {
        "personal_info": {"full_name": "Jane Doe"},
        "experience": [{"company": "Tech Corp", "responsibilities": ["Maintained Python and FastAPI services."]}],
        "skills": {"languages": [{"name": "Python"}], "frameworks": [{"name": "FastAPI"}]},
        "inferred_skills": [{"name": "Docker"}, {"name": "PostgreSQL"}],
        "projects": []
    }

    match_resp = resume_job_matcher.match_resume_to_job(
        resume_id="res-123",
        version_id="ver-456",
        target_job_title=jd_title,
        target_job_description=jd_desc,
        raw_resume_text=resume_text,
        extractions=extractions
    )

    # Check required skills match breakdown
    req_match = match_resp.required_skills_match
    assert req_match["target_count"] > 0
    assert "python" in [m.lower() for m in req_match["matched"]]
    assert "fastapi" in [m.lower() for m in req_match["matched"]]
    assert req_match["match_percentage"] >= 40.0

    # Check preferred skills match breakdown
    pref_match = match_resp.preferred_skills_match
    assert pref_match["target_count"] > 0
    assert "kafka" in [m.lower() for m in pref_match["missing"]]

    # Check experience level
    exp_match = match_resp.experience_level_match
    assert exp_match["required_years"] == 5.0
    assert exp_match["estimated_candidate_years"] >= 5.0
    assert exp_match["assessment"] == "MEETS_REQUIREMENT"
    assert exp_match["score"] == 100.0

    # Check overall match score
    assert 40.0 <= match_resp.overall_match_score <= 100.0


def test_job_matcher_unverified_matches_flagged():
    """Skills found in text/inferred but not explicitly in skills list are flagged as unverified."""
    jd_title = "Data Platform Engineer"
    jd_desc = "Requirements: Python, Snowflake, PySpark, Airflow"
    resume_text = "Experienced in Python and Snowflake data warehouse pipelines."

    extractions = {
        "experience": [{"company": "Data Co", "responsibilities": ["Built Snowflake pipelines."]}],
        "skills": {"languages": [{"name": "Python"}]},  # Snowflake not in explicit skills
        "inferred_skills": [{"name": "Snowflake"}],
        "projects": []
    }

    match_resp = resume_job_matcher.match_resume_to_job(
        resume_id="res-789",
        version_id="ver-012",
        target_job_title=jd_title,
        target_job_description=jd_desc,
        raw_resume_text=resume_text,
        extractions=extractions
    )

    unverified = [u.lower() for u in match_resp.unverified_matches]
    assert "snowflake" in unverified
