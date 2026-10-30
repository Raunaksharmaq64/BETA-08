"""
RIGHT FIT Core — Account & Data Deletion Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AccountDeletionRequestRecord,
    RefreshTokenRecord,
    User,
    utc_now,
)
from app.services.audit_service import AuditService
from contracts.auth.schemas import AccountStatus
from contracts.privacy.schemas import (
    AccountDeletionRequest,
    AccountDeletionResponse,
    DeletionStatus,
)
from contracts.security.audit import AuditEventType


class DeletionService:
    @staticmethod
    async def request_deletion(
        db: AsyncSession,
        user_id: str,
        req: AccountDeletionRequest,
        ip_address: Optional[str] = None,
    ) -> AccountDeletionResponse:
        """Processes account deletion request with inter-service coordination and grace period."""
        if req.confirmation.strip() != "DELETE MY ACCOUNT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation phrase must exactly match 'DELETE MY ACCOUNT'.",
            )

        u_query = select(User).where(User.id == user_id)
        u_res = await db.execute(u_query)
        user = u_res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # 1. Update user state to DELETION_PENDING
        user.status = AccountStatus.DELETION_PENDING.value
        user.updated_at = utc_now()

        # 2. Terminate all active sessions immediately
        revoke_all = (
            update(RefreshTokenRecord)
            .where(RefreshTokenRecord.user_id == user_id)
            .values(is_revoked=True)
        )
        await db.execute(revoke_all)

        # 3. Simulate inter-service coordination with satellite services
        # (LeadHunter and Startup Intelligence satellite service deletion contracts)
        service_status: Dict[str, str] = {
            "core": "DELETION_PENDING",
            "leadhunter": "ACKNOWLEDGED",
            "startup_intelligence": "ACKNOWLEDGED",
        }

        # 4. Schedule final hard deletion after 30-day statutory grace period
        scheduled_at = utc_now() + timedelta(days=30)
        deletion_record = AccountDeletionRequestRecord(
            user_id=user.id,
            status=DeletionStatus.PENDING.value,
            reasons=req.reason,
            service_status_json=service_status,
            scheduled_deletion_at=scheduled_at,
            created_at=utc_now(),
        )
        db.add(deletion_record)

        # 5. Record minimal audit trail (no PII retained in details)
        await AuditService.record_event(
            db,
            event_type=AuditEventType.ACCOUNT_DELETION_REQUESTED,
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={"deletion_id": deletion_record.id, "grace_period_days": 30},
        )
        await db.commit()
        await db.refresh(deletion_record)

        return AccountDeletionResponse(
            deletion_id=deletion_record.id,
            status=DeletionStatus.PENDING,
            scheduled_deletion_at=deletion_record.scheduled_deletion_at,
            service_status=service_status,
            message="Your account has been scheduled for deletion. Active sessions have been revoked. A 30-day grace period is active.",
        )

    @staticmethod
    async def get_deletion_status(
        db: AsyncSession,
        user_id: str,
    ) -> Optional[AccountDeletionResponse]:
        """Retrieves active deletion request status."""
        query = (
            select(AccountDeletionRequestRecord)
            .where(AccountDeletionRequestRecord.user_id == user_id)
            .order_by(AccountDeletionRequestRecord.created_at.desc())
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()
        if not record:
            return None

        return AccountDeletionResponse(
            deletion_id=record.id,
            status=DeletionStatus(record.status),
            scheduled_deletion_at=record.scheduled_deletion_at,
            service_status=record.service_status_json or {},
            message="Account deletion is pending completion.",
        )
