"""
RIGHT FIT Core — Candidate Data Export Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import (
    CandidatePreferenceRecord,
    CandidateProfile,
    ConsentRecord,
    DataExportRequestRecord,
    PrivacySettingsRecord,
    User,
    is_expired,
    utc_now,
)
from app.services.audit_service import AuditService
from app.services.preferences_service import PreferencesService
from app.services.privacy_service import PrivacyService
from app.services.profile_service import ProfileService
from app.services.rate_limiter import rate_limiter
from contracts.privacy.schemas import (
    DataExportDownloadResponse,
    DataExportResponse,
    DataExportStatus,
)
from contracts.security.audit import AuditEventType


class ExportService:
    @staticmethod
    async def generate_export(
        db: AsyncSession,
        user_id: str,
        ip_address: Optional[str] = None,
    ) -> DataExportResponse:
        """Collects all candidate profile and privacy data, strips sensitive hashes, and persists export."""
        # 1. Rate limiting
        allowed, retry_after = rate_limiter.is_allowed(
            f"export:{user_id}",
            max_requests=settings.RATE_LIMIT_DATA_EXPORT,
            window_seconds=60,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Data export request limit reached. Retry after {retry_after}s.",
            )

        # 2. Query User
        u_query = select(User).where(User.id == user_id)
        u_res = await db.execute(u_query)
        user = u_res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # 3. Collect domain components
        profile_dto = await ProfileService.get_profile_response(db, user_id)
        prefs_dto = await PreferencesService.get_preferences(db, user_id)
        privacy_dto = await PrivacyService.get_privacy_settings(db, user_id)
        consents = await PrivacyService.list_consents(db, user_id)

        # 4. Assemble export payload without credentials or internal secrets
        export_payload: Dict[str, Any] = {
            "account": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "status": user.status,
                "is_email_verified": user.is_email_verified,
                "created_at": user.created_at.isoformat(),
            },
            "profile": profile_dto.model_dump(mode="json"),
            "preferences": prefs_dto.model_dump(mode="json"),
            "privacy_settings": privacy_dto.model_dump(mode="json"),
            "consent_records": [c.model_dump(mode="json") for c in consents],
        }

        # 5. Persist record
        export_record = DataExportRequestRecord(
            user_id=user.id,
            status=DataExportStatus.COMPLETED.value,
            export_data_json=export_payload,
            expires_at=utc_now() + timedelta(hours=24),
            created_at=utc_now(),
            completed_at=utc_now(),
        )
        db.add(export_record)
        await AuditService.record_event(
            db,
            event_type=AuditEventType.DATA_EXPORT_REQUESTED,
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            details={"export_id": export_record.id},
        )
        await db.commit()
        await db.refresh(export_record)

        return DataExportResponse(
            export_id=export_record.id,
            status=DataExportStatus.COMPLETED,
            created_at=export_record.created_at,
            expires_at=export_record.expires_at,
            download_url=f"/api/v1/candidate/data-export/{export_record.id}/download",
        )

    @staticmethod
    async def get_export_download(
        db: AsyncSession,
        user_id: str,
        export_id: str,
    ) -> DataExportDownloadResponse:
        """Retrieves exported archive with strict ownership and expiry validation."""
        query = select(DataExportRequestRecord).where(
            DataExportRequestRecord.id == export_id,
            DataExportRequestRecord.user_id == user_id,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export file not found or unauthorized.",
            )

        if record.expires_at and is_expired(record.expires_at):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This export file has expired. Please initiate a new export request.",
            )

        return DataExportDownloadResponse(
            export_id=record.id,
            user_id=record.user_id,
            generated_at=record.created_at,
            metadata={
                "schema_version": "1.0",
                "platform": "RIGHT FIT Career Intelligence Platform",
                "format": "JSON",
            },
            data=record.export_data_json or {},
        )
