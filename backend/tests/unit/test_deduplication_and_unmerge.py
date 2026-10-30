"""
Unit Tests: Deduplication Engine, Tiered Matching & Reversible Unmerge
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

import pytest
from datetime import timedelta
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.db.models import (
    CanonicalOpportunityRecord,
    MergeDecisionRecord,
    OpportunitySourceMappingRecord,
    utc_now,
)
from app.services.deduplication_service import DeduplicationService
from contracts.verification.schemas import MatchTier, MergeStatus


def test_tiered_matching_tier1_exact_dedup_hash():
    """Verify identical SHA-256 deduplication hashes classify as Tier 1 Exact."""
    opp1 = CanonicalOpportunityRecord(
        id="opp-1",
        title="Full Stack Engineer",
        company_name="Stripe",
        external_job_id="stripe-100",
        dedup_key_sha256="hash_exact_match_999",
    )
    opp2 = CanonicalOpportunityRecord(
        id="opp-2",
        title="Full Stack Engineer - Core",
        company_name="Stripe",
        external_job_id="stripe-100",
        dedup_key_sha256="hash_exact_match_999",
    )

    tier, score, evidence, method = DeduplicationService.compare_opportunities(opp1, opp2)
    assert tier == MatchTier.TIER_1_EXACT
    assert score == 1.0
    assert method == "EXACT_DEDUP_KEY_MATCH"


def test_tiered_matching_tier2_strong_multi_attribute():
    """Verify same company, normalized title, location and close dates classify as Tier 2 Strong."""
    now = utc_now()
    opp1 = CanonicalOpportunityRecord(
        id="opp-1",
        title="Senior Python Backend Engineer",
        company_name="Datadog",
        city="New York",
        state="NY",
        country="USA",
        is_remote=False,
        dedup_key_sha256="hash_a",
        source_published_at=now - timedelta(days=2),
    )
    opp2 = CanonicalOpportunityRecord(
        id="opp-2",
        title="Senior Python Backend Engineer",
        company_name="Datadog",
        city="New York",
        state="NY",
        country="USA",
        is_remote=False,
        dedup_key_sha256="hash_b",
        source_published_at=now - timedelta(days=8),
    )

    tier, score, evidence, method = DeduplicationService.compare_opportunities(opp1, opp2)
    assert tier == MatchTier.TIER_2_STRONG
    assert score >= 0.95
    assert method == "STRONG_MULTI_ATTRIBUTE_MATCH"


def test_tiered_matching_tier4_distinct_companies():
    """Verify opportunities from distinct companies classify as Tier 4 Distinct."""
    opp1 = CanonicalOpportunityRecord(
        id="opp-1",
        title="Staff Software Engineer",
        company_name="Google",
        dedup_key_sha256="hash_g",
    )
    opp2 = CanonicalOpportunityRecord(
        id="opp-2",
        title="Staff Software Engineer",
        company_name="Meta",
        dedup_key_sha256="hash_m",
    )

    tier, score, evidence, method = DeduplicationService.compare_opportunities(opp1, opp2)
    assert tier == MatchTier.TIER_4_DISTINCT
    assert score == 0.0


def test_merge_and_unmerge_reversibility():
    """Verify merge suppresses duplicate and repoints mappings, while unmerge cleanly reverses all changes."""
    db = MagicMock(spec=Session)

    primary = CanonicalOpportunityRecord(
        id="prim-1",
        title="Senior ML Engineer",
        company_name="Scale AI",
        is_suppressed=False,
    )
    duplicate = CanonicalOpportunityRecord(
        id="dup-1",
        title="Senior ML Engineer - San Francisco",
        company_name="Scale AI",
        is_suppressed=False,
        verification_status="OPEN_CONFIRMED",
    )

    mapping = OpportunitySourceMappingRecord(
        id="map-1",
        canonical_opportunity_id="dup-1",
        source_id="src-1",
        external_job_id="job-scale-1",
        original_url="https://scale.com/careers/1",
    )

    # Setup mock behavior
    def mock_get(model, pk):
        if pk == "prim-1":
            return primary
        if pk == "dup-1":
            return duplicate
        if pk == "map-1":
            return mapping
        return None

    db.get.side_effect = mock_get

    mock_exec = MagicMock()
    mock_exec.scalars.return_value.all.return_value = [mapping]
    db.execute.return_value = mock_exec

    # Execute merge
    decision = DeduplicationService.merge_opportunities(
        db=db,
        primary_id="prim-1",
        duplicate_ids=["dup-1"],
        actor_id="admin@rightfit.ai",
        reason="Verified cross-board duplicate posting",
    )

    assert duplicate.is_suppressed is True
    assert mapping.canonical_opportunity_id == "prim-1"
    assert decision.status == MergeStatus.CONFIRMED.value
    assert "previous_state" in decision.evidence_json

    # Execute unmerge
    def mock_get_unmerge(model, pk):
        if pk == decision.id:
            return decision
        if pk == "dup-1":
            return duplicate
        if pk == "map-1":
            return mapping
        return None

    db.get.side_effect = mock_get_unmerge

    unmerged = DeduplicationService.unmerge_opportunities(
        db=db,
        decision_id=decision.id,
        actor_id="admin@rightfit.ai",
        reason="Mistaken merge; distinct office locations",
    )

    assert unmerged.status == MergeStatus.UNMERGED.value
    assert duplicate.is_suppressed is False
    assert mapping.canonical_opportunity_id == "dup-1"
    assert unmerged.unmerged_at is not None

