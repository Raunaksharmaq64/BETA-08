"""
RIGHT FIT — Opportunity Deduplication & Source Mapping Service
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

from __future__ import annotations

import difflib
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    CanonicalOpportunityRecord,
    DuplicateCandidateRecord,
    MergeDecisionRecord,
    OpportunitySourceMappingRecord,
    utc_now,
)
from contracts.verification.schemas import (
    MatchTier,
    MergeStatus,
)

logger = logging.getLogger("rightfit.deduplication")


class DeduplicationService:
    """
    Tiered deduplication engine, source mapping manager, and auditable
    reversible merge/unmerge service for canonical career opportunities.
    """

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """Standardize text for comparison by lowercasing, stripping punctuation and redundant whitespace."""
        if not text:
            return ""
        # Lowercase
        normalized = text.lower()
        # Replace non-alphanumeric with spaces
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        # Collapse multiple spaces
        return " ".join(normalized.split())

    @classmethod
    def compare_opportunities(
        cls,
        opp1: CanonicalOpportunityRecord,
        opp2: CanonicalOpportunityRecord,
    ) -> Tuple[MatchTier, float, Dict[str, Any], str]:
        """
        Compare two canonical opportunities and evaluate match tier, confidence score,
        and evidentiary reasoning.
        """
        if opp1.id == opp2.id:
            return (
                MatchTier.TIER_1_EXACT,
                1.0,
                {"reason": "Identical canonical ID"},
                "IDENTICAL_ID",
            )

        norm_title1 = cls.normalize_text(opp1.title)
        norm_title2 = cls.normalize_text(opp2.title)
        norm_comp1 = cls.normalize_text(opp1.company_name)
        norm_comp2 = cls.normalize_text(opp2.company_name)

        # 1. Tier 1: Exact requisition ID or exact SHA256 deduplication key
        if opp1.dedup_key_sha256 and opp1.dedup_key_sha256 == opp2.dedup_key_sha256:
            return (
                MatchTier.TIER_1_EXACT,
                1.0,
                {
                    "rule": "EXACT_DEDUP_KEY_HASH",
                    "dedup_key": opp1.dedup_key_sha256,
                    "company": opp1.company_name,
                },
                "EXACT_DEDUP_KEY_MATCH",
            )

        if (
            opp1.external_job_id
            and opp1.external_job_id == opp2.external_job_id
            and (norm_comp1 == norm_comp2 or norm_comp1 in norm_comp2 or norm_comp2 in norm_comp1)
        ):
            return (
                MatchTier.TIER_1_EXACT,
                1.0,
                {
                    "rule": "EXACT_REQUISITION_ID_AND_COMPANY",
                    "external_job_id": opp1.external_job_id,
                    "company1": opp1.company_name,
                    "company2": opp2.company_name,
                },
                "EXACT_REQUISITION_MATCH",
            )

        # Check company match
        comp_match = (
            norm_comp1 == norm_comp2
            or (len(norm_comp1) > 3 and norm_comp1 in norm_comp2)
            or (len(norm_comp2) > 3 and norm_comp2 in norm_comp1)
        )
        if not comp_match:
            return (
                MatchTier.TIER_4_DISTINCT,
                0.0,
                {"reason": "Different companies"},
                "DISTINCT_COMPANY",
            )

        # 2. Tier 2: Strong multi-attribute match
        # Same company + exact normalized title + location/remote alignment
        title_similarity = difflib.SequenceMatcher(None, norm_title1, norm_title2).ratio()
        
        # Location alignment check
        loc1 = cls.normalize_text(f"{opp1.city or ''} {opp1.state or ''} {opp1.country or ''}")
        loc2 = cls.normalize_text(f"{opp2.city or ''} {opp2.state or ''} {opp2.country or ''}")
        same_remote = opp1.is_remote == opp2.is_remote
        same_location = loc1 == loc2 or (opp1.is_remote and opp2.is_remote)

        # Observation timeframe proximity (within 30 days)
        date1 = opp1.source_published_at or opp1.first_seen_at
        date2 = opp2.source_published_at or opp2.first_seen_at
        days_apart = abs((date1 - date2).total_seconds()) / 86400.0 if (date1 and date2) else 0.0

        if norm_title1 == norm_title2 and (same_location or same_remote) and days_apart <= 45:
            confidence = 0.95
            if same_location and same_remote:
                confidence = 0.98
            return (
                MatchTier.TIER_2_STRONG,
                confidence,
                {
                    "rule": "STRONG_MULTI_ATTRIBUTE",
                    "title": opp1.title,
                    "company": opp1.company_name,
                    "same_location": same_location,
                    "same_remote": same_remote,
                    "days_apart": round(days_apart, 1),
                },
                "STRONG_MULTI_ATTRIBUTE_MATCH",
            )

        # 3. Tier 3: Probable cross-source match
        # High title similarity (> 0.80) or title contained within title + same company
        if title_similarity >= 0.80 or (len(norm_title1) > 5 and norm_title1 in norm_title2) or (len(norm_title2) > 5 and norm_title2 in norm_title1):
            confidence = round(0.70 + (title_similarity * 0.18), 2)
            return (
                MatchTier.TIER_3_PROBABLE,
                confidence,
                {
                    "rule": "PROBABLE_TEXT_SIMILARITY",
                    "title1": opp1.title,
                    "title2": opp2.title,
                    "title_similarity": round(title_similarity, 3),
                    "company": opp1.company_name,
                },
                "PROBABLE_TEXT_SIMILARITY",
            )

        # 4. Tier 4: Distinct
        return (
            MatchTier.TIER_4_DISTINCT,
            round(title_similarity * 0.5, 2),
            {
                "rule": "INSUFFICIENT_SIMILARITY",
                "title_similarity": round(title_similarity, 3),
            },
            "DISTINCT_RECORDS",
        )

    @classmethod
    def detect_duplicate_candidates(
        cls,
        db: Session,
        lookback_days: int = 60,
    ) -> List[DuplicateCandidateRecord]:
        """
        Scan recent unsuppressed canonical opportunities and detect candidate duplicate pairs.
        """
        since = utc_now() - timedelta(days=lookback_days)
        recent_opps = db.execute(
            select(CanonicalOpportunityRecord)
            .where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.last_seen_at >= since,
            )
            .order_by(CanonicalOpportunityRecord.first_seen_at.asc())
        ).scalars().all()

        detected: List[DuplicateCandidateRecord] = []
        n = len(recent_opps)

        for i in range(n):
            for j in range(i + 1, n):
                opp1 = recent_opps[i]
                opp2 = recent_opps[j]

                # Quick pre-filter: Company prefix match
                if not cls.normalize_text(opp1.company_name) or not cls.normalize_text(opp2.company_name):
                    continue

                tier, score, evidence, method = cls.compare_opportunities(opp1, opp2)

                if tier in (MatchTier.TIER_1_EXACT, MatchTier.TIER_2_STRONG, MatchTier.TIER_3_PROBABLE):
                    # Check if already recorded
                    existing = db.execute(
                        select(DuplicateCandidateRecord).where(
                            or_(
                                and_(
                                    DuplicateCandidateRecord.primary_opportunity_id == opp1.id,
                                    DuplicateCandidateRecord.duplicate_opportunity_id == opp2.id,
                                ),
                                and_(
                                    DuplicateCandidateRecord.primary_opportunity_id == opp2.id,
                                    DuplicateCandidateRecord.duplicate_opportunity_id == opp1.id,
                                ),
                            )
                        )
                    ).scalars().first()

                    if not existing:
                        candidate = DuplicateCandidateRecord(
                            primary_opportunity_id=opp1.id,
                            duplicate_opportunity_id=opp2.id,
                            match_tier=tier.value,
                            match_method=method,
                            confidence_score=score,
                            match_evidence_json=evidence,
                            status=MergeStatus.PROPOSED.value,
                        )
                        db.add(candidate)
                        detected.append(candidate)

        if detected:
            db.commit()
            for cand in detected:
                db.refresh(cand)

        return detected

    @classmethod
    def get_duplicate_candidates(
        cls,
        db: Session,
        status: Optional[str] = "PROPOSED",
    ) -> List[DuplicateCandidateRecord]:
        """Fetch duplicate candidate pairs with joined opportunities."""
        stmt = (
            select(DuplicateCandidateRecord)
            .options(
                joinedload(DuplicateCandidateRecord.primary_opportunity),
                joinedload(DuplicateCandidateRecord.duplicate_opportunity),
            )
            .order_by(DuplicateCandidateRecord.created_at.desc())
        )
        if status:
            stmt = stmt.where(DuplicateCandidateRecord.status == status)

        return list(db.execute(stmt).scalars().all())

    @classmethod
    def merge_opportunities(
        cls,
        db: Session,
        primary_id: str,
        duplicate_ids: List[str],
        actor_id: str,
        actor_type: str = "ADMIN",
        reason: str = "Deduplication merge",
    ) -> MergeDecisionRecord:
        """
        Merge one or more duplicate opportunities into a primary canonical opportunity.
        This operation is completely auditable and reversible.
        """
        primary = db.get(CanonicalOpportunityRecord, primary_id)
        if not primary:
            raise ValueError(f"Primary opportunity not found: {primary_id}")
        if primary.is_suppressed:
            raise ValueError(f"Cannot merge into suppressed primary opportunity: {primary_id}")

        duplicates: List[CanonicalOpportunityRecord] = []
        for dup_id in duplicate_ids:
            if dup_id == primary_id:
                continue
            dup = db.get(CanonicalOpportunityRecord, dup_id)
            if not dup:
                raise ValueError(f"Duplicate opportunity not found: {dup_id}")
            duplicates.append(dup)

        if not duplicates:
            raise ValueError("No valid duplicate opportunities provided for merge")

        # Capture snapshot of state before merge for reversibility
        previous_state: Dict[str, Any] = {
            "primary_id": primary.id,
            "duplicates": [],
        }

        reassigned_mapping_ids: List[str] = []

        for dup in duplicates:
            # Get existing source mappings for this duplicate
            mappings = db.execute(
                select(OpportunitySourceMappingRecord).where(
                    OpportunitySourceMappingRecord.canonical_opportunity_id == dup.id
                )
            ).scalars().all()

            mapping_ids = [m.id for m in mappings]
            previous_state["duplicates"].append({
                "duplicate_id": dup.id,
                "was_suppressed": dup.is_suppressed,
                "verification_status": dup.verification_status,
                "source_mapping_ids": mapping_ids,
            })

            # Suppress duplicate opportunity
            dup.is_suppressed = True

            # Repoint source mappings to primary canonical opportunity
            for mapping in mappings:
                mapping.canonical_opportunity_id = primary.id
                mapping.match_tier = MatchTier.TIER_1_EXACT.value
                mapping.match_method = "MERGE_DECISION"
                reassigned_mapping_ids.append(mapping.id)

        # Create immutable MergeDecisionRecord
        merge_decision = MergeDecisionRecord(
            canonical_opportunity_id=primary.id,
            original_opportunity_ids_json=[d.id for d in duplicates],
            match_tier=MatchTier.TIER_2_STRONG.value,
            match_method="MANUAL_ADMIN_MERGE" if actor_type == "ADMIN" else "AUTOMATED_MERGE",
            evidence_json={
                "reason": reason,
                "previous_state": previous_state,
                "reassigned_mapping_ids": reassigned_mapping_ids,
            },
            actor_type=actor_type,
            actor_id=actor_id,
            rule_version="1.0.0",
            reason=reason,
            status=MergeStatus.CONFIRMED.value,
        )
        db.add(merge_decision)
        db.flush()

        # Update merge_decision_id on reassigned mappings
        for mapping_id in reassigned_mapping_ids:
            m = db.get(OpportunitySourceMappingRecord, mapping_id)
            if m:
                m.merge_decision_id = merge_decision.id

        # Update candidate records involving these pairs to CONFIRMED
        for dup in duplicates:
            cands = db.execute(
                select(DuplicateCandidateRecord).where(
                    or_(
                        and_(
                            DuplicateCandidateRecord.primary_opportunity_id == primary.id,
                            DuplicateCandidateRecord.duplicate_opportunity_id == dup.id,
                        ),
                        and_(
                            DuplicateCandidateRecord.primary_opportunity_id == dup.id,
                            DuplicateCandidateRecord.duplicate_opportunity_id == primary.id,
                        ),
                    )
                )
            ).scalars().all()
            for cand in cands:
                cand.status = MergeStatus.CONFIRMED.value
                cand.decision_id = merge_decision.id
                cand.resolved_at = utc_now()
                cand.resolved_by = actor_id

        db.commit()
        db.refresh(merge_decision)
        logger.info(
            f"Successfully merged {len(duplicates)} duplicates into primary {primary.id}. Decision: {merge_decision.id}"
        )
        return merge_decision

    @classmethod
    def unmerge_opportunities(
        cls,
        db: Session,
        decision_id: str,
        actor_id: str,
        reason: str,
    ) -> MergeDecisionRecord:
        """
        Reverse a previous merge decision:
        - Restores is_suppressed=False on unmerged duplicates.
        - Reassigns original source mappings back to their respective opportunities.
        - Marks MergeDecisionRecord as UNMERGED with audit trail.
        """
        decision = db.get(MergeDecisionRecord, decision_id)
        if not decision:
            raise ValueError(f"Merge decision not found: {decision_id}")
        if decision.status == MergeStatus.UNMERGED.value:
            raise ValueError(f"Merge decision has already been unmerged: {decision_id}")

        evidence = decision.evidence_json or {}
        previous_state = evidence.get("previous_state", {})
        dup_states = previous_state.get("duplicates", [])

        if not dup_states:
            # Fallback using original_opportunity_ids_json
            dup_states = [{"duplicate_id": did} for did in decision.original_opportunity_ids_json]

        for item in dup_states:
            dup_id = item.get("duplicate_id")
            if not dup_id:
                continue
            dup = db.get(CanonicalOpportunityRecord, dup_id)
            if dup:
                dup.is_suppressed = item.get("was_suppressed", False)

            # Reassign source mappings back
            mapping_ids = item.get("source_mapping_ids", [])
            for mid in mapping_ids:
                mapping = db.get(OpportunitySourceMappingRecord, mid)
                if mapping:
                    mapping.canonical_opportunity_id = dup_id
                    mapping.merge_decision_id = None
                    mapping.match_method = "UNMERGE_REVERT"

        # Mark decision as UNMERGED
        decision.status = MergeStatus.UNMERGED.value
        decision.unmerged_at = utc_now()
        decision.unmerged_by = actor_id
        decision.unmerge_reason = reason

        # Update duplicate candidates back to PROPOSED
        cands = db.execute(
            select(DuplicateCandidateRecord).where(
                DuplicateCandidateRecord.decision_id == decision.id
            )
        ).scalars().all()
        for cand in cands:
            cand.status = MergeStatus.UNMERGED.value
            cand.resolved_at = utc_now()
            cand.resolved_by = actor_id

        db.commit()
        db.refresh(decision)
        logger.info(f"Successfully unmerged decision {decision.id} by actor {actor_id}")
        return decision

    @classmethod
    def create_or_update_source_mapping(
        cls,
        db: Session,
        canonical_opportunity_id: str,
        source_id: str,
        external_job_id: str,
        original_url: str,
        match_tier: MatchTier = MatchTier.TIER_1_EXACT,
        match_method: str = "EXACT_SOURCE_ID",
        confidence_score: float = 1.0,
        match_evidence: Optional[Dict[str, Any]] = None,
    ) -> OpportunitySourceMappingRecord:
        """Create or refresh an auditable OpportunitySourceMappingRecord."""
        existing = db.execute(
            select(OpportunitySourceMappingRecord).where(
                OpportunitySourceMappingRecord.source_id == source_id,
                OpportunitySourceMappingRecord.external_job_id == external_job_id,
            )
        ).scalars().first()

        now = utc_now()
        if existing:
            existing.last_seen_at = now
            existing.canonical_opportunity_id = canonical_opportunity_id
            existing.original_url = original_url
            db.commit()
            db.refresh(existing)
            return existing

        mapping = OpportunitySourceMappingRecord(
            canonical_opportunity_id=canonical_opportunity_id,
            source_id=source_id,
            external_job_id=external_job_id,
            original_url=original_url,
            first_seen_at=now,
            last_seen_at=now,
            mapping_status="ACTIVE",
            match_tier=match_tier.value,
            match_method=match_method,
            match_evidence_json=match_evidence or {},
            confidence_score=confidence_score,
        )
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return mapping

