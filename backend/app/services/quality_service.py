"""
RIGHT FIT — Data Quality Metrics Service
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import (
    CanonicalOpportunityRecord,
    DuplicateCandidateRecord,
    JobSourceRecord,
    MergeDecisionRecord,
    UserListingFeedbackRecord,
    utc_now,
)
from contracts.verification.schemas import (
    FreshnessState,
    MergeStatus,
    QualityMetricsResponse,
    VerificationStatus,
)

logger = logging.getLogger("rightfit.quality")


class QualityService:
    """Aggregates and computes operational data quality metrics across canonical opportunities."""

    @classmethod
    def get_quality_metrics(cls, db: Session) -> QualityMetricsResponse:
        """Calculate live system quality, freshness, verification coverage, and source health KPIs."""
        total_opps = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False
            )
        ) or 0

        fresh_opps = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.freshness_state == FreshnessState.FRESH.value,
            )
        ) or 0

        aging_opps = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.freshness_state == FreshnessState.AGING.value,
            )
        ) or 0

        stale_opps = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.freshness_state == FreshnessState.STALE.value,
            )
        ) or 0

        confirmed_open = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.verification_status == VerificationStatus.OPEN_CONFIRMED.value,
            )
        ) or 0

        confirmed_closed = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.verification_status.in_([
                    VerificationStatus.CLOSED_CONFIRMED.value,
                    VerificationStatus.EXPIRED_CONFIRMED.value,
                ]),
            )
        ) or 0

        unavailable_count = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.verification_status == VerificationStatus.UNAVAILABLE.value,
            )
        ) or 0

        ambiguous_count = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.verification_status.in_([
                    VerificationStatus.AMBIGUOUS.value,
                    VerificationStatus.CHECK_FAILED.value,
                ]),
            )
        ) or 0

        verified_count = db.scalar(
            select(func.count(CanonicalOpportunityRecord.id)).where(
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.verification_status != VerificationStatus.UNVERIFIED.value,
            )
        ) or 0

        duplicate_candidates = db.scalar(
            select(func.count(DuplicateCandidateRecord.id)).where(
                DuplicateCandidateRecord.status == MergeStatus.PROPOSED.value
            )
        ) or 0

        confirmed_merges = db.scalar(
            select(func.count(MergeDecisionRecord.id)).where(
                MergeDecisionRecord.status == MergeStatus.CONFIRMED.value
            )
        ) or 0

        user_feedback_count = db.scalar(
            select(func.count(UserListingFeedbackRecord.id))
        ) or 0

        # KPI percentages
        freshness_rate = round((fresh_opps / total_opps * 100.0), 2) if total_opps > 0 else 0.0
        verification_coverage = round((verified_count / total_opps * 100.0), 2) if total_opps > 0 else 0.0
        confirmed_open_rate = round((confirmed_open / total_opps * 100.0), 2) if total_opps > 0 else 0.0
        link_unavailable_rate = round((unavailable_count / total_opps * 100.0), 2) if total_opps > 0 else 0.0

        # Source breakdown
        sources = db.execute(select(JobSourceRecord).order_by(JobSourceRecord.display_name.asc())).scalars().all()
        source_breakdown: List[Dict[str, Any]] = []

        for src in sources:
            src_total = db.scalar(
                select(func.count(CanonicalOpportunityRecord.id)).where(
                    CanonicalOpportunityRecord.source_id == src.id,
                    CanonicalOpportunityRecord.is_suppressed == False,
                )
            ) or 0

            src_open = db.scalar(
                select(func.count(CanonicalOpportunityRecord.id)).where(
                    CanonicalOpportunityRecord.source_id == src.id,
                    CanonicalOpportunityRecord.is_suppressed == False,
                    CanonicalOpportunityRecord.verification_status == VerificationStatus.OPEN_CONFIRMED.value,
                )
            ) or 0

            src_fresh = db.scalar(
                select(func.count(CanonicalOpportunityRecord.id)).where(
                    CanonicalOpportunityRecord.source_id == src.id,
                    CanonicalOpportunityRecord.is_suppressed == False,
                    CanonicalOpportunityRecord.freshness_state == FreshnessState.FRESH.value,
                )
            ) or 0

            source_breakdown.append({
                "source_id": src.id,
                "name": src.display_name,
                "provider": src.provider,
                "enabled": src.enabled,
                "circuit_breaker_state": src.circuit_breaker_state,
                "total_opportunities": src_total,
                "confirmed_open": src_open,
                "fresh_rate": round((src_fresh / src_total * 100.0), 1) if src_total > 0 else 0.0,
            })

        return QualityMetricsResponse(
            total_opportunities=total_opps,
            fresh_opportunities=fresh_opps,
            aging_opportunities=aging_opps,
            stale_opportunities=stale_opps,
            confirmed_open_count=confirmed_open,
            confirmed_closed_count=confirmed_closed,
            unavailable_count=unavailable_count,
            ambiguous_count=ambiguous_count,
            freshness_rate=freshness_rate,
            verification_coverage=verification_coverage,
            confirmed_open_rate=confirmed_open_rate,
            link_unavailable_rate=link_unavailable_rate,
            duplicate_candidates_count=duplicate_candidates,
            confirmed_merges_count=confirmed_merges,
            user_feedback_count=user_feedback_count,
            source_breakdown=source_breakdown,
            generated_at=utc_now(),
        )
