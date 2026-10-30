"""
RIGHT FIT Core — Ingestion Orchestration Service
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Orchestrates the complete ingestion lifecycle:
1. Enforces Source Policy Gate (ACTIVE policy status required)
2. Checks 3-State Circuit Breaker (CLOSED / HALF_OPEN)
3. Enforces sliding-window per-source rate limits
4. Retries transient network/HTTP failures with exponential backoff & jitter
5. Captures raw observation payloads with payload hashes and provenance
6. Normalizes listings without fabricating compensation or requirements
7. Deduplicates across sources using stable SHA-256 keys
8. Updates operational metrics and source run logs
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CanonicalOpportunityRecord,
    JobSourceRecord,
    SourceObservationRecord,
    SourceRunLogRecord,
    utc_now,
)
from app.services.connectors import get_connector
from app.services.normalization_service import NormalizationService
from app.services.resilience import (
    CircuitBreakerManager,
    CircuitOpenException,
    RateLimitExceededException,
    RetryPolicy,
    circuit_breaker,
    source_rate_limiter,
)
from contracts.sources.schemas import (
    CircuitBreakerState,
    IngestionTriggerResponse,
    PolicyStatus,
    RunStatus,
    TriggerType,
)

logger = logging.getLogger("rightfit.ingestion")


class IngestionService:
    """Orchestrates ingestion runs, resilience enforcement, and canonical normalization."""

    @classmethod
    async def run_ingestion(
        cls,
        db: AsyncSession,
        source_id: str,
        trigger_type: str = TriggerType.MANUAL.value,
        max_records: int = 50,
        force: bool = False,
    ) -> IngestionTriggerResponse:
        """Executes a full ingestion run for the target source with complete guardrails."""
        res = await db.execute(
            select(JobSourceRecord).where(JobSourceRecord.id == source_id)
        )
        source = res.scalar_one_or_none()

        if not source:
            raise KeyError(f"Source with ID {source_id} not found")

        # ----------------------------------------------------------------------
        # 1. Source Policy Gate Check
        # ----------------------------------------------------------------------
        if source.policy_status != PolicyStatus.ACTIVE.value:
            run_log = SourceRunLogRecord(
                source_id=source.id,
                trigger_type=trigger_type,
                status=RunStatus.FAILED.value,
                error_category="POLICY_BLOCKED",
                safe_error_summary=(
                    f"Policy gate rejection: Source '{source.source_key}' has status '{source.policy_status}'. "
                    f"Only ACTIVE sources are permitted to ingest."
                ),
                started_at=utc_now(),
                completed_at=utc_now(),
                duration_seconds=0.0,
            )
            db.add(run_log)
            await db.commit()
            raise PermissionError(run_log.safe_error_summary)

        if not source.enabled:
            run_log = SourceRunLogRecord(
                source_id=source.id,
                trigger_type=trigger_type,
                status=RunStatus.FAILED.value,
                error_category="SOURCE_DISABLED",
                safe_error_summary=f"Administrative rejection: Source '{source.source_key}' is disabled.",
                started_at=utc_now(),
                completed_at=utc_now(),
                duration_seconds=0.0,
            )
            db.add(run_log)
            await db.commit()
            raise ValueError(run_log.safe_error_summary)

        # ----------------------------------------------------------------------
        # 2. Circuit Breaker Check
        # ----------------------------------------------------------------------
        allowed, effective_state, rejection_reason = circuit_breaker.can_execute(
            circuit_state=source.circuit_breaker_state,
            cooldown_until=source.cooldown_until,
            force=force,
        )

        if not allowed:
            run_log = SourceRunLogRecord(
                source_id=source.id,
                trigger_type=trigger_type,
                status=RunStatus.FAILED.value,
                error_category="CIRCUIT_OPEN",
                safe_error_summary=rejection_reason or "Circuit breaker is OPEN. Ingestion rejected.",
                started_at=utc_now(),
                completed_at=utc_now(),
                duration_seconds=0.0,
            )
            db.add(run_log)
            await db.commit()
            raise CircuitOpenException(run_log.safe_error_summary, cooldown_until=source.cooldown_until)

        # ----------------------------------------------------------------------
        # 3. Rate Limit Quota Check
        # ----------------------------------------------------------------------
        rate_allowed, retry_after = source_rate_limiter.acquire(source.id, source.rate_limit_per_minute)
        if not rate_allowed:
            run_log = SourceRunLogRecord(
                source_id=source.id,
                trigger_type=trigger_type,
                status=RunStatus.FAILED.value,
                error_category="RATE_LIMIT_EXCEEDED",
                safe_error_summary=f"Rate limit exceeded ({source.rate_limit_per_minute} req/min). Cooldown: {retry_after}s.",
                started_at=utc_now(),
                completed_at=utc_now(),
                duration_seconds=0.0,
            )
            db.add(run_log)
            await db.commit()
            raise RateLimitExceededException(run_log.safe_error_summary, retry_after=retry_after)

        # ----------------------------------------------------------------------
        # 4. Initialize Active Run Log
        # ----------------------------------------------------------------------
        run_log = SourceRunLogRecord(
            source_id=source.id,
            trigger_type=trigger_type,
            status=RunStatus.RUNNING.value,
            started_at=utc_now(),
        )
        db.add(run_log)
        await db.commit()
        await db.refresh(run_log)

        # ----------------------------------------------------------------------
        # 5. Fetch Records with Retries
        # ----------------------------------------------------------------------
        start_time = time.time()
        connector = get_connector(source.provider)

        try:
            fetch_result = await RetryPolicy.execute_with_retry(
                coro_fn=lambda: connector.fetch_jobs(source, limit=max_records),
                max_attempts=source.retry_max_attempts,
                base_delay=0.5,
            )
        except Exception as exc:
            duration = time.time() - start_time
            new_state, failures, cooldown = circuit_breaker.record_failure(
                current_state=source.circuit_breaker_state,
                consecutive_failures=source.consecutive_failures,
            )
            source.circuit_breaker_state = new_state
            source.consecutive_failures = failures
            source.last_failure_at = utc_now()
            source.cooldown_until = cooldown

            run_log.status = RunStatus.FAILED.value
            run_log.error_category = "CONNECTOR_FETCH_ERROR"
            run_log.safe_error_summary = f"{type(exc).__name__}: {str(exc)}"
            run_log.completed_at = utc_now()
            run_log.duration_seconds = round(duration, 2)

            await db.commit()
            logger.error(f"Ingestion run {run_log.id} failed for source '{source.source_key}': {exc}")
            raise exc

        # ----------------------------------------------------------------------
        # 6. Normalize, Capture Observation, and Upsert Canonical Opportunities
        # ----------------------------------------------------------------------
        records_fetched = len(fetch_result.records)
        records_normalized = 0
        records_inserted = 0
        records_updated = 0
        duplicates_skipped = 0

        for raw_job in fetch_result.records:
            payload_hash = NormalizationService.compute_payload_hash(raw_job.raw_payload)

            obs_res = await db.execute(
                select(SourceObservationRecord).where(
                    SourceObservationRecord.source_id == source.id,
                    SourceObservationRecord.external_job_id == raw_job.external_job_id,
                )
            )
            existing_obs = obs_res.scalar_one_or_none()

            if existing_obs:
                existing_obs.last_seen_at = utc_now()
                existing_obs.observed_at = utc_now()
                existing_obs.payload_hash_sha256 = payload_hash
                existing_obs.raw_payload_json = raw_job.raw_payload
                existing_obs.listing_url = raw_job.listing_url
            else:
                new_obs = SourceObservationRecord(
                    source_id=source.id,
                    external_job_id=raw_job.external_job_id,
                    listing_url=raw_job.listing_url,
                    observed_at=utc_now(),
                    source_published_at=raw_job.source_published_at,
                    source_updated_at=raw_job.source_updated_at,
                    raw_payload_json=raw_job.raw_payload,
                    payload_hash_sha256=payload_hash,
                    normalization_status="NORMALIZED",
                    first_seen_at=utc_now(),
                    last_seen_at=utc_now(),
                )
                db.add(new_obs)

            # Normalization to Canonical Opportunity
            try:
                norm = NormalizationService.normalize_record(raw_job, source)
                records_normalized += 1
            except Exception as norm_exc:
                logger.warning(f"Normalization failed for job {raw_job.external_job_id}: {norm_exc}")
                continue

            # Check Canonical Deduplication
            opp_res = await db.execute(
                select(CanonicalOpportunityRecord).where(
                    CanonicalOpportunityRecord.source_id == source.id,
                    CanonicalOpportunityRecord.external_job_id == raw_job.external_job_id,
                )
            )
            existing_opp = opp_res.scalar_one_or_none()

            if existing_opp:
                existing_opp.title = norm["title"]
                existing_opp.description_clean = norm["description_clean"]
                existing_opp.employment_type = norm["employment_type"]
                existing_opp.workplace_type = norm["workplace_type"]
                existing_opp.department = norm["department"]
                existing_opp.city = norm["city"]
                existing_opp.state = norm["state"]
                existing_opp.country = norm["country"]
                existing_opp.is_remote = norm["is_remote"]
                existing_opp.min_salary = norm["min_salary"]
                existing_opp.max_salary = norm["max_salary"]
                existing_opp.currency = norm["currency"]
                existing_opp.salary_period = norm["salary_period"]
                existing_opp.required_skills_json = norm["required_skills_json"]
                existing_opp.application_url = norm["application_url"]
                existing_opp.source_published_at = norm["source_published_at"]
                existing_opp.provenance_json = norm["provenance_json"]
                existing_opp.last_seen_at = utc_now()
                existing_opp.is_active = True
                records_updated += 1
            else:
                dup_res = await db.execute(
                    select(CanonicalOpportunityRecord).where(
                        CanonicalOpportunityRecord.dedup_key_sha256 == norm["dedup_key_sha256"]
                    )
                )
                cross_source_dup = dup_res.scalar_one_or_none()

                if cross_source_dup:
                    duplicates_skipped += 1
                else:
                    new_opp = CanonicalOpportunityRecord(
                        source_id=source.id,
                        external_job_id=norm["external_job_id"],
                        dedup_key_sha256=norm["dedup_key_sha256"],
                        title=norm["title"],
                        company_name=norm["company_name"],
                        description_clean=norm["description_clean"],
                        employment_type=norm["employment_type"],
                        workplace_type=norm["workplace_type"],
                        department=norm["department"],
                        city=norm["city"],
                        state=norm["state"],
                        country=norm["country"],
                        is_remote=norm["is_remote"],
                        min_salary=norm["min_salary"],
                        max_salary=norm["max_salary"],
                        currency=norm["currency"],
                        salary_period=norm["salary_period"],
                        is_salary_estimated=norm["is_salary_estimated"],
                        required_skills_json=norm["required_skills_json"],
                        application_url=norm["application_url"],
                        source_published_at=norm["source_published_at"],
                        first_seen_at=utc_now(),
                        last_seen_at=utc_now(),
                        is_active=True,
                        provenance_json=norm["provenance_json"],
                    )
                    db.add(new_opp)
                    records_inserted += 1

        # ----------------------------------------------------------------------
        # 7. Finalize Run & Update Circuit Breaker State
        # ----------------------------------------------------------------------
        duration = time.time() - start_time
        new_state, failures, cooldown = circuit_breaker.record_success(
            current_state=source.circuit_breaker_state,
            consecutive_failures=source.consecutive_failures,
        )
        source.circuit_breaker_state = new_state
        source.consecutive_failures = failures
        source.last_success_at = utc_now()
        source.cooldown_until = None

        run_log.status = RunStatus.SUCCESS.value
        run_log.records_fetched = records_fetched
        run_log.records_normalized = records_normalized
        run_log.records_inserted = records_inserted
        run_log.records_updated = records_updated
        run_log.duplicates_skipped = duplicates_skipped
        run_log.completed_at = utc_now()
        run_log.duration_seconds = round(duration, 2)

        await db.commit()
        logger.info(
            f"Ingestion run {run_log.id} complete for '{source.source_key}': "
            f"{records_fetched} fetched, {records_inserted} inserted, {records_updated} updated, "
            f"{duplicates_skipped} dupes skipped in {duration:.2f}s"
        )

        return IngestionTriggerResponse(
            run_id=run_log.id,
            source_id=source.id,
            source_key=source.source_key,
            status=RunStatus.SUCCESS,
            records_fetched=records_fetched,
            records_inserted=records_inserted,
            records_updated=records_updated,
            duplicates_skipped=duplicates_skipped,
            duration_seconds=round(duration, 2),
            circuit_state=CircuitBreakerState(source.circuit_breaker_state),
            message=f"Ingestion run completed successfully in {duration:.2f}s",
        )
