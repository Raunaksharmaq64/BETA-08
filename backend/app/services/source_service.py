"""
RIGHT FIT Core — Job Source Administration Service
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CanonicalOpportunityRecord,
    JobSourceRecord,
    SourceObservationRecord,
    SourceRunLogRecord,
    utc_now,
)
from app.services.connectors import get_connector
from contracts.sources.schemas import (
    PolicyStatus,
    SourceCreateRequest,
    SourcePolicyUpdateRequest,
    SourceUpdateRequest,
)

logger = logging.getLogger("rightfit.sources")


class SourceService:
    """Administrative service for managing opportunity data sources."""

    @staticmethod
    async def create_source(db: AsyncSession, request: SourceCreateRequest) -> JobSourceRecord:
        """Registers a new opportunity source in DRAFT state after configuration check."""
        res = await db.execute(
            select(JobSourceRecord).where(JobSourceRecord.source_key == request.source_key)
        )
        existing = res.scalar_one_or_none()
        if existing:
            raise ValueError(f"A source with source_key '{request.source_key}' already exists")

        # Validate provider connector config
        connector = get_connector(request.provider)
        connector.validate_config(request.base_url, request.credential_reference)

        initial_decision = {
            "initial_registration": {
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "initial_status": PolicyStatus.DRAFT.value,
                "notes": request.notes or "Initial source registration pending policy review."
            },
            "history": []
        }

        record = JobSourceRecord(
            source_key=request.source_key,
            display_name=request.display_name,
            source_type=request.source_type.value,
            provider=request.provider.lower(),
            base_url=request.base_url,
            integration_method=request.integration_method.value,
            auth_type=request.auth_type.value,
            credential_reference=request.credential_reference,
            enabled=True,
            policy_status=PolicyStatus.DRAFT.value,
            policy_decision_json=initial_decision,
            rate_limit_per_minute=request.rate_limit_per_minute,
            timeout_seconds=request.timeout_seconds,
            retry_max_attempts=request.retry_max_attempts,
            circuit_breaker_state="CLOSED",
            consecutive_failures=0,
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.info(f"Source '{record.source_key}' registered successfully with ID {record.id}")
        return record

    @staticmethod
    async def get_source_by_id(db: AsyncSession, source_id: str) -> Optional[JobSourceRecord]:
        """Retrieves source record by UUID."""
        res = await db.execute(
            select(JobSourceRecord).where(JobSourceRecord.id == source_id)
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def get_source_by_key(db: AsyncSession, source_key: str) -> Optional[JobSourceRecord]:
        """Retrieves source record by unique slug."""
        res = await db.execute(
            select(JobSourceRecord).where(JobSourceRecord.source_key == source_key.strip().lower())
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def list_sources(
        db: AsyncSession,
        policy_status: Optional[str] = None,
        enabled: Optional[bool] = None,
        provider: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[JobSourceRecord], int]:
        """Lists sources with optional filtering."""
        query = select(JobSourceRecord)

        if policy_status:
            query = query.where(JobSourceRecord.policy_status == policy_status.upper())
        if enabled is not None:
            query = query.where(JobSourceRecord.enabled == enabled)
        if provider:
            query = query.where(JobSourceRecord.provider == provider.lower())

        count_query = select(func.count()).select_from(query.subquery())
        count_res = await db.execute(count_query)
        total = count_res.scalar_one()

        query = query.order_by(desc(JobSourceRecord.created_at)).offset(skip).limit(limit)
        results = list((await db.execute(query)).scalars().all())
        return results, total

    @staticmethod
    async def update_source(db: AsyncSession, source_id: str, request: SourceUpdateRequest) -> JobSourceRecord:
        """Updates runtime configuration settings of an existing source."""
        source = await SourceService.get_source_by_id(db, source_id)
        if not source:
            raise KeyError(f"Source with ID {source_id} not found")

        if request.display_name is not None:
            source.display_name = request.display_name
        if request.base_url is not None:
            connector = get_connector(source.provider)
            connector.validate_config(request.base_url, source.credential_reference)
            source.base_url = request.base_url
        if request.enabled is not None:
            source.enabled = request.enabled
        if request.rate_limit_per_minute is not None:
            source.rate_limit_per_minute = request.rate_limit_per_minute
        if request.timeout_seconds is not None:
            source.timeout_seconds = request.timeout_seconds
        if request.retry_max_attempts is not None:
            source.retry_max_attempts = request.retry_max_attempts
        if request.credential_reference is not None:
            source.credential_reference = request.credential_reference

        await db.commit()
        await db.refresh(source)
        return source

    @staticmethod
    async def update_policy_status(
        db: AsyncSession,
        source_id: str,
        request: SourcePolicyUpdateRequest,
        reviewer_email: str
    ) -> JobSourceRecord:
        """Updates governance policy status with audit trail."""
        source = await SourceService.get_source_by_id(db, source_id)
        if not source:
            raise KeyError(f"Source with ID {source_id} not found")

        old_status = source.policy_status
        new_status = request.policy_status.value

        decisions = dict(source.policy_decision_json or {})
        history = list(decisions.get("history", []))

        history.append({
            "from_status": old_status,
            "to_status": new_status,
            "changed_at": datetime.now(timezone.utc).isoformat(),
            "reviewer_email": reviewer_email,
            "review_notes": request.review_notes,
        })

        decisions["history"] = history
        decisions["latest_review"] = {
            "status": new_status,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "reviewer_email": reviewer_email,
            "notes": request.review_notes,
        }

        source.policy_status = new_status
        source.policy_decision_json = decisions

        await db.commit()
        await db.refresh(source)
        logger.info(f"Source '{source.source_key}' policy changed: {old_status} -> {new_status} by {reviewer_email}")
        return source

    @staticmethod
    async def get_source_run_logs(db: AsyncSession, source_id: str, limit: int = 50) -> List[SourceRunLogRecord]:
        """Retrieves recent execution run logs for a source."""
        query = (
            select(SourceRunLogRecord)
            .where(SourceRunLogRecord.source_id == source_id)
            .order_by(desc(SourceRunLogRecord.started_at))
            .limit(limit)
        )
        return list((await db.execute(query)).scalars().all())

    @staticmethod
    async def get_source_observations(db: AsyncSession, source_id: str, limit: int = 50) -> List[SourceObservationRecord]:
        """Retrieves recent observations for a source."""
        query = (
            select(SourceObservationRecord)
            .where(SourceObservationRecord.source_id == source_id)
            .order_by(desc(SourceObservationRecord.observed_at))
            .limit(limit)
        )
        return list((await db.execute(query)).scalars().all())
