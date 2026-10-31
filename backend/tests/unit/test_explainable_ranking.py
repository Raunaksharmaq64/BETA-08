"""
Unit tests for RIGHT FIT Transparent Multi-Dimensional Ranking
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery
"""

import pytest
from contracts.matching.schemas import EligibilityStatus
from app.services.matching_service import MatchingService


def test_ranking_score_deterministic_calculation():
    # 100% skill fit (40 pts) + MEETS (25 pts) + OPEN_CONFIRMED (15 pts) + FRESH (10 pts) + 100% pref (10 pts)
    score_perfect = MatchingService.calculate_ranking_score(
        skill_fit_score=100.0,
        eligibility_status=EligibilityStatus.MEETS_REQUIREMENTS,
        verification_status="OPEN_CONFIRMED",
        freshness_state="FRESH",
        preference_alignment_score=100.0,
    )
    assert score_perfect == 100.0

    # 50% skill fit (20 pts) + UNKNOWN elig (15 pts) + UNVERIFIED (8 pts) + RECENT (7 pts) + 50% pref (5 pts) = 55.0
    score_mid = MatchingService.calculate_ranking_score(
        skill_fit_score=50.0,
        eligibility_status=EligibilityStatus.UNKNOWN,
        verification_status="UNVERIFIED",
        freshness_state="RECENT",
        preference_alignment_score=50.0,
    )
    assert score_mid == 55.0

    # 0% skill fit + DOES NOT MEET + CLOSED_CONFIRMED + STALE + 0% pref
    score_low = MatchingService.calculate_ranking_score(
        skill_fit_score=0.0,
        eligibility_status=EligibilityStatus.DOES_NOT_MEET_REQUIREMENTS,
        verification_status="CLOSED_CONFIRMED",
        freshness_state="STALE",
        preference_alignment_score=0.0,
    )
    # 0 + 0 + 0 + 2 (STALE freshness) + 0 = 2.0
    assert score_low == 2.0


def test_ranking_relative_ordering():
    # Verified fresh job with high match ranks strictly above unverified stale job with lower match
    score_high = MatchingService.calculate_ranking_score(
        skill_fit_score=90.0,
        eligibility_status=EligibilityStatus.MEETS_REQUIREMENTS,
        verification_status="OPEN_CONFIRMED",
        freshness_state="FRESH",
    )
    score_lower = MatchingService.calculate_ranking_score(
        skill_fit_score=60.0,
        eligibility_status=EligibilityStatus.UNKNOWN,
        verification_status="UNVERIFIED",
        freshness_state="STALE",
    )
    assert score_high > score_lower

