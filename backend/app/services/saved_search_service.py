"""
RIGHT FIT — Saved Jobs, Saved Searches & Alert Subscriptions Service
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery

Implements:
1. Candidate Saved Jobs CRUD with personal notes
2. Saved Searches and alert configuration (INSTANT, DAILY, WEEKLY)
3. Idempotent Alert Delivery Worker and audit logs
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    AlertDeliveryLogRecord,
    CanonicalOpportunityRecord,
    SavedJobRecord,
    SavedSearchRecord,
)
from contracts.matching.schemas import (
    AlertDeliveryLogResponse,
    AlertFrequency,
    JobSearchResultItem,
    SavedJobCreateRequest,
    SavedJobResponse,
    SavedJobUpdateRequest,
    SavedSearchCreateRequest,
    SavedSearchResponse,
    SavedSearchUpdateRequest,
)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class SavedSearchService:
    """Manages saved jobs, persistent search subscriptions, and automated alert delivery."""

    # --------------------------------------------------------------------------
    # Saved Jobs
    # --------------------------------------------------------------------------

    @classmethod
    def save_job(
        cls,
        session: Session,
        user_id: str,
        opportunity_id: str,
        notes: Optional[str] = None,
    ) -> SavedJobResponse:
        """Saves a career opportunity for a candidate; updates notes if already saved."""
        existing = session.execute(
            select(SavedJobRecord).where(
                SavedJobRecord.user_id == user_id,
                SavedJobRecord.opportunity_id == opportunity_id,
            )
        ).scalars().first()

        if existing:
            if notes is not None:
                existing.notes = notes
                session.commit()
                session.refresh(existing)
            return cls._to_saved_job_response(existing)

        # Verify opportunity exists
        opp = session.execute(
            select(CanonicalOpportunityRecord).where(CanonicalOpportunityRecord.id == opportunity_id)
        ).scalars().first()
        if not opp:
            raise ValueError(f"Opportunity with ID '{opportunity_id}' not found.")

        record = SavedJobRecord(
            user_id=user_id,
            opportunity_id=opportunity_id,
            notes=notes,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return cls._to_saved_job_response(record, opp)

    @classmethod
    def list_saved_jobs(cls, session: Session, user_id: str) -> List[SavedJobResponse]:
        """Returns all jobs saved by the specified candidate."""
        records = session.execute(
            select(SavedJobRecord)
            .options(
                joinedload(SavedJobRecord.opportunity).joinedload(CanonicalOpportunityRecord.source)
            )
            .where(SavedJobRecord.user_id == user_id)
            .order_by(SavedJobRecord.created_at.desc())
        ).scalars().all()

        return [cls._to_saved_job_response(rec, rec.opportunity) for rec in records]

    @classmethod
    def unsave_job(cls, session: Session, user_id: str, identifier: str) -> bool:
        """Removes a saved job by either saved_job_id or opportunity_id."""
        record = session.execute(
            select(SavedJobRecord).where(
                SavedJobRecord.user_id == user_id,
                (SavedJobRecord.id == identifier) | (SavedJobRecord.opportunity_id == identifier),
            )
        ).scalars().first()

        if not record:
            return False

        session.delete(record)
        session.commit()
        return True

    @classmethod
    def update_saved_job_notes(
        cls,
        session: Session,
        user_id: str,
        saved_job_id: str,
        notes: Optional[str],
    ) -> Optional[SavedJobResponse]:
        """Updates personal notes on a saved job."""
        record = session.execute(
            select(SavedJobRecord)
            .options(
                joinedload(SavedJobRecord.opportunity).joinedload(CanonicalOpportunityRecord.source)
            )
            .where(
                SavedJobRecord.user_id == user_id,
                SavedJobRecord.id == saved_job_id,
            )
        ).scalars().first()

        if not record:
            return None

        record.notes = notes
        session.commit()
        session.refresh(record)
        return cls._to_saved_job_response(record, record.opportunity)

    @classmethod
    def _to_saved_job_response(
        cls,
        record: SavedJobRecord,
        opp: Optional[CanonicalOpportunityRecord] = None,
    ) -> SavedJobResponse:
        opp_item = None
        if opp:
            opp_item = JobSearchResultItem(
                id=opp.id,
                title=opp.title,
                company_name=opp.company_name,
                city=opp.city,
                state=opp.state,
                country=opp.country,
                workplace_type=opp.workplace_type,
                is_remote=opp.is_remote,
                employment_type=opp.employment_type,
                min_salary=opp.min_salary,
                max_salary=opp.max_salary,
                currency=opp.currency,
                salary_period=opp.salary_period,
                required_skills=opp.required_skills_json or [],
                application_url=opp.application_url,
                verification_status=opp.verification_status,
                freshness_state=opp.freshness_state,
                first_seen_at=opp.first_seen_at,
                last_verified_at=opp.last_verified_at,
                source_name=opp.source.display_name if opp.source else "Core Feed",
                is_saved=True,
                saved_job_id=record.id,
            )

        return SavedJobResponse(
            id=record.id,
            user_id=record.user_id,
            opportunity_id=record.opportunity_id,
            notes=record.notes,
            created_at=record.created_at,
            opportunity=opp_item,
        )

    # --------------------------------------------------------------------------
    # Saved Searches & Alerts
    # --------------------------------------------------------------------------

    @classmethod
    def create_saved_search(
        cls,
        session: Session,
        user_id: str,
        req: SavedSearchCreateRequest,
    ) -> SavedSearchResponse:
        """Saves search parameters and configures alert frequency."""
        query_payload = {"query": req.query} if req.query else {}
        record = SavedSearchRecord(
            user_id=user_id,
            name=req.name,
            query_json=query_payload,
            filters_json=req.filters or {},
            alert_enabled=req.alert_enabled,
            alert_frequency=req.alert_frequency.value,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return cls._to_saved_search_response(record)

    @classmethod
    def list_saved_searches(cls, session: Session, user_id: str) -> List[SavedSearchResponse]:
        """Lists all saved searches for candidate."""
        records = session.execute(
            select(SavedSearchRecord)
            .where(SavedSearchRecord.user_id == user_id)
            .order_by(SavedSearchRecord.created_at.desc())
        ).scalars().all()
        return [cls._to_saved_search_response(r) for r in records]

    @classmethod
    def update_saved_search(
        cls,
        session: Session,
        user_id: str,
        search_id: str,
        req: SavedSearchUpdateRequest,
    ) -> Optional[SavedSearchResponse]:
        """Updates query filters or notification cadence."""
        record = session.execute(
            select(SavedSearchRecord).where(
                SavedSearchRecord.user_id == user_id,
                SavedSearchRecord.id == search_id,
            )
        ).scalars().first()

        if not record:
            return None

        if req.name is not None:
            record.name = req.name
        if req.query is not None:
            record.query_json = {"query": req.query}
        if req.filters is not None:
            record.filters_json = req.filters
        if req.alert_enabled is not None:
            record.alert_enabled = req.alert_enabled
        if req.alert_frequency is not None:
            record.alert_frequency = req.alert_frequency.value

        session.commit()
        session.refresh(record)
        return cls._to_saved_search_response(record)

    @classmethod
    def delete_saved_search(cls, session: Session, user_id: str, search_id: str) -> bool:
        """Deletes a saved search subscription."""
        record = session.execute(
            select(SavedSearchRecord).where(
                SavedSearchRecord.user_id == user_id,
                SavedSearchRecord.id == search_id,
            )
        ).scalars().first()

        if not record:
            return False

        session.delete(record)
        session.commit()
        return True

    @classmethod
    def process_alerts(
        cls,
        session: Session,
        search_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> List[AlertDeliveryLogResponse]:
        """
        Evaluates active saved searches, finds newly ingested/updated jobs matching criteria,
        and logs delivery idempotently.
        """
        now = datetime.now(timezone.utc)
        query = select(SavedSearchRecord).where(SavedSearchRecord.alert_enabled.is_(True))
        if search_id:
            query = query.where(SavedSearchRecord.id == search_id)

        subscriptions = session.execute(query).scalars().all()
        delivery_logs: List[AlertDeliveryLogResponse] = []

        for sub in subscriptions:
            # Check cadence
            last_notified = ensure_utc(sub.last_notified_at)
            since_time = last_notified or (now - timedelta(days=1))
            if sub.alert_frequency == AlertFrequency.WEEKLY.value and last_notified:
                if (now - last_notified) < timedelta(days=7):
                    continue
            elif sub.alert_frequency == AlertFrequency.DAILY.value and last_notified:
                if (now - last_notified) < timedelta(hours=23):
                    continue

            # Query newly matching opportunities
            opp_q = select(CanonicalOpportunityRecord.id).where(
                CanonicalOpportunityRecord.is_suppressed.is_(False),
                CanonicalOpportunityRecord.is_active.is_(True),
                CanonicalOpportunityRecord.first_seen_at >= since_time,
            )

            # Apply saved query keywords
            kw = sub.query_json.get("query")
            if kw:
                term = f"%{kw.strip().lower()}%"
                opp_q = opp_q.where(
                    CanonicalOpportunityRecord.title.ilike(term) |
                    CanonicalOpportunityRecord.company_name.ilike(term) |
                    CanonicalOpportunityRecord.description_clean.ilike(term)
                )

            # Apply saved filters
            filters = sub.filters_json or {}
            if filters.get("is_remote") is not None:
                opp_q = opp_q.where(CanonicalOpportunityRecord.is_remote == filters["is_remote"])
            if filters.get("city"):
                opp_q = opp_q.where(CanonicalOpportunityRecord.city.ilike(f"%{filters['city']}%"))

            matching_opp_ids = session.execute(opp_q.limit(50)).scalars().all()

            if matching_opp_ids and not dry_run:
                log_rec = AlertDeliveryLogRecord(
                    saved_search_id=sub.id,
                    user_id=sub.user_id,
                    opportunity_ids_json=list(matching_opp_ids),
                    delivery_channel="IN_APP",
                    status="DELIVERED",
                    delivered_at=now,
                )
                session.add(log_rec)
                sub.last_notified_at = now
                session.commit()
                session.refresh(log_rec)

                delivery_logs.append(
                    AlertDeliveryLogResponse(
                        id=log_rec.id,
                        saved_search_id=sub.id,
                        user_id=sub.user_id,
                        opportunity_ids=list(matching_opp_ids),
                        delivered_at=log_rec.delivered_at,
                        delivery_channel=log_rec.delivery_channel,
                        status=log_rec.status,
                    )
                )

        return delivery_logs

    @classmethod
    def _to_saved_search_response(cls, record: SavedSearchRecord) -> SavedSearchResponse:
        return SavedSearchResponse(
            id=record.id,
            user_id=record.user_id,
            name=record.name,
            query_json=record.query_json or {},
            filters_json=record.filters_json or {},
            alert_enabled=record.alert_enabled,
            alert_frequency=AlertFrequency(record.alert_frequency),
            last_notified_at=record.last_notified_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
