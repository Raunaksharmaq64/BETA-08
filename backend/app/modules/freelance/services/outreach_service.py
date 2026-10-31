"""
Freelance Outreach Service — Candidate-governed draft generation, edit invalidation, and secure transmission.
"""

from __future__ import annotations

import hashlib
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import (
    FreelanceOpportunityRecord,
    OutreachDeliveryLogRecord,
    OutreachDraftRecord,
    User,
    utc_now,
)
from app.modules.freelance.repositories.freelance_repository import FreelanceRepository
from app.modules.freelance.services.mockup_service import MockupService
from app.modules.freelance.utils.ai_writer import AIOutreachWriter
from app.modules.freelance.utils.whatsapp import WhatsAppMessenger

logger = logging.getLogger(__name__)


class FreelanceOutreachService:
    """Manages outreach pitch drafting, mandatory approval state machine, and transmission."""

    @classmethod
    async def generate_draft(
        cls,
        session: AsyncSession,
        user_id: str,
        opportunity_id: str,
        channel: str = "EMAIL",
        tone: str = "professional",
        service: Optional[str] = None,
        project_sample: Optional[str] = None,
        refine_feedback: Optional[str] = None,
        min_words: int = 150,
    ) -> OutreachDraftRecord:
        repo = FreelanceRepository(session)
        opp = await repo.get_opportunity_by_id(opportunity_id)
        if not opp:
            raise ValueError(f"Freelance opportunity not found: {opportunity_id}")

        user_settings = await repo.get_candidate_settings(user_id)
        gemini_key = user_settings.encrypted_gemini_key if user_settings else None

        lead_data = {
            "name": opp.business_name,
            "category": opp.service_category,
            "city": opp.city,
            "rating": opp.rating,
            "reviews_count": opp.reviews_count,
            "website": opp.website,
            "is_broken_website": opp.is_broken_website,
        }

        sender_info = {
            "name": (user_settings.sender_name if user_settings else None) or "RightFit Growth Partner",
            "brand": (user_settings.sender_brand if user_settings else None) or "RightFit",
        }

        chosen_service = service or opp.suggested_service or "Website Technical Repair & Modern Redesign"

        if channel.upper() == "WHATSAPP":
            body = AIOutreachWriter.generate_pitch(
                lead_data=lead_data,
                project_sample=project_sample or "",
                tone=tone,
                service=chosen_service,
                sender_info=sender_info,
                api_key=gemini_key,
            )
            subject = f"Growth opportunity for {opp.business_name}"
            recipient_contact = opp.phone or ""
        else:
            subject, body = AIOutreachWriter.generate_email_pitch(
                lead_data=lead_data,
                project_sample=project_sample or "",
                tone=tone,
                service=chosen_service,
                sender_info=sender_info,
                api_key=gemini_key,
                min_words=min_words,
            )
            recipient_contact = opp.email or ""

        draft = OutreachDraftRecord(
            user_id=user_id,
            opportunity_id=opp.id,
            channel=channel.upper(),
            recipient_name=opp.business_name,
            recipient_contact=recipient_contact,
            subject=subject,
            message_body=body,
            proposed_service=chosen_service,
            status="DRAFT",
            is_approved=False,
            candidate_edits_count=0,
        )
        session.add(draft)
        await session.flush()
        return draft

    @classmethod
    async def update_draft(
        cls,
        session: AsyncSession,
        user_id: str,
        draft_id: str,
        subject: Optional[str] = None,
        message_body: Optional[str] = None,
        recipient_contact: Optional[str] = None,
    ) -> OutreachDraftRecord:
        repo = FreelanceRepository(session)
        draft = await repo.get_draft_by_id(draft_id, user_id=user_id)
        if not draft:
            raise ValueError(f"Outreach draft not found: {draft_id}")

        modified = False
        if subject is not None and subject != draft.subject:
            draft.subject = subject
            modified = True
        if message_body is not None and message_body != draft.message_body:
            draft.message_body = message_body
            modified = True
        if recipient_contact is not None and recipient_contact != draft.recipient_contact:
            draft.recipient_contact = recipient_contact
            modified = True

        if modified:
            # Edit invalidation rule: Any change resets prior approval
            draft.is_approved = False
            draft.approved_at = None
            draft.approved_recipient = None
            draft.approved_subject = None
            draft.approved_body_hash = None
            draft.status = "DRAFT"
            draft.candidate_edits_count += 1
            await session.flush()

        return draft

    @classmethod
    async def approve_draft(
        cls, session: AsyncSession, user_id: str, draft_id: str
    ) -> OutreachDraftRecord:
        repo = FreelanceRepository(session)
        draft = await repo.get_draft_by_id(draft_id, user_id=user_id)
        if not draft:
            raise ValueError(f"Outreach draft not found: {draft_id}")

        if not draft.recipient_contact or "@" not in draft.recipient_contact:
            if draft.channel == "EMAIL":
                raise ValueError("Valid recipient email contact is required before approving draft.")

        # Compute tamper-detection SHA-256 hash of approved body
        body_hash = hashlib.sha256(draft.message_body.encode("utf-8")).hexdigest()

        draft.is_approved = True
        draft.approved_at = utc_now()
        draft.approved_recipient = draft.recipient_contact
        draft.approved_subject = draft.subject
        draft.approved_body_hash = body_hash
        draft.status = "APPROVED"

        await session.flush()
        return draft

    @classmethod
    async def send_approved_draft(
        cls, session: AsyncSession, user_id: str, draft_id: str
    ) -> OutreachDeliveryLogRecord:
        repo = FreelanceRepository(session)
        draft = await repo.get_draft_by_id(draft_id, user_id=user_id)
        if not draft:
            raise ValueError(f"Outreach draft not found: {draft_id}")

        if not draft.is_approved:
            raise PermissionError("Outreach transmission rejected: Draft requires explicit candidate approval.")

        # Re-verify body integrity
        current_hash = hashlib.sha256(draft.message_body.encode("utf-8")).hexdigest()
        if current_hash != draft.approved_body_hash:
            draft.is_approved = False
            draft.status = "DRAFT"
            await session.flush()
            raise PermissionError("Outreach transmission rejected: Draft body was modified after approval.")

        # Check suppression list
        is_suppressed = await repo.is_contact_suppressed(draft.recipient_contact)
        if is_suppressed:
            log = OutreachDeliveryLogRecord(
                draft_id=draft.id,
                provider="SUPPRESSION_LIST",
                provider_response_code=403,
                provider_raw_response="Recipient address is on the do-not-contact suppression list.",
                delivery_status="SUPPRESSED",
                error_message="Recipient has unsubscribed or opted out.",
                event_timestamp=utc_now(),
            )
            session.add(log)
            draft.status = "SUPPRESSED"
            await session.flush()
            return log

        # Dispatch via configured SMTP or development sandbox
        user_settings = await repo.get_candidate_settings(user_id)
        provider = "SMTP"
        response_code = 250
        raw_resp = "Message accepted for delivery."

        try:
            if user_settings and user_settings.smtp_host and user_settings.smtp_email and user_settings.encrypted_smtp_password:
                # Real SMTP dispatch using user's BYOK inbox
                msg = MIMEMultipart()
                msg["From"] = user_settings.smtp_email
                msg["To"] = draft.recipient_contact
                msg["Subject"] = draft.subject
                msg.attach(MIMEText(draft.message_body, "plain"))

                if user_settings.smtp_use_ssl:
                    server = smtplib.SMTP_SSL(user_settings.smtp_host, user_settings.smtp_port, timeout=10)
                else:
                    server = smtplib.SMTP(user_settings.smtp_host, user_settings.smtp_port, timeout=10)
                    server.starttls()

                server.login(user_settings.smtp_email, user_settings.encrypted_smtp_password)
                server.send_message(msg)
                server.quit()
                raw_resp = "Dispatched via configured custom SMTP relay."
            else:
                # Development/Demo sandbox dispatch
                provider = "SANDBOX_MOCK"
                raw_resp = "Simulated delivery in sandbox environment (no SMTP inbox configured)."
        except Exception as e:
            logger.error(f"[OutreachService] Failed to dispatch email: {e}")
            log = OutreachDeliveryLogRecord(
                draft_id=draft.id,
                provider=provider,
                provider_response_code=500,
                provider_raw_response=str(e),
                delivery_status="FAILED",
                error_message=str(e),
                event_timestamp=utc_now(),
            )
            session.add(log)
            draft.status = "FAILED"
            await session.flush()
            raise RuntimeError(f"Email delivery failed: {e}") from e

        log = OutreachDeliveryLogRecord(
            draft_id=draft.id,
            provider=provider,
            provider_message_id=f"msg_{draft.id[:8]}",
            provider_response_code=response_code,
            provider_raw_response=raw_resp,
            delivery_status="SENT",
            event_timestamp=utc_now(),
        )
        session.add(log)
        draft.status = "SENT"
        await session.flush()
        return log

    @classmethod
    def generate_whatsapp_link(cls, phone: str, message: str) -> str:
        return WhatsAppMessenger.generate_whatsapp_link(phone, message)
