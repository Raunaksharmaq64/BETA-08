"""
RIGHT FIT Core — Resume Intelligence Endpoints
API routes for secure upload, extraction, evidence review, and ATS analysis.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

import io
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contracts.resume.schemas import (
    ATSAnalysisRequest,
    ATSAnalysisResponse,
    ResumeConfirmSyncRequest,
    ResumeConfirmSyncResponse,
    ResumeExtractionResponse,
    ResumeReviewFieldUpdate,
    ResumeReviewResponse,
    ResumeSummaryResponse,
    ResumeUploadResponse,
    ResumeVersionResponse,
)
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import (
    ATSAnalysisRecord,
    ResumeExtractionRecord,
    ResumeRecord,
    ResumeVersionRecord,
    User,
)
from app.services.ats_service import ats_service
from app.services.resume_service import resume_service
from app.services.review_service import review_service
from app.services.storage_service import StorageSecurityError, storage_service

router = APIRouter(prefix="/resumes", tags=["Resume Intelligence"])


@router.post("", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    title: str = Form("My Resume"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Securely uploads an initial resume document (PDF or DOCX)."""
    try:
        file_bytes = await file.read()
        res = await resume_service.upload_initial_resume(
            db=db,
            user_id=current_user.id,
            title=title,
            file_bytes=file_bytes,
            filename=file.filename or "resume.pdf"
        )
        return res
    except StorageSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[ResumeSummaryResponse])
async def list_resumes(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all resume containers owned by the candidate."""
    return await resume_service.list_resumes(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeSummaryResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves resume summary and active version details."""
    try:
        return await resume_service.get_resume_summary(db, current_user.id, resume_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently deletes a resume, all versions, extraction data, and stored files."""
    try:
        await resume_service.delete_resume(db, current_user.id, resume_id)
        return {"success": True, "message": "Resume and all associated records deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/versions", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_new_version(
    resume_id: str,
    version_label: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Uploads an additional version to an existing candidate resume."""
    try:
        file_bytes = await file.read()
        return await resume_service.upload_new_version(
            db=db,
            user_id=current_user.id,
            resume_id=resume_id,
            file_bytes=file_bytes,
            filename=file.filename or "resume.pdf",
            version_label=version_label
        )
    except StorageSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}/versions", response_model=List[ResumeVersionResponse])
async def list_versions(
    resume_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all versions of a specific resume."""
    try:
        return await resume_service.list_versions(db, current_user.id, resume_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{resume_id}/active-version", response_model=ResumeSummaryResponse)
async def set_active_version(
    resume_id: str,
    version_id: str = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Designates a specific version as the active resume."""
    try:
        return await resume_service.set_active_version(db, current_user.id, resume_id, version_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/parse", response_model=ResumeExtractionResponse)
async def parse_resume(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers the document text extraction and structured parsing pipeline."""
    try:
        return await resume_service.execute_parse_pipeline(
            db=db,
            user_id=current_user.id,
            resume_id=resume_id,
            version_id=version_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{resume_id}/extraction", response_model=ResumeExtractionResponse)
async def get_extraction(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves structured extractions and evidence for a parsed resume."""
    try:
        return await resume_service.get_extraction(db, current_user.id, resume_id, version_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}/review", response_model=ResumeReviewResponse)
async def get_review_workbench(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves review workbench state with profile conflict detection."""
    try:
        # Resolve target version
        if not version_id:
            summary = await resume_service.get_resume_summary(db, current_user.id, resume_id)
            if not summary.active_version_id:
                raise ValueError("Active version not found.")
            target_version_id = summary.active_version_id
        else:
            target_version_id = version_id

        return await review_service.get_or_create_review(db, target_version_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{resume_id}/review", response_model=ResumeReviewResponse)
async def update_field_review(
    resume_id: str,
    update: ResumeReviewFieldUpdate,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirms, corrects, or rejects an extracted field."""
    try:
        if not version_id:
            summary = await resume_service.get_resume_summary(db, current_user.id, resume_id)
            target_version_id = summary.active_version_id
        else:
            target_version_id = version_id

        if not target_version_id:
            raise ValueError("Target version not found.")

        return await review_service.update_field_review(db, target_version_id, current_user.id, update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/confirm", response_model=ResumeConfirmSyncResponse)
async def confirm_and_sync_profile(
    resume_id: str,
    sync_req: ResumeConfirmSyncRequest,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Synchronizes candidate-confirmed fields into canonical candidate profile tables."""
    try:
        if not version_id:
            summary = await resume_service.get_resume_summary(db, current_user.id, resume_id)
            target_version_id = summary.active_version_id
        else:
            target_version_id = version_id

        if not target_version_id:
            raise ValueError("Target version not found.")

        return await review_service.sync_approved_to_profile(
            db=db,
            version_id=target_version_id,
            user_id=current_user.id,
            sync_req=sync_req
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{resume_id}/ats-analysis", response_model=ATSAnalysisResponse)
async def analyze_ats_compatibility(
    resume_id: str,
    req: ATSAnalysisRequest,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluates ATS keyword coverage, bullet impact, and non-fabricating advice."""
    try:
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)

        # Collect bullets from experience and projects
        bullets: List[str] = []
        for exp in ext.experience:
            bullets.extend(exp.get("responsibilities", []))
        for proj in ext.projects:
            if proj.get("description"):
                bullets.append(proj["description"])

        # Fetch raw text
        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == ext.version_id
        )
        res_ext = await db.execute(stmt_ext)
        ext_record = res_ext.scalar_one()

        analysis_data = ats_service.analyze_resume_for_ats(
            resume_text=ext_record.raw_text,
            job_title=req.target_job_title,
            job_description=req.target_job_description,
            bullets=bullets,
            extractions={
                "personal_info": ext.personal_info,
                "sections": ext_record.sections_json
            }
        )

        analysis_record = ATSAnalysisRecord(
            resume_version_id=ext.version_id,
            user_id=current_user.id,
            target_job_title=req.target_job_title,
            target_job_description=req.target_job_description,
            coverage_score=analysis_data["coverage_score"],
            matched_keywords_json=analysis_data["matched_keywords"],
            missing_keywords_json=analysis_data["missing_keywords"],
            bullet_impact_score=analysis_data["bullet_impact_score"],
            bullet_impact_analysis_json=analysis_data["bullet_impact_analysis"],
            actionable_suggestions_json=analysis_data["actionable_suggestions"],
            formatting_observations_json=analysis_data["formatting_observations"],
            methodology_and_limitations=analysis_data["methodology_and_limitations"]
        )
        db.add(analysis_record)
        await db.commit()
        await db.refresh(analysis_record)

        return ATSAnalysisResponse(
            analysis_id=analysis_record.id,
            resume_id=resume_id,
            version_id=ext.version_id,
            target_job_title=req.target_job_title,
            coverage_score=analysis_record.coverage_score,
            matched_keywords=analysis_record.matched_keywords_json,
            missing_keywords=analysis_record.missing_keywords_json,
            bullet_impact_score=analysis_record.bullet_impact_score,
            bullet_impact_analysis=analysis_record.bullet_impact_analysis_json,
            actionable_suggestions=analysis_record.actionable_suggestions_json,
            formatting_observations=analysis_record.formatting_observations_json,
            methodology_and_limitations=analysis_record.methodology_and_limitations,
            created_at=analysis_record.created_at
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{resume_id}/ats-analysis/{analysis_id}", response_model=ATSAnalysisResponse)
async def get_ats_analysis(
    resume_id: str,
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves an existing ATS analysis result."""
    stmt = select(ATSAnalysisRecord).where(
        ATSAnalysisRecord.id == analysis_id,
        ATSAnalysisRecord.user_id == current_user.id
    )
    res = await db.execute(stmt)
    analysis = res.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    return ATSAnalysisResponse(
        analysis_id=analysis.id,
        resume_id=resume_id,
        version_id=analysis.resume_version_id,
        target_job_title=analysis.target_job_title,
        coverage_score=analysis.coverage_score,
        matched_keywords=analysis.matched_keywords_json,
        missing_keywords=analysis.missing_keywords_json,
        bullet_impact_score=analysis.bullet_impact_score,
        bullet_impact_analysis=analysis.bullet_impact_analysis_json,
        actionable_suggestions=analysis.actionable_suggestions_json,
        formatting_observations=analysis.formatting_observations_json,
        methodology_and_limitations=analysis.methodology_and_limitations,
        created_at=analysis.created_at
    )


@router.get("/{resume_id}/download")
async def download_resume_file(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Authenticated streaming download of the candidate's original resume file."""
    try:
        if version_id:
            stmt = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == version_id,
                ResumeVersionRecord.resume_id == resume_id,
                ResumeVersionRecord.user_id == current_user.id
            )
        else:
            stmt_r = select(ResumeRecord).where(ResumeRecord.id == resume_id, ResumeRecord.user_id == current_user.id)
            res_r = await db.execute(stmt_r)
            resume = res_r.scalar_one_or_none()
            if not resume or not resume.active_version_id:
                raise ValueError("Active version not found.")
            stmt = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == resume.active_version_id,
                ResumeVersionRecord.user_id == current_user.id
            )

        res = await db.execute(stmt)
        ver = res.scalar_one_or_none()
        if not ver:
            raise ValueError("Resume file not found.")

        file_bytes = storage_service.read_resume_file(ver.storage_path, current_user.id)
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=ver.mime_type,
            headers={"Content-Disposition": f'attachment; filename="{ver.original_filename}"'}
        )
    except StorageSecurityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
