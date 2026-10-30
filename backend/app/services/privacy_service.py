"""
RIGHT FIT Core — Privacy & Consent Management Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ConsentRecord, PrivacySettingsRecord, utc_now
from app.services.audit_service import AuditService
from contracts.privacy.schemas import (
    ConsentGrantRequest,
    ConsentRecordResponse,
    PrivacySettingsResponse,
    PrivacySettingsUpdate,
    ProfileVisibility,
)
from contracts.security.audit import AuditEventType


class PrivacyService:
    @staticmethod
    async def get_or_create_settings(db: AsyncSession, user_id: str) -> PrivacySettingsRecord:
        """Retrieves or provisions default privacy preferences."""
        query = select(PrivacySettingsRecord).where(PrivacySettingsRecord.user_id == user_id)
        res = await db.execute(query)
        settings = res.scalar_one_or_none()

        if not settings:
            settings = PrivacySettingsRecord(
                user_id=user_id,
                profile_visibility="PUBLIC",
                opportunity_alerts=True,
                email_notifications=True,
                ai_processing_enabled=True,
                data_usage_research=False,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)

        return settings

    @staticmethod
    async def get_privacy_settings(db: AsyncSession, user_id: str) -> PrivacySettingsResponse:
        """Returns privacy preferences."""
        record = await PrivacyService.get_or_create_settings(db, user_id)
        return PrivacySettingsResponse(
            id=record.id,
            user_id=record.user_id,
            profile_visibility=ProfileVisibility(record.profile_visibility),
            opportunity_alerts=record.opportunity_alerts,
            email_notifications=record.email_notifications,
            ai_processing_enabled=record.ai_processing_enabled,
            data_usage_research=record.data_usage_research,
            updated_at=record.updated_at,
        )

    @staticmethod
    async def update_privacy_settings(
        db: AsyncSession,
        user_id: str,
        update_data: PrivacySettingsUpdate,
        ip_address: Optional[str] = None,
    ) -> PrivacySettingsResponse:
        """Updates and persists privacy settings with security audit trail."""
        record = await PrivacyService.get_or_create_settings(db, user_id)
        record.profile_visibility = str(update_data.profile_visibility)
        record.opportunity_alerts = update_data.opportunity_alerts
        record.email_notifications = update_data.email_notifications
        record.ai_processing_enabled = update_data.ai_processing_enabled
        record.data_usage_research = update_data.data_usage_research
        record.updated_at = utc_now()

        await AuditService.record_event(
            db,
            event_type=AuditEventType.PRIVACY_SETTINGS_UPDATED,
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            details=update_data.model_dump(),
        )
        await db.commit()
        await db.refresh(record)
        return await PrivacyService.get_privacy_settings(db, user_id)

    @staticmethod
    async def grant_consent(
        db: AsyncSession,
        user_id: str,
        req: ConsentGrantRequest,
        ip_address: Optional[str] = None,
    ) -> ConsentRecordResponse:
        """Records an explicit consent action."""
        purpose_str = req.purpose.value if hasattr(req.purpose, "value") else str(req.purpose)
        record = ConsentRecord(
            user_id=user_id,
            purpose=purpose_str,
            granted=True,
            policy_version=req.policy_version,
            ip_address=ip_address,
            created_at=utc_now(),
        )
        db.add(record)
        await AuditService.record_event(
            db,
            event_type=AuditEventType.CONSENT_GRANTED,
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            details={"purpose": purpose_str, "policy_version": req.policy_version},
        )
        await db.commit()
        await db.refresh(record)

        return ConsentRecordResponse(
            id=record.id,
            user_id=record.user_id,
            purpose=record.purpose,
            granted=record.granted,
            policy_version=record.policy_version,
            created_at=record.created_at,
            withdrawn_at=record.withdrawn_at,
        )

    @staticmethod
    async def withdraw_consent(
        db: AsyncSession,
        user_id: str,
        consent_id: str,
        ip_address: Optional[str] = None,
    ) -> ConsentRecordResponse:
        """Revokes an existing consent with audit trail."""
        query = select(ConsentRecord).where(
            ConsentRecord.id == consent_id,
            ConsentRecord.user_id == user_id,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent record not found.",
            )

        record.granted = False
        record.withdrawn_at = utc_now()

        await AuditService.record_event(
            db,
            event_type=AuditEventType.CONSENT_WITHDRAWN,
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            details={"consent_id": consent_id, "purpose": record.purpose},
        )
        await db.commit()
        await db.refresh(record)

        return ConsentRecordResponse(
            id=record.id,
            user_id=record.user_id,
            purpose=record.purpose,
            granted=record.granted,
            policy_version=record.policy_version,
            created_at=record.created_at,
            withdrawn_at=record.withdrawn_at,
        )

    @staticmethod
    async def list_consents(db: AsyncSession, user_id: str) -> List[ConsentRecordResponse]:
        """Lists user consent history."""
        query = select(ConsentRecord).where(ConsentRecord.user_id == user_id).order_by(ConsentRecord.created_at.desc())
        res = await db.execute(query)
        records = res.scalars().all()
        return [
            ConsentRecordResponse(
                id=r.id,
                user_id=r.user_id,
                purpose=r.purpose,
                granted=r.granted,
                policy_version=r.policy_version,
                created_at=r.created_at,
                withdrawn_at=r.withdrawn_at,
            )
            for r in records
        ]

