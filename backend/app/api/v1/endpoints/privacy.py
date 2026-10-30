"""
RIGHT FIT Core — Privacy, Consent, Export & Deletion API Endpoints
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_client_ip, get_current_active_user, get_current_user
from app.db.models import User
from app.services.deletion_service import DeletionService
from app.services.export_service import ExportService
from app.services.privacy_service import PrivacyService
from contracts.common.envelope import ResponseMeta, StandardResponse
from contracts.privacy.schemas import (
    AccountDeletionRequest,
    AccountDeletionResponse,
    ConsentGrantRequest,
    ConsentRecordResponse,
    DataExportDownloadResponse,
    DataExportResponse,
    PrivacySettingsResponse,
    PrivacySettingsUpdate,
)

router = APIRouter(prefix="/candidate", tags=["Privacy, Consent & Data Rights"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id, service="core_career_engine")


@router.get("/privacy", response_model=StandardResponse[PrivacySettingsResponse])
async def get_privacy_settings(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PrivacySettingsResponse]:
    """Retrieves candidate privacy and visibility preferences."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    settings = await PrivacyService.get_privacy_settings(db, current_user.id)
    return StandardResponse(data=settings, meta=make_meta(req_id))


@router.put("/privacy", response_model=StandardResponse[PrivacySettingsResponse])
async def update_privacy_settings(
    payload: PrivacySettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[PrivacySettingsResponse]:
    """Updates candidate privacy and visibility preferences."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    settings = await PrivacyService.update_privacy_settings(db, current_user.id, payload, ip_address=ip)
    return StandardResponse(data=settings, meta=make_meta(req_id))


@router.get("/consents", response_model=StandardResponse[List[ConsentRecordResponse]])
async def list_consents(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[ConsentRecordResponse]]:
    """Lists auditable consent history."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    consents = await PrivacyService.list_consents(db, current_user.id)
    return StandardResponse(data=consents, meta=make_meta(req_id))


@router.post("/consents", response_model=StandardResponse[ConsentRecordResponse], status_code=status.HTTP_201_CREATED)
async def grant_consent(
    payload: ConsentGrantRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ConsentRecordResponse]:
    """Records explicit consent for a processing purpose."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    consent = await PrivacyService.grant_consent(db, current_user.id, payload, ip_address=ip)
    return StandardResponse(data=consent, meta=make_meta(req_id))


@router.delete("/consents/{consent_id}", response_model=StandardResponse[ConsentRecordResponse])
async def withdraw_consent(
    consent_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[ConsentRecordResponse]:
    """Withdraws an existing consent grant."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    updated = await PrivacyService.withdraw_consent(db, current_user.id, consent_id, ip_address=ip)
    return StandardResponse(data=updated, meta=make_meta(req_id))


@router.post("/data-export", response_model=StandardResponse[DataExportResponse], status_code=status.HTTP_202_ACCEPTED)
async def request_data_export(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[DataExportResponse]:
    """Generates a structured, machine-readable JSON data archive of all candidate information."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    export_resp = await ExportService.generate_export(db, current_user.id, ip_address=ip)
    return StandardResponse(data=export_resp, meta=make_meta(req_id))


@router.get("/data-export/{export_id}/download", response_model=StandardResponse[DataExportDownloadResponse])
async def download_data_export(
    export_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[DataExportDownloadResponse]:
    """Downloads the candidate's exported data payload with strict ownership verification."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    download = await ExportService.get_export_download(db, current_user.id, export_id)
    return StandardResponse(data=download, meta=make_meta(req_id))


@router.post("/account-deletion", response_model=StandardResponse[AccountDeletionResponse])
async def request_account_deletion(
    payload: AccountDeletionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[AccountDeletionResponse]:
    """Initiates account deletion workflow, revokes sessions, and coordinates satellite deletion."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    resp = await DeletionService.request_deletion(db, current_user.id, payload, ip_address=ip)
    return StandardResponse(data=resp, meta=make_meta(req_id))


@router.get("/account-deletion/status", response_model=StandardResponse[Optional[AccountDeletionResponse]])
async def get_account_deletion_status(
    request: Request,
    current_user: User = Depends(get_current_user),  # Can check status even if DELETION_PENDING
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Optional[AccountDeletionResponse]]:
    """Retrieves current deletion workflow status."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    resp = await DeletionService.get_deletion_status(db, current_user.id)
    return StandardResponse(data=resp, meta=make_meta(req_id))
