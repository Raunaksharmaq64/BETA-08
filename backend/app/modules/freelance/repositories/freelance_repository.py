"""
Freelance Repository — Async database operations for freelance opportunities, evidence, history, and outreach.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    ContactEvidenceRecord,
    FreelanceCandidateSettingsRecord,
    FreelanceOpportunityRecord,
    FreelanceSearchHistoryRecord,
    OutreachDeliveryLogRecord,
    OutreachDraftRecord,
    OutreachSuppressionRecord,
    SavedFreelanceOpportunityRecord,
    utc_now,
)

logger = logging.getLogger(__name__)


class FreelanceRepository:
    """Encapsulates all Core database queries for Freelance Intelligence."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # -------------------------------------------------------------------------
    # 1. Opportunities & Evidence
    # -------------------------------------------------------------------------

    async def list_opportunities(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        classification_state: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FreelanceOpportunityRecord]:
        stmt = (
            select(FreelanceOpportunityRecord)
            .options(
                selectinload(FreelanceOpportunityRecord.contact_evidence),
                selectinload(FreelanceOpportunityRecord.drafts),
            )
            .order_by(desc(FreelanceOpportunityRecord.discovered_at))
        )

        conditions = []
        if city:
            conditions.append(func.lower(FreelanceOpportunityRecord.city) == city.lower())
        if category:
            conditions.append(func.lower(FreelanceOpportunityRecord.service_category) == category.lower())
        if classification_state and classification_state != "ALL":
            conditions.append(FreelanceOpportunityRecord.classification_state == classification_state)
        if query:
            q_lower = f"%{query.lower()}%"
            conditions.append(
                or_(
                    func.lower(FreelanceOpportunityRecord.business_name).like(q_lower),
                    func.lower(FreelanceOpportunityRecord.city).like(q_lower),
                    func.lower(FreelanceOpportunityRecord.service_category).like(q_lower),
                    func.lower(FreelanceOpportunityRecord.description).like(q_lower),
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[FreelanceOpportunityRecord]:
        stmt = (
            select(FreelanceOpportunityRecord)
            .options(
                selectinload(FreelanceOpportunityRecord.contact_evidence),
                selectinload(FreelanceOpportunityRecord.drafts),
                selectinload(FreelanceOpportunityRecord.saved_by),
            )
            .where(FreelanceOpportunityRecord.id == opportunity_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_existing_opportunity(
        self,
        place_id: Optional[str] = None,
        leadhunter_id: Optional[str] = None,
        business_name: Optional[str] = None,
        city: Optional[str] = None,
    ) -> Optional[FreelanceOpportunityRecord]:
        """Multi-signal lookup to prevent duplicates."""
        clauses = []
        if place_id:
            clauses.append(FreelanceOpportunityRecord.place_id == place_id)
        if leadhunter_id:
            clauses.append(FreelanceOpportunityRecord.leadhunter_lead_id == leadhunter_id)
        if business_name and city:
            clauses.append(
                and_(
                    func.lower(FreelanceOpportunityRecord.business_name) == business_name.lower().strip(),
                    func.lower(FreelanceOpportunityRecord.city) == city.lower().strip(),
                )
            )

        if not clauses:
            return None

        stmt = select(FreelanceOpportunityRecord).where(or_(*clauses))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # -------------------------------------------------------------------------
    # 2. Bookmarks & Saved Opportunities
    # -------------------------------------------------------------------------

    async def get_saved_opportunity(
        self, user_id: str, opportunity_id: str
    ) -> Optional[SavedFreelanceOpportunityRecord]:
        stmt = select(SavedFreelanceOpportunityRecord).where(
            SavedFreelanceOpportunityRecord.user_id == user_id,
            SavedFreelanceOpportunityRecord.opportunity_id == opportunity_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_saved_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(SavedFreelanceOpportunityRecord)
            .options(selectinload(SavedFreelanceOpportunityRecord.opportunity))
            .where(SavedFreelanceOpportunityRecord.user_id == user_id)
            .order_by(desc(SavedFreelanceOpportunityRecord.created_at))
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        output = []
        for r in records:
            opp = r.opportunity
            output.append({
                "bookmark_id": r.id,
                "opportunity_id": r.opportunity_id,
                "status": r.status,
                "notes": r.notes,
                "saved_at": r.created_at.isoformat() if r.created_at else None,
                "opportunity": {
                    "id": opp.id,
                    "business_name": opp.business_name,
                    "opportunity_title": opp.opportunity_title,
                    "service_category": opp.service_category,
                    "city": opp.city,
                    "website": opp.website,
                    "is_broken_website": opp.is_broken_website,
                    "rating": opp.rating,
                    "reviews_count": opp.reviews_count,
                    "phone": opp.phone,
                    "email": opp.email,
                    "classification_state": opp.classification_state,
                    "relevance_score": opp.relevance_score,
                } if opp else None,
            })
        return output

    async def save_opportunity(
        self, user_id: str, opportunity_id: str, notes: Optional[str] = None
    ) -> SavedFreelanceOpportunityRecord:
        existing = await self.get_saved_opportunity(user_id, opportunity_id)
        if existing:
            if notes is not None:
                existing.notes = notes
            return existing

        new_saved = SavedFreelanceOpportunityRecord(
            user_id=user_id,
            opportunity_id=opportunity_id,
            notes=notes,
            status="SAVED",
        )
        self.session.add(new_saved)
        await self.session.flush()
        return new_saved

    async def remove_saved_opportunity(self, user_id: str, opportunity_id: str) -> bool:
        existing = await self.get_saved_opportunity(user_id, opportunity_id)
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
            return True
        return False

    # -------------------------------------------------------------------------
    # 3. Search History
    # -------------------------------------------------------------------------

    async def save_search_history(
        self,
        user_id: str,
        query: str,
        city: str,
        results_count: int,
        leads_count: int,
        deep_scan: bool = False,
        zones: Optional[List[str]] = None,
        include_with_website: bool = False,
    ) -> FreelanceSearchHistoryRecord:
        record = FreelanceSearchHistoryRecord(
            user_id=user_id,
            query=query,
            city=city,
            results_count=results_count,
            leads_count=leads_count,
            deep_scan=deep_scan,
            zones=",".join(zones) if zones else None,
            include_with_website=include_with_website,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_search_history(self, user_id: str, limit: int = 20) -> List[FreelanceSearchHistoryRecord]:
        stmt = (
            select(FreelanceSearchHistoryRecord)
            .where(FreelanceSearchHistoryRecord.user_id == user_id)
            .order_by(desc(FreelanceSearchHistoryRecord.searched_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # 4. Outreach Drafts & Delivery
    # -------------------------------------------------------------------------

    async def get_draft_by_id(self, draft_id: str, user_id: Optional[str] = None) -> Optional[OutreachDraftRecord]:
        stmt = (
            select(OutreachDraftRecord)
            .options(
                selectinload(OutreachDraftRecord.opportunity),
                selectinload(OutreachDraftRecord.delivery_logs),
            )
            .where(OutreachDraftRecord.id == draft_id)
        )
        if user_id:
            stmt = stmt.where(OutreachDraftRecord.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_drafts_for_user(self, user_id: str, limit: int = 50) -> List[OutreachDraftRecord]:
        stmt = (
            select(OutreachDraftRecord)
            .options(
                selectinload(OutreachDraftRecord.opportunity),
                selectinload(OutreachDraftRecord.delivery_logs),
            )
            .where(OutreachDraftRecord.user_id == user_id)
            .order_by(desc(OutreachDraftRecord.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def is_contact_suppressed(self, recipient_contact: str) -> bool:
        clean = recipient_contact.strip().lower()
        stmt = select(OutreachSuppressionRecord).where(
            func.lower(OutreachSuppressionRecord.recipient_value) == clean
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def add_suppression(
        self, recipient_contact: str, reason: str = "UNSUBSCRIBED", user_id: Optional[str] = None
    ) -> OutreachSuppressionRecord:
        clean = recipient_contact.strip().lower()
        stmt = select(OutreachSuppressionRecord).where(
            func.lower(OutreachSuppressionRecord.recipient_value) == clean
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()
        if existing:
            return existing

        record = OutreachSuppressionRecord(
            recipient_value=clean,
            reason=reason,
            created_by_user_id=user_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    # -------------------------------------------------------------------------
    # 5. Candidate Freelance Settings (BYOK Keys)
    # -------------------------------------------------------------------------

    async def get_candidate_settings(self, user_id: str) -> Optional[FreelanceCandidateSettingsRecord]:
        stmt = select(FreelanceCandidateSettingsRecord).where(
            FreelanceCandidateSettingsRecord.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_candidate_settings(self, user_id: str) -> FreelanceCandidateSettingsRecord:
        existing = await self.get_candidate_settings(user_id)
        if existing:
            return existing

        settings_rec = FreelanceCandidateSettingsRecord(user_id=user_id)
        self.session.add(settings_rec)
        await self.session.flush()
        return settings_rec
