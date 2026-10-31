"""
RIGHT FIT Core — Interview Intelligence, STAR Builder & Mock Interviews Endpoints
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import User
from app.services.interview_intelligence_service import InterviewIntelligenceService
from contracts.applications.schemas import (
    InterviewDebriefCreate,
    InterviewDebriefResponse,
    InterviewPlanCreate,
    InterviewPlanResponse,
    InterviewRoundCreate,
    InterviewRoundResponse,
    MockQuestionAnswerRequest,
    MockQuestionResponse,
    MockSessionCreateRequest,
    MockSessionResponse,
    Sprint48HourResponse,
    STARAnswerCreate,
    STARAnswerResponse,
)
from contracts.common.envelope import ResponseMeta, StandardResponse

router = APIRouter(tags=["Interview Intelligence"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id)


# ------------------------------------------------------------------------------
# Interview Plans & Multiple Rounds
# ------------------------------------------------------------------------------

@router.post("/interview-plans", response_model=StandardResponse[InterviewPlanResponse], status_code=status.HTTP_201_CREATED)
async def create_interview_plan(
    req: InterviewPlanCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[InterviewPlanResponse]:
    """Creates a structured multi-round interview preparation plan."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_create(session: Session) -> InterviewPlanResponse:
        try:
            return InterviewIntelligenceService.create_plan(session=session, user_id=current_user.id, req=req)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    plan = await db.run_sync(_sync_create)
    return StandardResponse(data=plan, meta=make_meta(req_id))


@router.get("/interview-plans", response_model=StandardResponse[List[InterviewPlanResponse]])
async def list_interview_plans(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[InterviewPlanResponse]]:
    """Lists candidate interview plans with scheduled rounds."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[InterviewPlanResponse]:
        return InterviewIntelligenceService.list_plans(session=session, user_id=current_user.id)

    plans = await db.run_sync(_sync_list)
    return StandardResponse(data=plans, meta=make_meta(req_id))


@router.get("/interview-plans/{plan_id}", response_model=StandardResponse[InterviewPlanResponse])
async def get_interview_plan(
    plan_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[InterviewPlanResponse]:
    """Retrieves an interview plan."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_get(session: Session) -> Optional[InterviewPlanResponse]:
        return InterviewIntelligenceService.get_plan(session=session, plan_id=plan_id, user_id=current_user.id)

    plan = await db.run_sync(_sync_get)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview plan not found.")

    return StandardResponse(data=plan, meta=make_meta(req_id))


@router.post("/interview-plans/{plan_id}/rounds", response_model=StandardResponse[InterviewRoundResponse], status_code=status.HTTP_201_CREATED)
async def add_interview_round(
    plan_id: str,
    req: InterviewRoundCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[InterviewRoundResponse]:
    """Adds a scheduled round to an interview plan."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_round(session: Session) -> InterviewRoundResponse:
        try:
            return InterviewIntelligenceService.add_round(session=session, plan_id=plan_id, user_id=current_user.id, req=req)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    round_res = await db.run_sync(_sync_round)
    return StandardResponse(data=round_res, meta=make_meta(req_id))


@router.get("/interview-plans/{plan_id}/48-hour-prep", response_model=StandardResponse[Sprint48HourResponse])
async def get_48_hour_prep(
    plan_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Sprint48HourResponse]:
    """Generates a prioritized 48-hour interview sprint based on job specs and confirmed candidate evidence."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_prep(session: Session) -> Sprint48HourResponse:
        try:
            return InterviewIntelligenceService.generate_48_hour_prep(session=session, plan_id=plan_id, user_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    prep = await db.run_sync(_sync_prep)
    return StandardResponse(data=prep, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# STAR Answer Builder
# ------------------------------------------------------------------------------

@router.post("/star-answers", response_model=StandardResponse[STARAnswerResponse], status_code=status.HTTP_201_CREATED)
async def create_star_answer(
    req: STARAnswerCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[STARAnswerResponse]:
    """Saves a structured STAR answer grounded in candidate verified resume and experience."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_star(session: Session) -> STARAnswerResponse:
        try:
            return InterviewIntelligenceService.create_star_answer(session=session, user_id=current_user.id, req=req)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    answer = await db.run_sync(_sync_star)
    return StandardResponse(data=answer, meta=make_meta(req_id))


@router.get("/star-answers", response_model=StandardResponse[List[STARAnswerResponse]])
async def list_star_answers(
    request: Request,
    plan_id: Optional[str] = Query(None, description="Filter by interview plan"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[STARAnswerResponse]]:
    """Lists candidate STAR answers."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[STARAnswerResponse]:
        return InterviewIntelligenceService.list_star_answers(session=session, user_id=current_user.id, plan_id=plan_id)

    answers = await db.run_sync(_sync_list)
    return StandardResponse(data=answers, meta=make_meta(req_id))


@router.delete("/star-answers/{answer_id}", response_model=StandardResponse[Dict[str, Any]])
async def delete_star_answer(
    answer_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[Dict[str, Any]]:
    """Deletes a STAR answer."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_del(session: Session) -> bool:
        return InterviewIntelligenceService.delete_star_answer(session=session, answer_id=answer_id, user_id=current_user.id)

    deleted = await db.run_sync(_sync_del)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="STAR answer not found.")

    return StandardResponse(data={"success": True, "message": "STAR answer deleted."}, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Mock Interviews & 6-Factor Rubric
# ------------------------------------------------------------------------------

@router.post("/mock-interviews", response_model=StandardResponse[MockSessionResponse], status_code=status.HTTP_201_CREATED)
async def create_mock_interview(
    req: MockSessionCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[MockSessionResponse]:
    """Creates a mock interview practice session with questions."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_mock(session: Session) -> MockSessionResponse:
        return InterviewIntelligenceService.create_mock_session(session=session, user_id=current_user.id, req=req)

    sess = await db.run_sync(_sync_mock)
    return StandardResponse(data=sess, meta=make_meta(req_id))


@router.post("/mock-interviews/{session_id}/questions/{question_id}/answer", response_model=StandardResponse[MockQuestionResponse])
async def submit_mock_answer(
    session_id: str,
    question_id: str,
    req: MockQuestionAnswerRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[MockQuestionResponse]:
    """Submits candidate practice answer and evaluates against 6-factor rubric."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    req.question_id = question_id

    def _sync_eval(session: Session) -> MockQuestionResponse:
        try:
            return InterviewIntelligenceService.submit_mock_answer(
                session=session,
                session_id=session_id,
                user_id=current_user.id,
                req=req,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    res = await db.run_sync(_sync_eval)
    return StandardResponse(data=res, meta=make_meta(req_id))


# ------------------------------------------------------------------------------
# Interview Debriefs
# ------------------------------------------------------------------------------

@router.post("/interview-debriefs", response_model=StandardResponse[InterviewDebriefResponse], status_code=status.HTTP_201_CREATED)
async def record_interview_debrief(
    req: InterviewDebriefCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[InterviewDebriefResponse]:
    """Records post-interview reflections, questions asked, and recruiter promises."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_debrief(session: Session) -> InterviewDebriefResponse:
        try:
            return InterviewIntelligenceService.record_debrief(session=session, user_id=current_user.id, req=req)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    debrief = await db.run_sync(_sync_debrief)
    return StandardResponse(data=debrief, meta=make_meta(req_id))


@router.get("/interview-debriefs", response_model=StandardResponse[List[InterviewDebriefResponse]])
async def list_interview_debriefs(
    request: Request,
    application_id: Optional[str] = Query(None, description="Filter by application"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[InterviewDebriefResponse]]:
    """Lists candidate interview debriefs."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    def _sync_list(session: Session) -> List[InterviewDebriefResponse]:
        return InterviewIntelligenceService.list_debriefs(session=session, user_id=current_user.id, application_id=application_id)

    debriefs = await db.run_sync(_sync_list)
    return StandardResponse(data=debriefs, meta=make_meta(req_id))

