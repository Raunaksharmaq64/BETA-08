"""
RIGHT FIT Core — Candidate Skill Intelligence & Taxonomy Unit Tests
Master Implementation: Candidate Confirmation, Evidence Provenance & Taxonomy Matching
"""

import pytest
from contracts.matching.schemas import EligibilityStatus
from app.services.matching_service import (
    MatchingService,
    normalize_skill,
    SKILL_ALIASES,
    SKILL_RELATIONSHIPS,
)


def test_skill_normalization_and_aliases():
    """Verifies that skill names are canonicalized and common abbreviations resolve."""
    assert normalize_skill("JS") == "javascript"
    assert normalize_skill("TypeScript  ") == "typescript"
    assert normalize_skill("Postgres") == "postgresql"
    assert normalize_skill("k8s") == "kubernetes"
    assert normalize_skill("Next.js") == "next.js"
    assert normalize_skill("React.js") == "react"


def test_evidence_based_exact_and_related_matching():
    """
    Verifies that candidates matching exact skills receive 1.0 weight,
    and candidates matching related/transferable taxonomy skills receive partial credit.
    """
    candidate_skills = [
        {
            "skill_name": "Python",
            "proficiency": "Advanced",
            "years_experience": 4.0,
            "provenance": "RESUME_WORK_EXPERIENCE",
            "is_confirmed": True,
        },
        {
            "skill_name": "JavaScript",
            "proficiency": "Intermediate",
            "years_experience": 3.0,
            "provenance": "RESUME_PROJECTS",
            "is_confirmed": True,
        },
        {
            "skill_name": "Docker",
            "proficiency": "Intermediate",
            "years_experience": 2.0,
            "provenance": "USER_ENTERED",
            "is_confirmed": True,
        },
    ]

    # Job requires FastAPI (Python related/parent-child) and TypeScript (JavaScript transferable)
    job_required = ["FastAPI", "TypeScript"]
    job_preferred = ["Docker"]

    breakdown = MatchingService.compute_skill_fit(
        candidate_skills=candidate_skills,
        job_required_skills=job_required,
        job_preferred_skills=job_preferred,
    )

    # Candidate has Docker exactly matched in preferred
    assert "Docker" in breakdown.matched_preferred_skills
    assert breakdown.matched_preferred_count == 1

    # Candidate has related skills for FastAPI (via Python) and TypeScript (via JavaScript)
    assert len(breakdown.related_required_skills) == 2
    req_names = {r["required_skill"] for r in breakdown.related_required_skills}
    assert "FastAPI" in req_names
    assert "TypeScript" in req_names

    # Relationship strengths should be > 0.8
    for rel in breakdown.related_required_skills:
        assert rel["relationship_strength"] >= 0.80
        assert "transfers to required" in rel["explanation"]

    # Fit score should reflect partial credit rather than zero or 100%
    assert 50.0 < breakdown.fit_score < 100.0


def test_missing_mandatory_skills_and_unconfirmed():
    """Verifies that missing required skills and unconfirmed skills are cleanly segregated."""
    candidate_skills = [
        {
            "skill_name": "Python",
            "is_confirmed": True,
        },
        {
            "skill_name": "Rust",
            "is_confirmed": False,  # AI-extracted pending candidate confirmation
        },
    ]

    job_required = ["Python", "Rust", "C++"]

    breakdown = MatchingService.compute_skill_fit(
        candidate_skills=candidate_skills,
        job_required_skills=job_required,
    )

    assert "Python" in breakdown.matched_required_skills
    assert "Rust" in breakdown.unconfirmed_skills
    assert "C++" in breakdown.missing_required_skills


def test_configurable_ranking_formula():
    """Verifies Section 6.3 configurable scoring components formula."""
    # 1. Standard weights: Skill (40%), Role (20%), Exp (15%), Pref (15%), Freshness (10%)
    score = MatchingService.calculate_ranking_score(
        skill_fit_score=90.0,
        eligibility_status=EligibilityStatus.MEETS_REQUIREMENTS,
        verification_status="OPEN_CONFIRMED",
        freshness_state="FRESH",
        preference_alignment_score=100.0,
        role_relevance_score=90.0,
        experience_fit_score=85.0,
    )

    # Expected: 90*0.4 + 90*0.2 + 85*0.15 + 100*0.15 + 100*0.10
    # = 36 + 18 + 12.75 + 15 + 10 = 91.75
    assert 90.0 <= score <= 93.0

    # 2. Custom configurable weights
    custom_weights = {
        "skill": 0.60,
        "role": 0.10,
        "experience": 0.10,
        "preference": 0.10,
        "freshness": 0.10,
    }
    custom_score = MatchingService.calculate_ranking_score(
        skill_fit_score=90.0,
        eligibility_status=EligibilityStatus.MEETS_REQUIREMENTS,
        verification_status="OPEN_CONFIRMED",
        freshness_state="FRESH",
        preference_alignment_score=100.0,
        role_relevance_score=90.0,
        experience_fit_score=85.0,
        weights=custom_weights,
    )
    # Expected: 90*0.6 + 90*0.1 + 85*0.1 + 100*0.1 + 100*0.1 = 54 + 9 + 8.5 + 10 + 10 = 91.5
    assert 90.0 <= custom_score <= 93.0

