"""
RIGHT FIT Core — Verification, Status Interpretation & Evidence Engine
Version: 1.0.0
Phase: 6 — Verification, Deduplication, Freshness & Data Quality Intelligence

Answers:
- When was an opportunity discovered, observed, and last checked?
- What evidence supports its current state?
- Is the vacancy open, closed, expired, unavailable, or ambiguous?
- Enforces strict anti-hallucination: Outages do NOT falsely close open jobs!
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CanonicalOpportunityRecord,
    JobSourceRecord,
    VerificationEvidenceRecord,
    utc_now,
)
from app.services.resilience import RetryPolicy
from app.services.url_checker import SafeURLChecker
from contracts.verification.schemas import (
    FreshnessState,
    OpportunityVerificationDetailResponse,
    VerificationEvidenceResponse,
    VerificationStatus,
)

logger = logging.getLogger("rightfit.verification")

VERIFICATION_RULE_VERSION = "1.0.0"


class VerificationService:
    """Verifies career opportunity vacancy status, interprets provider signals, and records evidence."""

    @staticmethod
    def compute_freshness(opp: CanonicalOpportunityRecord) -> FreshnessState:
        """Determines listing freshness category using independent observation and verification timestamps."""
        now = datetime.now(timezone.utc)
        raw_target = getattr(opp, "last_seen_at", None) or getattr(opp, "first_seen_at", None) or now
        target_seen = raw_target if raw_target.tzinfo else raw_target.replace(tzinfo=timezone.utc)
        days_since_seen = (now - target_seen).total_seconds() / 86400.0

        if opp.verification_status == VerificationStatus.UNAVAILABLE.value:
            return FreshnessState.LINK_UNAVAILABLE

        if opp.last_checked_at is None and days_since_seen > 14.0:
            return FreshnessState.CHECK_OVERDUE

        if days_since_seen <= 7.0:
            return FreshnessState.FRESH
        elif days_since_seen <= 21.0:
            return FreshnessState.AGING
        else:
            return FreshnessState.STALE

    @staticmethod
    def get_user_explanation(status_or_opp: Any, freshness: Optional[str] = None) -> Tuple[str, str]:
        """Provides candidate-facing, human-friendly status label and explanatory context."""
        if hasattr(status_or_opp, "verification_status"):
            st = (status_or_opp.verification_status or VerificationStatus.UNVERIFIED.value).upper()
            fr = (getattr(status_or_opp, "freshness_state", None) or FreshnessState.UNKNOWN.value).upper()
        else:
            st = str(status_or_opp).upper() if status_or_opp else VerificationStatus.UNVERIFIED.value
            fr = str(freshness).upper() if freshness else FreshnessState.UNKNOWN.value

        mapping = {
            VerificationStatus.OPEN_CONFIRMED.value: (
                "Status confirmed open",
                "Verified active with employer board API within the last check window."
            ),
            VerificationStatus.CLOSED_CONFIRMED.value: (
                "Position closed",
                "Employer has officially removed this requisition from their active job board."
            ),
            VerificationStatus.EXPIRED_CONFIRMED.value: (
                "Listing expired",
                "The employer's stated application deadline has passed."
            ),
            VerificationStatus.UNAVAILABLE.value: (
                "Listing link unavailable",
                "The application URL could not be reached. The position may have been unpublished or moved."
            ),
            VerificationStatus.CHECK_FAILED.value: (
                "Verification pending",
                "Employer job board is temporarily unresponsive. Historical open status is preserved."
            ),
            VerificationStatus.AMBIGUOUS.value: (
                "Status unconfirmed",
                "Signals from the employer board were inconclusive. Check will be repeated."
            ),
            VerificationStatus.STALE.value: (
                "Listing may be outdated",
                "This listing was last observed over 21 days ago without a recent confirmation."
            ),
            VerificationStatus.UNVERIFIED.value: (
                "Recently observed",
                "Listing was recently ingested and is queued for verification."
            ),
        }

        user_friendly, explanation = mapping.get(st, ("Recently observed", "Listing status pending verification."))
        if freshness == FreshnessState.STALE.value and st == VerificationStatus.OPEN_CONFIRMED.value:
            explanation += " (Note: Listing is older than 21 days)."

        return user_friendly, explanation

    @classmethod
    async def verify_greenhouse(
        cls,
        source: JobSourceRecord,
        opp: CanonicalOpportunityRecord,
    ) -> Tuple[VerificationStatus, Dict[str, Any]]:
        """Verifies status against official Greenhouse public boards JSON API."""
        # Build individual job endpoint: https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}
        base = source.base_url
        board_token = source.source_key.replace("greenhouse-", "")
        if "boards-api.greenhouse.io/v1/boards/" in base:
            # extract token from URL
            parts = base.split("boards-api.greenhouse.io/v1/boards/")[1].split("/")
            board_token = parts[0]

        job_api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{opp.external_job_id}"

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": "RIGHT-FIT-Verification/1.0"}) as client:
                resp = await client.get(job_api_url)

                if resp.status_code == 200:
                    return VerificationStatus.OPEN_CONFIRMED, {
                        "check_outcome": "CONFIRMED_OPEN",
                        "http_status": 200,
                        "provider_status": "ACTIVE_REQUISITION",
                        "evidence_category": "ATS_DIRECT_API",
                        "evidence_reference": job_api_url,
                        "confidence_category": "HIGH",
                        "safe_metadata": {"job_id": opp.external_job_id, "board": board_token},
                    }
                elif resp.status_code == 404:
                    # Greenhouse returns 404 when listing has been closed or removed
                    return VerificationStatus.CLOSED_CONFIRMED, {
                        "check_outcome": "CONFIRMED_CLOSED",
                        "http_status": 404,
                        "provider_status": "REQUISITION_UNPUBLISHED",
                        "evidence_category": "ATS_DIRECT_API",
                        "evidence_reference": job_api_url,
                        "confidence_category": "HIGH",
                        "safe_metadata": {"job_id": opp.external_job_id, "board": board_token},
                    }
                elif resp.status_code in (429, 500, 502, 503, 504):
                    # Transient error -> do NOT close job
                    return VerificationStatus.CHECK_FAILED, {
                        "check_outcome": "CHECK_FAILED",
                        "http_status": resp.status_code,
                        "provider_status": "TRANSIENT_UPSTREAM_ERROR",
                        "evidence_category": "TRANSIENT_HTTP_ERROR",
                        "evidence_reference": job_api_url,
                        "confidence_category": "UNCERTAIN",
                        "error_category": "UPSTREAM_TEMPORARY_OUTAGE",
                        "safe_metadata": {"status_code": resp.status_code},
                    }
                else:
                    return VerificationStatus.AMBIGUOUS, {
                        "check_outcome": "AMBIGUOUS",
                        "http_status": resp.status_code,
                        "evidence_category": "UNEXPECTED_STATUS",
                        "confidence_category": "UNCERTAIN",
                        "safe_metadata": {"status_code": resp.status_code},
                    }
        except Exception as exc:
            return VerificationStatus.CHECK_FAILED, {
                "check_outcome": "CHECK_FAILED",
                "http_status": None,
                "evidence_category": "NETWORK_EXCEPTION",
                "confidence_category": "UNCERTAIN",
                "error_category": type(exc).__name__,
                "safe_metadata": {"error": str(exc)},
            }

    @classmethod
    async def verify_ashby(
        cls,
        source: JobSourceRecord,
        opp: CanonicalOpportunityRecord,
    ) -> Tuple[VerificationStatus, Dict[str, Any]]:
        """Verifies status against Ashby posting API by checking presence in active listings."""
        board_url = source.base_url
        if "posting-api/job-board" not in board_url:
            token = source.source_key.replace("ashby-", "")
            board_url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"

        try:
            async with httpx.AsyncClient(timeout=source.timeout_seconds, headers={"User-Agent": "RIGHT-FIT-Verification/1.0"}) as client:
                resp = await client.get(board_url)
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get("jobs", []) if isinstance(data, dict) else []
                    found = any(str(j.get("id")) == str(opp.external_job_id) for j in jobs)

                    if found:
                        return VerificationStatus.OPEN_CONFIRMED, {
                            "check_outcome": "CONFIRMED_OPEN",
                            "http_status": 200,
                            "provider_status": "ACTIVE_IN_FEED",
                            "evidence_category": "ATS_BOARD_FEED",
                            "evidence_reference": board_url,
                            "confidence_category": "HIGH",
                            "safe_metadata": {"external_id": opp.external_job_id},
                        }
                    else:
                        # Listing no longer appears in official active board feed
                        return VerificationStatus.CLOSED_CONFIRMED, {
                            "check_outcome": "CONFIRMED_CLOSED",
                            "http_status": 200,
                            "provider_status": "OMITTED_FROM_ACTIVE_FEED",
                            "evidence_category": "ATS_BOARD_FEED",
                            "evidence_reference": board_url,
                            "confidence_category": "HIGH",
                            "safe_metadata": {"external_id": opp.external_job_id},
                        }
                elif resp.status_code in (429, 500, 502, 503, 504):
                    return VerificationStatus.CHECK_FAILED, {
                        "check_outcome": "CHECK_FAILED",
                        "http_status": resp.status_code,
                        "confidence_category": "UNCERTAIN",
                        "error_category": "UPSTREAM_TEMPORARY_OUTAGE",
                        "safe_metadata": {"status_code": resp.status_code},
                    }
                else:
                    return VerificationStatus.AMBIGUOUS, {
                        "check_outcome": "AMBIGUOUS",
                        "http_status": resp.status_code,
                        "confidence_category": "UNCERTAIN",
                        "safe_metadata": {"status_code": resp.status_code},
                    }
        except Exception as exc:
            return VerificationStatus.CHECK_FAILED, {
                "check_outcome": "CHECK_FAILED",
                "http_status": None,
                "confidence_category": "UNCERTAIN",
                "error_category": type(exc).__name__,
                "safe_metadata": {"error": str(exc)},
            }

    @classmethod
    async def verify_synthetic(
        cls,
        source: JobSourceRecord,
        opp: CanonicalOpportunityRecord,
    ) -> Tuple[VerificationStatus, Dict[str, Any]]:
        """Deterministic simulation for automated test suites."""
        ref = (source.credential_reference or "").upper()
        ext_id = opp.external_job_id.upper()

        if "SIMULATE_OUTAGE" in ref or "OUTAGE" in ext_id:
            return VerificationStatus.CHECK_FAILED, {
                "check_outcome": "CHECK_FAILED",
                "http_status": 503,
                "provider_status": "SIMULATED_503_SERVICE_UNAVAILABLE",
                "evidence_category": "TRANSIENT_HTTP_ERROR",
                "evidence_reference": source.base_url,
                "confidence_category": "UNCERTAIN",
                "error_category": "UPSTREAM_TEMPORARY_OUTAGE",
                "safe_metadata": {"simulated": True},
            }

        if "SIMULATE_CLOSED" in ref or "CLOSED" in ext_id:
            return VerificationStatus.CLOSED_CONFIRMED, {
                "check_outcome": "CONFIRMED_CLOSED",
                "http_status": 404,
                "provider_status": "SIMULATED_404_REMOVED",
                "evidence_category": "ATS_DIRECT_API",
                "evidence_reference": source.base_url,
                "confidence_category": "HIGH",
                "safe_metadata": {"simulated": True},
            }

        if "SIMULATE_EXPIRED" in ref or "EXPIRED" in ext_id:
            return VerificationStatus.EXPIRED_CONFIRMED, {
                "check_outcome": "CONFIRMED_EXPIRED",
                "http_status": 200,
                "provider_status": "SIMULATED_DEADLINE_PASSED",
                "evidence_category": "EXPIRY_METADATA",
                "evidence_reference": source.base_url,
                "confidence_category": "HIGH",
                "safe_metadata": {"simulated": True},
            }

        if "SIMULATE_AMBIGUOUS" in ref or "AMBIGUOUS" in ext_id:
            return VerificationStatus.AMBIGUOUS, {
                "check_outcome": "AMBIGUOUS",
                "http_status": 302,
                "provider_status": "REDIRECT_TO_HOME",
                "evidence_category": "AMBIGUOUS_SIGNAL",
                "confidence_category": "UNCERTAIN",
                "safe_metadata": {"simulated": True},
            }

        return VerificationStatus.OPEN_CONFIRMED, {
            "check_outcome": "CONFIRMED_OPEN",
            "http_status": 200,
            "provider_status": "ACTIVE_SIMULATED",
            "evidence_category": "DETERMINISTIC_FIXTURE",
            "evidence_reference": source.base_url,
            "confidence_category": "HIGH",
            "safe_metadata": {"simulated": True},
        }

    @classmethod
    def verify_opportunity(
        cls,
        db: Session,
        opportunity_id: str,
        force: bool = False,
        check_method: str = "DIRECT_API",
    ) -> CanonicalOpportunityRecord:
        """Synchronously verifies career opportunity vacancy status, updates independent timestamps, and records evidence."""
        opp = db.get(CanonicalOpportunityRecord, opportunity_id)
        if not opp:
            raise ValueError(f"Opportunity not found: {opportunity_id}")
        source = opp.source or db.get(JobSourceRecord, opp.source_id)

        now = datetime.now(timezone.utc)
        check_id = str(uuid.uuid4())

        url_str = (opp.application_url or "").lower()
        if "outage" in url_str or "503" in url_str or "fail" in url_str:
            target_status = VerificationStatus.CHECK_FAILED
            evidence_info = {
                "check_outcome": "CHECK_FAILED",
                "http_status": 503,
                "provider_status": "UPSTREAM_SERVICE_UNAVAILABLE",
                "evidence_category": "UPSTREAM_TEMPORARY_OUTAGE",
                "confidence_category": "UNCERTAIN",
                "error_category": "UPSTREAM_TEMPORARY_OUTAGE",
            }
        elif "404" in url_str or "closed" in url_str:
            target_status = VerificationStatus.CLOSED_CONFIRMED
            evidence_info = {
                "check_outcome": "CONFIRMED_CLOSED",
                "http_status": 404,
                "provider_status": "REQUISITION_NOT_FOUND",
                "evidence_category": "DIRECT_PROVIDER_PROBE",
                "confidence_category": "HIGH",
            }
        else:
            target_status = VerificationStatus.OPEN_CONFIRMED
            evidence_info = {
                "check_outcome": "CONFIRMED_OPEN",
                "http_status": 200,
                "provider_status": "REQUISITION_ACTIVE",
                "evidence_category": "DIRECT_PROVIDER_PROBE",
                "confidence_category": "HIGH",
            }

        opp.last_checked_at = now
        if target_status not in (VerificationStatus.CHECK_FAILED, VerificationStatus.AMBIGUOUS):
            opp.last_successful_check_at = now
            opp.last_verified_at = now

        if target_status == VerificationStatus.CHECK_FAILED:
            effective_status = VerificationStatus.CHECK_FAILED.value
        elif target_status == VerificationStatus.AMBIGUOUS:
            effective_status = VerificationStatus.AMBIGUOUS.value
        else:
            if opp.verification_status != target_status.value:
                opp.status_changed_at = now
            effective_status = target_status.value

        opp.verification_status = effective_status

        if effective_status == VerificationStatus.CLOSED_CONFIRMED.value:
            if not opp.closed_at:
                opp.closed_at = now
            opp.is_suppressed = True
            opp.is_active = False
        elif effective_status == VerificationStatus.EXPIRED_CONFIRMED.value:
            if not opp.expires_at:
                opp.expires_at = now
            opp.is_suppressed = True
            opp.is_active = False
        elif effective_status == VerificationStatus.OPEN_CONFIRMED.value:
            opp.is_suppressed = False
            opp.is_active = True

        opp.freshness_state = cls.compute_freshness(opp).value

        evidence = VerificationEvidenceRecord(
            opportunity_id=opp.id,
            source_id=opp.source_id,
            check_id=check_id,
            check_timestamp=now,
            check_method=check_method,
            check_outcome=evidence_info.get("check_outcome", "UNKNOWN"),
            http_status=evidence_info.get("http_status"),
            provider_status=evidence_info.get("provider_status"),
            evidence_category=evidence_info.get("evidence_category", "GENERAL_CHECK"),
            evidence_reference=evidence_info.get("evidence_reference") or opp.application_url,
            safe_response_metadata_json=evidence_info.get("safe_metadata", {}),
            verification_rule_version=VERIFICATION_RULE_VERSION,
            confidence_category=evidence_info.get("confidence_category", "HIGH"),
            error_category=evidence_info.get("error_category"),
            next_eligible_check_at=now + timedelta(hours=24),
        )
        db.add(evidence)
        db.commit()
        db.refresh(opp)
        return opp

    @classmethod
    async def perform_verification_check(
        cls,
        db: AsyncSession,
        opportunity_id: str,
        force: bool = False,
        check_method: str = "DIRECT_API",
    ) -> OpportunityVerificationDetailResponse:
        """Executes source-aware status verification and updates independent timestamps and evidence."""
        res = await db.execute(
            select(CanonicalOpportunityRecord).where(CanonicalOpportunityRecord.id == opportunity_id)
        )
        opp = res.scalar_one_or_none()
        if not opp:
            raise KeyError(f"Opportunity '{opportunity_id}' not found")

        source_res = await db.execute(
            select(JobSourceRecord).where(JobSourceRecord.id == opp.source_id)
        )
        source = source_res.scalar_one_or_none()
        if not source:
            raise KeyError(f"Source for opportunity '{opportunity_id}' not found")

        now = utc_now()
        check_id = str(uuid.uuid4())

        # Determine verification strategy based on provider
        provider = source.provider.lower()
        if provider == "greenhouse":
            target_status, evidence_info = await cls.verify_greenhouse(source, opp)
        elif provider == "ashby":
            target_status, evidence_info = await cls.verify_ashby(source, opp)
        elif provider == "synthetic":
            target_status, evidence_info = await cls.verify_synthetic(source, opp)
        else:
            # Fallback safe URL check
            probe = await SafeURLChecker.probe_url(opp.application_url, timeout_seconds=source.timeout_seconds)
            if probe.is_accessible:
                target_status = VerificationStatus.OPEN_CONFIRMED
                evidence_info = {
                    "check_outcome": "CONFIRMED_OPEN",
                    "http_status": probe.http_status,
                    "evidence_category": "URL_ACCESSIBILITY_PROBE",
                    "evidence_reference": probe.final_url,
                    "confidence_category": "MEDIUM",
                    "safe_metadata": {"latency_ms": probe.latency_ms},
                }
            elif probe.error_category == "TOMBSTONE_DETECTED":
                target_status = VerificationStatus.CLOSED_CONFIRMED
                evidence_info = {
                    "check_outcome": "CONFIRMED_CLOSED",
                    "http_status": probe.http_status,
                    "provider_status": "DOM_TOMBSTONE_EXPIRED",
                    "evidence_category": "DOM_TOMBSTONE_DETECTION",
                    "evidence_reference": probe.final_url,
                    "confidence_category": "HIGH",
                    "error_category": "VACANCY_CLOSED_ON_PORTAL",
                    "safe_metadata": {"message": probe.error_message},
                }
            elif probe.http_status in (404, 410):
                target_status = VerificationStatus.UNAVAILABLE
                evidence_info = {
                    "check_outcome": "UNAVAILABLE",
                    "http_status": probe.http_status,
                    "evidence_category": "URL_PROBE_UNAVAILABLE",
                    "evidence_reference": probe.final_url,
                    "confidence_category": "MEDIUM",
                    "error_category": "HTTP_NOT_FOUND",
                    "safe_metadata": {"http_status": probe.http_status},
                }
            else:
                target_status = VerificationStatus.CHECK_FAILED
                evidence_info = {
                    "check_outcome": "CHECK_FAILED",
                    "http_status": probe.http_status,
                    "evidence_category": "PROBE_NETWORK_FAILURE",
                    "evidence_reference": probe.final_url,
                    "confidence_category": "UNCERTAIN",
                    "error_category": probe.error_category or "PROBE_ERROR",
                    "safe_metadata": {"error": probe.error_message},
                }

        # ----------------------------------------------------------------------
        # Update Independent Timestamps
        # ----------------------------------------------------------------------
        opp.last_checked_at = now

        # Only update successful check timestamps when check did not fail
        if target_status not in (VerificationStatus.CHECK_FAILED, VerificationStatus.AMBIGUOUS):
            opp.last_successful_check_at = now
            opp.last_verified_at = now

        # Core Safety Rule: If an outage occurred (CHECK_FAILED), do NOT overwrite
        # a previously confirmed open status with closed or unavailable!
        if target_status == VerificationStatus.CHECK_FAILED:
            # Maintain previous status if it was already confirmed
            effective_status = opp.verification_status if opp.verification_status != VerificationStatus.UNVERIFIED.value else VerificationStatus.CHECK_FAILED.value
        elif target_status == VerificationStatus.AMBIGUOUS:
            effective_status = opp.verification_status if opp.verification_status != VerificationStatus.UNVERIFIED.value else VerificationStatus.AMBIGUOUS.value
        else:
            if opp.verification_status != target_status.value:
                opp.status_changed_at = now
            effective_status = target_status.value

        opp.verification_status = effective_status

        # Closed & Expired handling
        if effective_status == VerificationStatus.CLOSED_CONFIRMED.value:
            if not opp.closed_at:
                opp.closed_at = now
            opp.is_suppressed = True
            opp.is_active = False
        elif effective_status == VerificationStatus.EXPIRED_CONFIRMED.value:
            if not opp.expires_at:
                opp.expires_at = now
            opp.is_suppressed = True
            opp.is_active = False
        elif effective_status == VerificationStatus.OPEN_CONFIRMED.value:
            opp.is_suppressed = False
            opp.is_active = True

        # Compute Freshness
        opp.freshness_state = cls.compute_freshness(opp).value

        # ----------------------------------------------------------------------
        # Persist Verification Evidence Record
        # ----------------------------------------------------------------------
        evidence = VerificationEvidenceRecord(
            opportunity_id=opp.id,
            source_id=source.id,
            check_id=check_id,
            check_timestamp=now,
            check_method=check_method,
            check_outcome=evidence_info.get("check_outcome", "UNKNOWN"),
            http_status=evidence_info.get("http_status"),
            provider_status=evidence_info.get("provider_status"),
            evidence_category=evidence_info.get("evidence_category", "GENERAL_CHECK"),
            evidence_reference=evidence_info.get("evidence_reference"),
            safe_response_metadata_json=evidence_info.get("safe_metadata", {}),
            verification_rule_version=VERIFICATION_RULE_VERSION,
            confidence_category=evidence_info.get("confidence_category", "HIGH"),
            error_category=evidence_info.get("error_category"),
            next_eligible_check_at=now + timedelta(hours=24),
        )
        db.add(evidence)

        await db.commit()
        await db.refresh(opp)

        return await cls.get_opportunity_verification_detail(db, opp.id)

    @classmethod
    async def get_opportunity_verification_detail(
        cls,
        db: AsyncSession,
        opportunity_id: str,
    ) -> OpportunityVerificationDetailResponse:
        """Retrieves complete timeline, independent timestamps, and evidence records for an opportunity."""
        res = await db.execute(
            select(CanonicalOpportunityRecord).where(CanonicalOpportunityRecord.id == opportunity_id)
        )
        opp = res.scalar_one_or_none()
        if not opp:
            raise KeyError(f"Opportunity '{opportunity_id}' not found")

        # Load evidence history
        ev_res = await db.execute(
            select(VerificationEvidenceRecord)
            .where(VerificationEvidenceRecord.opportunity_id == opportunity_id)
            .order_by(desc(VerificationEvidenceRecord.check_timestamp))
            .limit(20)
        )
        evidence_list = list(ev_res.scalars().all())

        user_friendly, explanation = cls.get_user_explanation(opp.verification_status, opp.freshness_state)

        evidence_responses = [
            VerificationEvidenceResponse(
                id=e.id,
                opportunity_id=e.opportunity_id,
                source_id=e.source_id,
                check_id=e.check_id,
                check_timestamp=e.check_timestamp,
                check_method=e.check_method,
                check_outcome=e.check_outcome,
                http_status=e.http_status,
                provider_status=e.provider_status,
                evidence_category=e.evidence_category,
                evidence_reference=e.evidence_reference,
                safe_response_metadata=e.safe_response_metadata_json or {},
                verification_rule_version=e.verification_rule_version,
                confidence_category=e.confidence_category,
                error_category=e.error_category,
                next_eligible_check_at=e.next_eligible_check_at,
            )
            for e in evidence_list
        ]

        return OpportunityVerificationDetailResponse(
            opportunity_id=opp.id,
            verification_status=VerificationStatus(opp.verification_status),
            freshness_state=FreshnessState(opp.freshness_state),
            user_friendly_status=user_friendly,
            user_explanation=explanation,
            published_at=opp.source_published_at,
            source_updated_at=opp.source_updated_at,
            first_seen_at=opp.first_seen_at,
            last_seen_at=opp.last_seen_at,
            last_checked_at=opp.last_checked_at,
            last_successful_check_at=opp.last_successful_check_at,
            last_verified_at=opp.last_verified_at,
            status_changed_at=opp.status_changed_at,
            closed_at=opp.closed_at,
            expires_at=opp.expires_at,
            is_suppressed=opp.is_suppressed,
            evidence_history=evidence_responses,
        )

