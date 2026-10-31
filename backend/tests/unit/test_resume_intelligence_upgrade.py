"""
Unit tests for Resume Intelligence Deep Migration & Enhancement.
Verifies ResumeQualityAnalyzer, ResumeJobMatcher, ResumeAIService, and extraction extensions.
Phases: 1, 2, 3, 4, 5
"""

import pytest
from app.services.resume_quality_service import resume_quality_analyzer
from app.services.resume_job_matcher import resume_job_matcher
from app.services.resume_ai_service import resume_ai_service
from contracts.resume.schemas import ConfidenceLevel, EvidenceDTO, ReviewStatus


def test_resume_quality_analyzer_scoring():
    """Verifies multi-metric scoring across structure, impact, skills, and formatting."""
    raw_text = (
        "Jane Doe\njane@example.com\n555-123-4567\n"
        "Professional Summary: Senior backend architect specializing in distributed cloud systems.\n"
        "Experience: Senior Engineer at Acme Corp.\n"
        "- Architected high-throughput API gateway reducing p99 latency by 35% across 2M daily requests.\n"
        "- Automated database migration pipelines, saving $45k annually.\n"
        "- Responsible for internal microservices maintenance.\n"
        "Skills: Python, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, AWS, Terraform, Go, Kafka, Celery, Linux.\n"
        "Education: BS in Computer Science from Stanford University.\n"
    )

    extractions = {
        "personal_info": {"email": "jane@example.com", "phone": "555-123-4567", "linkedin_url": "https://linkedin.com/in/janedoe"},
        "summary": {"text": "Senior backend architect specializing in distributed cloud systems."},
        "experience": [
            {
                "company": "Acme Corp",
                "title": "Senior Engineer",
                "responsibilities": [
                    "Architected high-throughput API gateway reducing p99 latency by 35% across 2M daily requests.",
                    "Automated database migration pipelines, saving $45k annually.",
                    "Responsible for internal microservices maintenance."
                ]
            }
        ],
        "education": [{"institution": "Stanford University", "degree": "BS in Computer Science"}],
        "skills": {
            "languages": [{"name": "Python"}, {"name": "Go"}],
            "frameworks": [{"name": "FastAPI"}],
            "databases": [{"name": "PostgreSQL"}, {"name": "Redis"}],
            "cloud": [{"name": "AWS"}, {"name": "Docker"}, {"name": "Kubernetes"}, {"name": "Terraform"}],
            "tools": [{"name": "Kafka"}, {"name": "Celery"}, {"name": "Linux"}]
        },
        "projects": []
    }

    report = resume_quality_analyzer.analyze_quality(
        resume_id="res-1",
        version_id="ver-1",
        raw_text=raw_text,
        extractions=extractions
    )

    assert report.overall_quality_score >= 70.0
    assert report.quality_band in ("STRONG", "MODERATE")
    assert "structure" in report.section_scores
    assert "impact_quantification" in report.section_scores
    assert len(report.strengths) >= 2
    assert any("passive" in w.lower() for w in report.weaknesses)
    assert len(report.improvement_priorities) >= 1


def test_resume_job_matcher_required_vs_preferred():
    """Verifies that ResumeJobMatcher distinguishes required vs preferred skills and aligns project bullets."""
    jd_title = "Senior Distributed Systems Engineer"
    jd_description = (
        "Minimum qualifications & requirements:\n"
        "- Must have 5+ years of experience in distributed systems.\n"
        "- Strong experience with Python, FastAPI, and Kubernetes.\n"
        "- Proficiency with PostgreSQL and Redis caching.\n\n"
        "Preferred qualifications:\n"
        "- Experience with Go, Kafka, and Terraform is a plus.\n"
    )

    resume_text = (
        "Senior Backend Engineer with 6 years experience.\n"
        "Core skills: Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes.\n"
        "Projects: Built distributed stream processor using Python and Kubernetes handling 50k events/sec.\n"
    )

    extractions = {
        "experience": [{"company": "Tech", "responsibilities": ["Maintained services", "Built microservices"]}],
        "skills": {"languages": [{"name": "Python"}], "frameworks": [{"name": "FastAPI"}]},
        "inferred_skills": [{"name": "Docker"}],
        "projects": [{"name": "Stream Engine", "description": "Built distributed stream processor using Python and Kubernetes handling 50k events/sec."}]
    }

    res = resume_job_matcher.match_resume_to_job(
        resume_id="res-1",
        version_id="ver-1",
        target_job_title=jd_title,
        target_job_description=jd_description,
        raw_resume_text=resume_text,
        extractions=extractions
    )

    assert res.overall_match_score > 50.0
    assert res.keyword_coverage_score > 0.0
    assert res.required_skills_match["match_percentage"] > 0.0
    assert "python" in [k.lower() for k in res.required_skills_match["matched"]]
    assert len(res.project_theme_alignments) >= 1
    assert res.experience_level_match["assessment"] == "MEETS_REQUIREMENT"


@pytest.mark.asyncio
async def test_resume_ai_service_deterministic_fallback():
    """Verifies that ResumeAIService generates grounded 'Before vs After' rewrites without inventing facts."""
    extractions = {
        "summary": None,  # Test missing summary suggestion
        "experience": [
            {
                "company": "BetaCorp",
                "responsibilities": [
                    "Responsible for customer onboarding workflow optimization."
                ]
            }
        ],
        "projects": [
            {"name": "Auth Service", "description": "Short description"}
        ]
    }

    res = await resume_ai_service.generate_suggestions("res-1", "ver-1", extractions)

    assert len(res.suggestions) >= 2
    summary_sug = next((s for s in res.suggestions if s.category == "SUMMARY_POLISH"), None)
    assert summary_sug is not None
    assert summary_sug.evidence_required_from_candidate

    bullet_sug = next((s for s in res.suggestions if s.category == "BULLET_REWRITE"), None)
    assert bullet_sug is not None
    assert "Spearheaded" in bullet_sug.recommended_text
    assert "[X]%" in bullet_sug.recommended_text  # Placeholders, never fabricated numbers!
    assert bullet_sug.evidence_required_from_candidate
