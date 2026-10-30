"""
Unit tests for ATSAnalysisService.
Verifies keyword coverage, bullet impact scoring, and ethical no-fabrication guidance.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

import pytest
from app.services.ats_service import ats_service


def test_tokenize_and_stopwords():
    """Verifies that common stopwords are stripped while technical terms are preserved."""
    text = "Experienced Senior Python and FastAPI Engineer with PostgreSQL and AWS knowledge."
    tokens = ats_service.tokenize(text)

    assert "python" in tokens
    assert "fastapi" in tokens
    assert "postgresql" in tokens
    assert "aws" in tokens
    # Stopwords should be stripped
    assert "and" not in tokens
    assert "with" not in tokens


def test_score_keyword_coverage():
    """Verifies coverage ratio calculation and keyword partitioning."""
    job_desc = "Looking for a Python backend engineer with FastAPI, Docker, and PostgreSQL experience."
    resume_text = "Senior Python developer with experience in FastAPI and Redis caching."

    coverage, matched, missing = ats_service.score_keyword_coverage(resume_text, job_desc)

    assert coverage > 0.0
    assert "python" in matched
    assert "fastapi" in matched
    assert "docker" in missing
    assert "postgresql" in missing


def test_bullet_impact_scoring():
    """Verifies scoring of quantified impact cues in resume bullets."""
    strong_bullets = [
        "Led team of 6 engineers to launch payment microservice, increasing revenue by 25%.",
        "Architected caching system processing 50k requests/sec, cutting latency by 40%.",
        "Automated deployment pipeline saving $50,000 annually in cloud infrastructure.",
    ]
    weak_bullets = [
        "Worked on backend tasks and attended meetings.",
        "Responsible for bug fixing and writing documentation.",
    ]

    strong_score, strong_analysis = ats_service.score_bullet_impact(strong_bullets)
    weak_score, weak_analysis = ats_service.score_bullet_impact(weak_bullets)

    assert strong_score == 100.0
    assert strong_analysis["strong_bullets_count"] == 3
    assert strong_analysis["weak_bullets_count"] == 0

    assert weak_score == 0.0
    assert weak_analysis["strong_bullets_count"] == 0
    assert weak_analysis["weak_bullets_count"] == 2


def test_no_fabrication_in_suggestions():
    """Verifies that suggestions NEVER invent metrics or claims and are strictly advisory."""
    missing_kws = ["kubernetes", "terraform", "rust"]
    bullet_analysis = {
        "scored_bullets": [
            {"bullet": "Developed backend features using Python.", "is_strong": False}
        ]
    }
    sections = {"sections": {}}

    suggestions = ats_service.generate_grounded_suggestions(
        missing_kws, bullet_analysis, sections
    )

    assert len(suggestions) >= 2
    for s in suggestions:
        assert s["is_advisory"] is True
        # Verify suggestions do NOT instruct candidate to lie
        assert "Do not add skills you have not used" in s["message"] or "Never invent" in s["message"] or "summary" in s["message"].lower()


def test_empty_job_description_handling():
    """Verifies graceful handling of empty inputs."""
    cov, matched, missing = ats_service.score_keyword_coverage("Python", "")
    assert cov == 0.0
    assert matched == []
    assert missing == []

