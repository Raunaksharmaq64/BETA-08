"""
Unit tests for RIGHT FIT Evidence-Based Skill Fit Engine
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

import pytest
from app.services.matching_service import MatchingService, normalize_skill


def test_normalize_skill_aliases():
    assert normalize_skill("Py") == "python"
    assert normalize_skill("TypeScript") == "typescript"
    assert normalize_skill("ts") == "typescript"
    assert normalize_skill("React.js") == "react"
    assert normalize_skill("reactjs") == "react"
    assert normalize_skill("K8s") == "kubernetes"
    assert normalize_skill("postgres") == "postgresql"
    assert normalize_skill("golang") == "go"


def test_compute_skill_fit_exact_and_alias_matches():
    candidate_skills = [
        {"skill_name": "Python", "provenance": "RESUME_EXTRACTION", "is_confirmed": True, "years_experience": 4.0},
        {"skill_name": "FastAPI", "provenance": "PROFILE_SKILL", "is_confirmed": True, "years_experience": 3.0},
        {"skill_name": "postgres", "provenance": "RESUME_EXTRACTION", "is_confirmed": True, "years_experience": 3.0},
        {"skill_name": "k8s", "provenance": "RESUME_EXTRACTION", "is_confirmed": False, "years_experience": 1.0},
    ]

    job_required = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    job_preferred = ["Kubernetes", "AWS"]

    breakdown = MatchingService.compute_skill_fit(
        candidate_skills=candidate_skills,
        job_required_skills=job_required,
        job_preferred_skills=job_preferred,
    )

    # 3 of 4 required matched (Python, FastAPI, PostgreSQL)
    assert set(breakdown.matched_required_skills) == {"Python", "FastAPI", "PostgreSQL"}
    assert breakdown.missing_required_skills == ["Docker"]
    assert breakdown.matched_required_count == 3
    assert breakdown.total_required_skills == 4

    # 1 of 2 preferred matched (Kubernetes via k8s alias)
    assert breakdown.matched_preferred_skills == ["Kubernetes"]
    assert breakdown.missing_preferred_skills == ["AWS"]

    # Kubernetes was unconfirmed in candidate profile
    assert "Kubernetes" in breakdown.unconfirmed_skills

    # Fit score calculation: (3/4 * 80) + (1/2 * 20) = 60 + 10 = 70.0
    assert breakdown.fit_score == 70.0


def test_compute_skill_fit_no_hallucinations_or_invented_skills():
    candidate_skills = [
        {"skill_name": "HTML"},
        {"skill_name": "CSS"},
    ]
    job_required = ["Rust", "Solidity"]

    breakdown = MatchingService.compute_skill_fit(
        candidate_skills=candidate_skills,
        job_required_skills=job_required,
    )

    assert breakdown.matched_required_count == 0
    assert len(breakdown.matched_required_skills) == 0
    assert set(breakdown.missing_required_skills) == {"Rust", "Solidity"}
    assert breakdown.fit_score == 0.0


def test_compute_skill_fit_with_resume_evidence_excerpts():
    candidate_skills = [
        {"skill_name": "Python", "provenance": "RESUME_EXTRACTION", "is_confirmed": True},
    ]
    evidence = [
        {
            "field_name": "skills",
            "extracted_value": "Python",
            "excerpt": "Engineered high-throughput data pipelines in Python and FastAPI.",
        }
    ]

    breakdown = MatchingService.compute_skill_fit(
        candidate_skills=candidate_skills,
        job_required_skills=["Python"],
        resume_evidence=evidence,
    )

    assert breakdown.fit_score == 100.0
    assert len(breakdown.skill_evidence) == 1
    ev_item = breakdown.skill_evidence[0]
    assert ev_item.skill == "Python"
    assert ev_item.evidence_excerpt == "Engineered high-throughput data pipelines in Python and FastAPI."

