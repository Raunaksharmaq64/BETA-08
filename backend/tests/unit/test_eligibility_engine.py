"""
Unit tests for RIGHT FIT Mandatory Eligibility Engine
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

import pytest
from contracts.matching.schemas import CriterionEvaluationStatus, EligibilityStatus
from app.services.matching_service import MatchingService


def test_missing_candidate_profile_returns_unknown_never_false_rejection():
    # Empty profile
    opp = {
        "title": "Senior Backend Engineer",
        "description_clean": "Requires 5+ years of experience and Bachelor's degree.",
        "workplace_type": "REMOTE",
        "is_remote": True,
    }

    breakdown = MatchingService.evaluate_eligibility(
        candidate_profile=None,
        opportunity=opp,
    )

    assert breakdown.status == EligibilityStatus.UNKNOWN
    assert breakdown.has_missing_candidate_data is True
    assert "Profile Data Availability" in breakdown.criteria[0].criterion_name


def test_missing_experience_and_education_evaluates_to_unknown():
    # Candidate has location but no experience or education records
    cand_profile = {
        "city": "Austin",
        "country": "United States",
        "experience": [],
        "education": [],
    }

    opp = {
        "title": "Senior Backend Engineer",
        "description_clean": "Must have 5+ years experience and Bachelor's in CS.",
        "workplace_type": "REMOTE",
        "is_remote": True,
    }

    breakdown = MatchingService.evaluate_eligibility(
        candidate_profile=cand_profile,
        opportunity=opp,
    )

    # Must be UNKNOWN (not DOES_NOT_MEET) because candidate hasn't entered experience/education
    assert breakdown.status == EligibilityStatus.UNKNOWN
    assert breakdown.has_missing_candidate_data is True

    # Check criteria
    exp_crit = next(c for c in breakdown.criteria if c.criterion_name == "Minimum Experience")
    assert exp_crit.status == CriterionEvaluationStatus.UNKNOWN


def test_satisfied_all_criteria_returns_meets_requirements():
    cand_profile = {
        "city": "New York",
        "country": "United States",
        "experience": [
            {"company": "Tech Corp", "role": "Backend Eng", "years_experience": 3.0},
            {"company": "StartUp", "role": "Senior Eng", "years_experience": 3.0},
        ],
        "education": [
            {"institution": "NYU", "degree": "Bachelor of Science", "field_of_study": "Computer Science"}
        ],
    }

    opp = {
        "title": "Senior Python Developer",
        "description_clean": "Looking for candidate with 5+ years experience and Bachelor's degree.",
        "workplace_type": "REMOTE",
        "is_remote": True,
    }

    breakdown = MatchingService.evaluate_eligibility(
        candidate_profile=cand_profile,
        opportunity=opp,
    )

    assert breakdown.status == EligibilityStatus.MEETS_REQUIREMENTS
    assert breakdown.has_missing_candidate_data is False


def test_unsatisfied_location_returns_does_not_meet():
    cand_profile = {
        "city": "London",
        "country": "United Kingdom",
        "experience": [{"company": "A", "role": "Dev", "years_experience": 6.0}],
        "education": [{"degree": "Bachelor of Science"}],
    }

    opp = {
        "title": "On-site Engineer",
        "description_clean": "Requires working in-office.",
        "workplace_type": "ON_SITE",
        "is_remote": False,
        "city": "Tokyo",
        "country": "Japan",
    }

    breakdown = MatchingService.evaluate_eligibility(
        candidate_profile=cand_profile,
        opportunity=opp,
    )

    assert breakdown.status == EligibilityStatus.DOES_NOT_MEET_REQUIREMENTS
    loc_crit = next(c for c in breakdown.criteria if c.criterion_name == "Geographic Location")
    assert loc_crit.status == CriterionEvaluationStatus.NOT_SATISFIED

