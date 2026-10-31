"""
Unit tests for Phase 3: Enhanced Quality & ATS Analysis.
Verifies ATS Keyword Coverage Scorer and Resume Bullet Impact Scorer.
Phase: 3
"""

import pytest
from app.services.ats_service import (
    ATSAnalysisService,
    ats_service,
    _STOPWORDS,
    _ACTION_VERBS,
)
from app.services.resume_quality_service import resume_quality_analyzer


def test_keyword_extraction_and_comprehensive_stopword_filtering():
    """Verifies that generic words (team, work, experience, required) are filtered out."""
    jd_text = (
        "We are seeking an experienced candidate for our dynamic team. "
        "The role requires strong skills in Python, FastAPI, Docker, and Kubernetes. "
        "The applicant must have years of experience with PostgreSQL and Redis."
    )
    tokens = ats_service.tokenize(jd_text)

    # Generic words must be filtered
    for stopword in ["seeking", "experienced", "candidate", "dynamic", "team", "role", "requires", "skills", "applicant", "must", "years", "experience"]:
        assert stopword not in tokens

    # High-signal technical keywords must remain
    assert "python" in tokens
    assert "fastapi" in tokens
    assert "docker" in tokens
    assert "kubernetes" in tokens
    assert "postgresql" in tokens
    assert "redis" in tokens


def test_first_seen_tie_breaking_order():
    """Verifies that keywords with identical frequencies break ties using their first-seen position."""
    # 'golang', 'rust', 'python' each appear once in that exact order
    jd_text = "Golang Rust Python"
    keywords = ats_service.extract_job_keywords(jd_text, top_k=3)

    assert keywords == ["golang", "rust", "python"]

    # When 'python' appears twice, it should lead, followed by first-seen 'golang' then 'rust'
    jd_text_2 = "Golang Rust Python Python"
    keywords_2 = ats_service.extract_job_keywords(jd_text_2, top_k=3)
    assert keywords_2 == ["python", "golang", "rust"]


def test_required_vs_preferred_keyword_classification():
    """Verifies segregation of required vs preferred qualifications in JD."""
    jd_text = (
        "Basic & Required Qualifications:\n"
        "- Strong proficiency in Python, FastAPI, and PostgreSQL.\n"
        "- Experience with Docker and Linux.\n\n"
        "Preferred Qualifications:\n"
        "- Knowledge of Kafka, Kubernetes, and AWS is a plus.\n"
    )

    resume_text = (
        "Backend developer with expertise in Python, FastAPI, and Docker. "
        "Built microservices with PostgreSQL on Linux."
    )

    outcome = ats_service.score_keyword_coverage(resume_text, jd_text, top_k=15)

    assert len(outcome.required_keywords) > 0
    assert len(outcome.preferred_keywords) > 0

    # Required: python, fastapi, postgresql, docker, linux
    for req in ["python", "fastapi", "docker"]:
        assert req in outcome.required_matched

    # Preferred: kafka, kubernetes, aws
    assert "kafka" in outcome.preferred_missing
    assert outcome.keyword_relevance["python"] == "REQUIRED"
    assert outcome.keyword_relevance["kafka"] == "PREFERRED"


def test_bullet_impact_strong_band():
    """Bullets with strong action verbs and quantified metrics (%, $, scale) land in STRONG band."""
    strong_bullets = [
        "Architected distributed event pipeline cutting p99 latency by 45% across 2M daily requests.",
        "Led cross-functional migration to PostgreSQL, saving $120k annually with zero downtime.",
        "Scaled caching infrastructure 5x to support 50k peak concurrent users.",
    ]

    for bullet in strong_bullets:
        item = ats_service.evaluate_bullet(bullet)
        assert item.impact_band == "STRONG"
        assert item.score >= 0.70
        assert len(item.detected_action_verbs) > 0
        assert len(item.quantifiable_evidence) > 0
        assert "Strong bullet" in item.explanation


def test_bullet_impact_moderate_band_contextual_complexity():
    """
    Do not assume a bullet without numbers is automatically weak.
    Technical complexity + action verbs achieve MODERATE band.
    """
    technical_qualitative_bullet = (
        "Refactored monolithic authentication service into distributed OAuth2 and OIDC microservices."
    )
    item = ats_service.evaluate_bullet(technical_qualitative_bullet)

    assert item.impact_band == "MODERATE"
    assert item.score >= 0.35
    assert not item.has_passive_phrase
    assert "refactored" in item.detected_action_verbs
    assert "Moderate bullet" in item.explanation
    assert "quantifiable" in item.improvement_opportunity.lower()


def test_bullet_impact_weak_band_passive_phrases():
    """Bullets with passive verbs ('responsible for', 'helped with') land in WEAK band."""
    weak_bullets = [
        "Responsible for handling internal database tickets and helping the team.",
        "Assisted in daily software bug fixes and participated in meetings.",
    ]

    for bullet in weak_bullets:
        item = ats_service.evaluate_bullet(bullet)
        assert item.impact_band == "WEAK"
        assert item.score < 0.35
        assert item.has_passive_phrase
        assert "Weak bullet" in item.explanation
        assert "active power verbs" in item.improvement_opportunity


def test_empty_and_malformed_job_descriptions():
    """Verifies that empty, whitespace, or punctuation-only JDs return safe zero-coverage outcomes."""
    for empty_input in [None, "", "   ", ".,;:!?---"]:
        outcome = ats_service.score_keyword_coverage("Python FastAPI developer", empty_input)
        assert outcome.coverage_score == 0.0
        assert outcome.jd_keywords == []
        assert outcome.present_keywords == []
        assert outcome.missing_keywords == []


def test_separation_of_quality_index_ats_coverage_and_bullet_impact():
    """
    Verifies that Resume Quality Index, ATS Keyword Coverage, and Bullet Impact
    remain distinct, explainable metrics without misleading aggregation.
    """
    resume_text = (
        "Jane Doe\njane@example.com\n555-0199\n"
        "Summary: Senior Python engineer.\n"
        "Experience: Acme Corp.\n"
        "- Architected high-throughput API reducing latency by 35%.\n"
        "- Responsible for internal microservices maintenance.\n"
        "Skills: Python, FastAPI, Docker, PostgreSQL.\n"
        "Education: BS in Computer Science.\n"
    )

    jd_text = "Required: Python, FastAPI, Docker, Kubernetes, Kafka, Redis."

    extractions = {
        "personal_info": {"email": "jane@example.com", "phone": "555-0199"},
        "summary": {"text": "Senior Python engineer."},
        "experience": [{
            "company": "Acme Corp",
            "responsibilities": [
                "Architected high-throughput API reducing latency by 35%.",
                "Responsible for internal microservices maintenance."
            ]
        }],
        "education": [{"institution": "Univ", "degree": "BS"}],
        "skills": {"languages": [{"name": "Python"}], "frameworks": [{"name": "FastAPI"}]},
        "projects": []
    }

    # 1. Independent Resume Quality Report
    quality_report = resume_quality_analyzer.analyze_quality(
        resume_id="res-1",
        version_id="ver-1",
        raw_text=resume_text,
        extractions=extractions
    )

    # 2. Independent ATS Keyword Coverage & Bullet Impact Analysis
    ats_result = ats_service.analyze_resume_for_ats(
        resume_text=resume_text,
        job_title="Senior Python Backend Engineer",
        job_description=jd_text,
        bullets=[
            "Architected high-throughput API reducing latency by 35%.",
            "Responsible for internal microservices maintenance."
        ],
        extractions=extractions
    )

    # Verify they are separate:
    # Quality Index is general health (0-100)
    assert 0.0 <= quality_report.overall_quality_score <= 100.0
    # ATS coverage is target JD match ratio (0.0 to 1.0)
    assert 0.0 <= ats_result["coverage_score"] <= 1.0
    # Bullet impact is quantified bullet percentage (0 to 100)
    assert 0.0 <= ats_result["bullet_impact_score"] <= 100.0

    # Ensure detailed rankings and explanations are present
    assert len(ats_result["keyword_rankings"]) > 0
    assert ats_result["total_relevant_keywords"] > 0
    assert "methodology_and_limitations" in ats_result
