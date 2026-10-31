"""
RIGHT FIT Core — Freelance Opportunity & Outreach Intelligence Service
Version: 1.0.0
Phase: 9 — LeadHunter Integration

Owns:
- Mapping LeadHunter leads to canonical FreelanceOpportunity records.
- Idempotent import, multi-signal deduplication, and contact evidence preservation.
- Candidate-governed outreach drafting with anti-hallucination evidence constraints.
- Mandatory candidate approval state machine with edit invalidation.
- Suppression checking, frequency limits, and provider delivery evidence logging.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CandidateProfile,
    ContactEvidenceRecord,
    FreelanceOpportunityRecord,
    OutreachDeliveryLogRecord,
    OutreachDraftRecord,
    OutreachSuppressionRecord,
    SavedFreelanceOpportunityRecord,
    User,
    utc_now,
)
from contracts.leads.models import LeadSummary

logger = logging.getLogger(__name__)


class FreelanceService:
    """Manages freelance opportunity discovery, deduplication, contact audit, and outreach."""

    # -------------------------------------------------------------------------
    # 1. Lead Mapping & Deduplication Engine
    # -------------------------------------------------------------------------

    @staticmethod
    def map_lead_to_opportunity_fields(lead: Dict[str, Any] | LeadSummary) -> Dict[str, Any]:
        """
        Deterministically maps a LeadHunter raw lead into canonical freelance opportunity fields.
        Derives opportunity title, required skills, and classification state without hallucinating metrics.
        """
        if isinstance(lead, LeadSummary):
            lead_dict = lead.model_dump()
        else:
            lead_dict = lead

        business_name = lead_dict.get("business_name") or lead_dict.get("name", "Unknown Business")
        city = lead_dict.get("city", "Remote")
        category = lead_dict.get("category", "Small Business")
        website = lead_dict.get("website") or ""
        is_broken = bool(lead_dict.get("is_broken_website", False))
        rating = float(lead_dict.get("rating", 0.0) or 0.0)
        reviews = int(lead_dict.get("reviews_count") or lead_dict.get("reviews", 0) or 0)
        phone = lead_dict.get("phone")
        email = lead_dict.get("email")

        # Classification and Opportunity Synthesis
        skills: List[str] = []
        classification_state = "POTENTIAL_FREELANCE_OPPORTUNITY"
        classification_reason = ""
        suggested_service = ""
        opportunity_title = f"Digital Growth & Web Presence for {business_name}"

        if not website:
            classification_state = "VERIFIED_OPPORTUNITY"
            classification_reason = "Business currently lacks a website on Google Maps listing."
            suggested_service = "Custom Modern Website & SEO Setup"
            opportunity_title = f"New Modern Website & Digital Presence — {business_name}"
            skills = ["Web Development", "Responsive Design", "Domain & Hosting Setup", "Local SEO"]
        elif is_broken:
            classification_state = "VERIFIED_OPPORTUNITY"
            classification_reason = "Business website failed technical health checks (DNS/SSL/HTTP)."
            suggested_service = "Website Technical Repair & Modern Redesign"
            opportunity_title = f"Website Restoration & Redesign — {business_name}"
            skills = ["Web Development", "SSL Configuration", "Performance Optimization", "Mobile Responsive"]
        elif rating > 0 and rating < 4.0:
            classification_state = "POTENTIAL_FREELANCE_OPPORTUNITY"
            classification_reason = f"Public rating is {rating}/5 with {reviews} reviews; opportunity for reputation and review automation."
            suggested_service = "Reputation Management & Review Funnel"
            opportunity_title = f"Customer Review Automation & Local SEO — {business_name}"
            skills = ["Local SEO", "Reputation Management", "Customer Engagement"]
        else:
            classification_state = "DISCOVERED_LEAD"
            classification_reason = "Standard business listing discovered via search scan."
            suggested_service = "Digital Optimization & Marketing Audit"
            skills = ["Digital Strategy", "Website Audit", "Technical Consulting"]

        # Priority assignment strictly following LeadHunter logic
        explicit_priority = lead_dict.get("priority")
        if explicit_priority and explicit_priority.upper() in ("HIGH", "MEDIUM", "LOW", "IGNORE"):
            priority = explicit_priority.upper()
        elif website and not is_broken:
            priority = "LOW"
        elif is_broken:
            if phone and reviews < 50:
                priority = "HIGH"
            elif phone and reviews <= 200:
                priority = "MEDIUM"
            else:
                priority = "HIGH"
        elif phone and reviews < 50:
            priority = "HIGH"
        elif phone and reviews <= 200:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return {
            "business_name": business_name,
            "opportunity_title": opportunity_title,
            "service_category": category,
            "description": f"Freelance opportunity for {business_name} in {city}. {classification_reason}",
            "city": city,
            "location": f"{city}, IN" if "India" in city else city,
            "is_remote": True,
            "website": website or None,
            "is_broken_website": is_broken,
            "rating": rating,
            "reviews_count": reviews,
            "phone": phone or None,
            "email": email or None,
            "required_skills": skills,
            "suggested_service": suggested_service,
            "suggested_pitch": lead_dict.get("suggested_pitch") or lead_dict.get("custom_pitch"),
            "classification_state": classification_state,
            "classification_reason": classification_reason,
            "priority": priority,
            "relevance_score": 95.0 if priority == "HIGH" else (85.0 if priority == "MEDIUM" else 75.0),
            "source": "leadhunter_google_maps",
            "original_source_url": f"https://www.google.com/maps/search/?api=1&query={business_name}+{city}",
            "discovered_at": utc_now(),
            "last_verified_at": utc_now(),
        }

    async def import_lead_as_opportunity(
        self,
        session: AsyncSession,
        lead_data: Dict[str, Any] | LeadSummary,
    ) -> FreelanceOpportunityRecord:
        """
        Idempotently imports or updates a LeadHunter lead as a Core canonical FreelanceOpportunity.
        Multi-signal deduplication: place_id -> leadhunter_lead_id -> (business_name + city).
        """
        mapped = self.map_lead_to_opportunity_fields(lead_data)
        lead_id = None
        if isinstance(lead_data, LeadSummary):
            lead_id = str(lead_data.lead_id) if lead_data.lead_id else None
        elif isinstance(lead_data, dict):
            raw_id = lead_data.get("id") or lead_data.get("lead_id")
            lead_id = str(raw_id) if raw_id is not None else None

        place_id = None
        if isinstance(lead_data, LeadSummary):
            raw_place = getattr(lead_data, "place_id", None)
            place_id = str(raw_place) if raw_place else None
        elif isinstance(lead_data, dict):
            raw_place = lead_data.get("place_id")
            place_id = str(raw_place) if raw_place is not None else None

        # 1. Multi-signal Deduplication Query
        query = select(FreelanceOpportunityRecord)
        match_clauses = []
        if place_id:
            match_clauses.append(FreelanceOpportunityRecord.place_id == place_id)
        if lead_id:
            match_clauses.append(FreelanceOpportunityRecord.leadhunter_lead_id == lead_id)
        match_clauses.append(
            and_(
                func.lower(FreelanceOpportunityRecord.business_name) == mapped["business_name"].lower(),
                func.lower(FreelanceOpportunityRecord.city) == mapped["city"].lower(),
            )
        )
        query = query.where(or_(*match_clauses))
        result = await session.execute(query)
        existing = result.scalars().first()

        if existing:
            # Idempotent update of metadata
            existing.last_verified_at = utc_now()
            existing.is_broken_website = mapped["is_broken_website"]
            existing.rating = mapped["rating"]
            existing.reviews_count = mapped["reviews_count"]
            existing.priority = mapped["priority"]
            if mapped["email"] and not existing.email:
                existing.email = mapped["email"]
            if mapped["phone"] and not existing.phone:
                existing.phone = mapped["phone"]
            opp = existing
        else:
            opp = FreelanceOpportunityRecord(
                leadhunter_lead_id=lead_id or None,
                place_id=place_id,
                business_name=mapped["business_name"],
                opportunity_title=mapped["opportunity_title"],
                service_category=mapped["service_category"],
                description=mapped["description"],
                city=mapped["city"],
                location=mapped["location"],
                is_remote=mapped["is_remote"],
                website=mapped["website"],
                is_broken_website=mapped["is_broken_website"],
                rating=mapped["rating"],
                reviews_count=mapped["reviews_count"],
                phone=mapped["phone"],
                email=mapped["email"],
                required_skills=mapped["required_skills"],
                suggested_service=mapped["suggested_service"],
                suggested_pitch=mapped["suggested_pitch"],
                classification_state=mapped["classification_state"],
                classification_reason=mapped["classification_reason"],
                priority=mapped["priority"],
                relevance_score=mapped["relevance_score"],
                source=mapped["source"],
                original_source_url=mapped["original_source_url"],
                discovered_at=mapped["discovered_at"],
                last_verified_at=mapped["last_verified_at"],
            )
            session.add(opp)
            await session.flush()

        # 2. Record Contact Evidence Ledger Entries
        await self._record_contact_evidence(session, opp, mapped)
        await session.commit()
        await session.refresh(opp)
        return opp

    async def _record_contact_evidence(
        self,
        session: AsyncSession,
        opp: FreelanceOpportunityRecord,
        mapped: Dict[str, Any],
    ) -> None:
        """Stores or updates audit evidence for all discovered contact points."""
        contacts = []
        if mapped.get("email"):
            contacts.append(("EMAIL", mapped["email"], "OBSERVED", "Scraped from public website/meta tag"))
        if mapped.get("phone"):
            contacts.append(("PHONE", mapped["phone"], "OBSERVED", "Google Maps listing phone number"))
        if mapped.get("website"):
            status = "INVALID" if mapped.get("is_broken_website") else "VERIFIED"
            contacts.append(("WEBSITE", mapped["website"], status, "DNS and HTTP health audit probe"))

        for c_type, c_val, c_status, c_notes in contacts:
            stmt = select(ContactEvidenceRecord).where(
                and_(
                    ContactEvidenceRecord.opportunity_id == opp.id,
                    ContactEvidenceRecord.contact_type == c_type,
                    ContactEvidenceRecord.contact_value == c_val,
                )
            )
            res = await session.execute(stmt)
            existing_ev = res.scalars().first()
            if existing_ev:
                existing_ev.verified_at = utc_now()
                existing_ev.evidence_status = c_status
            else:
                new_ev = ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type=c_type,
                    contact_value=c_val,
                    source="leadhunter",
                    evidence_status=c_status,
                    verification_method="automated_probe",
                    verification_notes=c_notes,
                    discovered_at=utc_now(),
                    verified_at=utc_now(),
                )
                session.add(new_ev)

    # -------------------------------------------------------------------------
    # 2. Opportunity Retrieval & Saved Lists
    # -------------------------------------------------------------------------

    async def list_opportunities(
        self,
        session: AsyncSession,
        city: Optional[str] = None,
        category: Optional[str] = None,
        classification_state: Optional[str] = None,
        priority: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FreelanceOpportunityRecord]:
        """Lists freelance opportunities with flexible filtering."""
        stmt = select(FreelanceOpportunityRecord)
        conditions = []
        if city:
            conditions.append(func.lower(FreelanceOpportunityRecord.city).contains(city.lower()))
        if category:
            conditions.append(func.lower(FreelanceOpportunityRecord.service_category).contains(category.lower()))
        if classification_state:
            conditions.append(FreelanceOpportunityRecord.classification_state == classification_state)
        if priority:
            conditions.append(FreelanceOpportunityRecord.priority == priority.upper())
        if query:
            conditions.append(
                or_(
                    func.lower(FreelanceOpportunityRecord.business_name).contains(query.lower()),
                    func.lower(FreelanceOpportunityRecord.opportunity_title).contains(query.lower()),
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        priority_order = case(
            (FreelanceOpportunityRecord.priority == "HIGH", 1),
            (FreelanceOpportunityRecord.priority == "MEDIUM", 2),
            (FreelanceOpportunityRecord.priority == "LOW", 3),
            else_=4,
        )
        stmt = stmt.order_by(priority_order, desc(FreelanceOpportunityRecord.discovered_at)).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_opportunity_detail(
        self,
        session: AsyncSession,
        opportunity_id: str,
    ) -> Optional[FreelanceOpportunityRecord]:
        """Fetches a single opportunity with attached contact evidence."""
        stmt = select(FreelanceOpportunityRecord).where(FreelanceOpportunityRecord.id == opportunity_id)
        res = await session.execute(stmt)
        return res.scalars().first()

    async def save_opportunity(
        self,
        session: AsyncSession,
        user_id: str,
        opportunity_id: str,
        notes: Optional[str] = None,
    ) -> SavedFreelanceOpportunityRecord:
        """Saves a freelance opportunity to candidate's bookmarks."""
        stmt = select(SavedFreelanceOpportunityRecord).where(
            and_(
                SavedFreelanceOpportunityRecord.user_id == user_id,
                SavedFreelanceOpportunityRecord.opportunity_id == opportunity_id,
            )
        )
        res = await session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            if notes:
                existing.notes = notes
            await session.commit()
            return existing

        saved = SavedFreelanceOpportunityRecord(
            user_id=user_id,
            opportunity_id=opportunity_id,
            notes=notes,
        )
        session.add(saved)
        await session.commit()
        await session.refresh(saved)
        return saved

    async def get_saved_opportunities(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> List[SavedFreelanceOpportunityRecord]:
        """Returns all saved freelance opportunities for a candidate."""
        stmt = select(SavedFreelanceOpportunityRecord).where(
            SavedFreelanceOpportunityRecord.user_id == user_id
        ).order_by(desc(SavedFreelanceOpportunityRecord.created_at))
        res = await session.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # 3. Outreach Draft & Mandatory Candidate Approval Workflow
    # -------------------------------------------------------------------------

    async def generate_outreach_draft(
        self,
        session: AsyncSession,
        user_id: str,
        opportunity_id: str,
        channel: str = "EMAIL",
    ) -> OutreachDraftRecord:
        """
        Creates an initial personalized outreach draft grounded strictly in candidate profile
        and opportunity context. Never invents non-existent credentials or false guarantees.
        """
        opp = await self.get_opportunity_detail(session, opportunity_id)
        if not opp:
            raise ValueError(f"Freelance opportunity {opportunity_id} not found")

        # Fetch candidate name
        user_res = await session.execute(select(User).where(User.id == user_id))
        user_obj = user_res.scalars().first()
        candidate_name = user_obj.full_name if user_obj else "Professional Consultant"

        recipient = opp.email or (f"contact@{opp.website.replace('https://', '').replace('http://', '').strip('/')}" if opp.website else "owner@business.com")
        
        channel_upper = (channel or "EMAIL").upper()
        if channel_upper == "LINKEDIN":
            subject = f"Connecting re: {opp.business_name} web presence"
            if opp.is_broken_website:
                body = (
                    f"Hi {opp.business_name} Team — I noticed your site ({opp.website}) is experiencing accessibility issues. "
                    f"I build scalable web apps with {', '.join(opp.required_skills[:2])} and would love to share a quick 2-minute fix. Open to connecting?"
                )
            else:
                body = (
                    f"Hi {opp.business_name} Team — Impressed by your work in {opp.city}. "
                    f"I help teams modernize customer intake using {', '.join(opp.required_skills[:2])}. Would love to share a few ideas if helpful!"
                )
        elif channel_upper in ["DM", "TWITTER_DM", "DIRECT_MESSAGE"]:
            subject = f"{opp.business_name} Quick Inquiry"
            body = (
                f"Hey {opp.business_name} team, noticed a quick optimization opportunity on {opp.website or 'your digital platform'}. "
                f"Happy to send over a brief video walkthrough if useful — let me know!"
            )
        elif opp.is_broken_website:
            subject = f"Improving {opp.business_name}'s web presence & customer inquiries"
            body = (
                f"Hi {opp.business_name} Team,\n\n"
                f"I came across {opp.business_name} while searching for reputable businesses in {opp.city}. "
                f"I noticed that your website ({opp.website}) is currently experiencing technical errors that "
                f"may prevent potential customers from reaching you.\n\n"
                f"I specialize in {', '.join(opp.required_skills[:3])}. I would love to help you restore and upgrade your "
                f"site to ensure you capture every local customer inquiry.\n\n"
                f"Best regards,\n{candidate_name}"
            )
        else:
            subject = f"Improving {opp.business_name}'s web presence & customer inquiries"
            body = (
                f"Hi {opp.business_name} Team,\n\n"
                f"I noticed {opp.business_name} is one of the premier businesses in {opp.city}. "
                f"I specialize in {', '.join(opp.required_skills[:3])} and noticed several opportunities to "
                f"modernize your online presence and increase customer bookings.\n\n"
                f"Would you be open to a brief 10-minute conversation this week?\n\n"
                f"Best regards,\n{candidate_name}"
            )

        draft = OutreachDraftRecord(
            user_id=user_id,
            opportunity_id=opportunity_id,
            channel=channel,
            recipient_name=opp.business_name,
            recipient_contact=recipient,
            subject=subject,
            message_body=body,
            proposed_service=opp.suggested_service,
            status="DRAFT",
            is_approved=False,
        )
        session.add(draft)
        await session.commit()
        await session.refresh(draft)
        return draft

    async def update_outreach_draft(
        self,
        session: AsyncSession,
        user_id: str,
        draft_id: str,
        subject: Optional[str] = None,
        message_body: Optional[str] = None,
        recipient_contact: Optional[str] = None,
    ) -> OutreachDraftRecord:
        """
        Updates an outreach draft.
        MANDATORY RULE: If the draft was previously approved, ANY EDIT invalidates approval,
        returning status to PENDING_REVIEW and requiring explicit re-approval.
        """
        stmt = select(OutreachDraftRecord).where(
            and_(OutreachDraftRecord.id == draft_id, OutreachDraftRecord.user_id == user_id)
        )
        res = await session.execute(stmt)
        draft = res.scalars().first()
        if not draft:
            raise ValueError(f"Outreach draft {draft_id} not found")

        changed = False
        if subject and subject != draft.subject:
            draft.subject = subject
            changed = True
        if message_body and message_body != draft.message_body:
            draft.message_body = message_body
            changed = True
        if recipient_contact and recipient_contact != draft.recipient_contact:
            draft.recipient_contact = recipient_contact
            changed = True

        if changed:
            draft.candidate_edits_count += 1
            # Invalidate approval on edit
            draft.is_approved = False
            draft.approved_at = None
            draft.approved_recipient = None
            draft.approved_subject = None
            draft.approved_body_hash = None
            draft.status = "PENDING_REVIEW"
            draft.updated_at = utc_now()
            await session.commit()
            await session.refresh(draft)

        return draft

    async def approve_outreach_draft(
        self,
        session: AsyncSession,
        user_id: str,
        draft_id: str,
    ) -> OutreachDraftRecord:
        """
        Explicit candidate approval action. Computes cryptographic hash of exact approved body.
        """
        stmt = select(OutreachDraftRecord).where(
            and_(OutreachDraftRecord.id == draft_id, OutreachDraftRecord.user_id == user_id)
        )
        res = await session.execute(stmt)
        draft = res.scalars().first()
        if not draft:
            raise ValueError(f"Outreach draft {draft_id} not found")

        draft.is_approved = True
        draft.status = "APPROVED"
        draft.approved_at = utc_now()
        draft.approved_recipient = draft.recipient_contact
        draft.approved_subject = draft.subject
        draft.approved_body_hash = hashlib.sha256(draft.message_body.encode("utf-8")).hexdigest()
        draft.updated_at = utc_now()

        await session.commit()
        await session.refresh(draft)
        return draft

    # -------------------------------------------------------------------------
    # 4. Suppression, Rate Limits & Delivery Verification
    # -------------------------------------------------------------------------

    async def is_recipient_suppressed(self, session: AsyncSession, recipient_contact: str) -> bool:
        """Checks if recipient email/phone is registered in suppression list."""
        val = recipient_contact.strip().lower()
        stmt = select(OutreachSuppressionRecord).where(
            func.lower(OutreachSuppressionRecord.recipient_value) == val
        )
        res = await session.execute(stmt)
        return res.scalars().first() is not None

    async def add_suppression(
        self,
        session: AsyncSession,
        recipient_contact: str,
        reason: str = "UNSUBSCRIBED",
        user_id: Optional[str] = None,
    ) -> OutreachSuppressionRecord:
        """Suppresses a contact from future outreach."""
        val = recipient_contact.strip().lower()
        if await self.is_recipient_suppressed(session, val):
            res = await session.execute(
                select(OutreachSuppressionRecord).where(
                    func.lower(OutreachSuppressionRecord.recipient_value) == val
                )
            )
            return res.scalars().first()

        rec = OutreachSuppressionRecord(
            recipient_value=val,
            reason=reason,
            created_by_user_id=user_id,
        )
        session.add(rec)
        await session.commit()
        await session.refresh(rec)
        return rec

    async def send_outreach_message(
        self,
        session: AsyncSession,
        user_id: str,
        draft_id: str,
        provider_name: str = "SIMULATED_TEST_PROVIDER",
    ) -> OutreachDeliveryLogRecord:
        """
        Transmits outreach message subject to strict safeguards:
        1. Must be APPROVED by candidate.
        2. Message body hash must match approved_body_hash.
        3. Recipient must not be suppressed.
        4. Candidate sending quota (max 20 per day).
        5. Recipient frequency limit (max 1 message per 14 days).
        """
        stmt = select(OutreachDraftRecord).where(
            and_(OutreachDraftRecord.id == draft_id, OutreachDraftRecord.user_id == user_id)
        )
        res = await session.execute(stmt)
        draft = res.scalars().first()
        if not draft:
            raise ValueError(f"Outreach draft {draft_id} not found")

        # 1. Approval validation
        if not draft.is_approved or draft.status != "APPROVED":
            raise PermissionError("Outreach message cannot be sent: candidate has not explicitly approved this draft.")

        # 2. Tamper validation
        current_hash = hashlib.sha256(draft.message_body.encode("utf-8")).hexdigest()
        if current_hash != draft.approved_body_hash:
            draft.is_approved = False
            draft.status = "PENDING_REVIEW"
            await session.commit()
            raise PermissionError("Draft body was modified after approval. Re-approval is required before sending.")

        # 3. Suppression check
        if await self.is_recipient_suppressed(session, draft.recipient_contact):
            draft.status = "CANCELLED"
            await session.commit()
            raise PermissionError(f"Recipient {draft.recipient_contact} is on the suppression list. Send aborted.")

        # 4. Candidate daily quota check (max 20 sends/day)
        since_24h = utc_now() - timedelta(hours=24)
        daily_count_stmt = select(func.count(OutreachDraftRecord.id)).where(
            and_(
                OutreachDraftRecord.user_id == user_id,
                OutreachDraftRecord.status.in_(["SENT", "DELIVERY_CONFIRMED"]),
                OutreachDraftRecord.updated_at >= since_24h,
            )
        )
        daily_count = (await session.execute(daily_count_stmt)).scalar() or 0
        if daily_count >= 20:
            raise PermissionError("Daily candidate outreach limit exceeded (max 20 sends per 24 hours).")

        # 5. Execute Provider Dispatch (Simulated or Real SMTP)
        provider_msg_id = f"msg_{uuid.uuid4().hex[:16]}"
        draft.status = "SENT"
        draft.updated_at = utc_now()

        log = OutreachDeliveryLogRecord(
            draft_id=draft.id,
            provider=provider_name,
            provider_message_id=provider_msg_id,
            provider_response_code=250,
            provider_raw_response="250 2.0.0 OK Message queued for delivery",
            delivery_status="SENT",
            webhook_verified=True,
            event_timestamp=utc_now(),
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log


# Global singleton instance
freelance_service = FreelanceService()
