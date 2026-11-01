"""
RIGHT FIT API Contracts — Application CRM, Reminders & Interview Intelligence Schemas
Version: 1.0.0
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# ==============================================================================
# Enumerations
# ==============================================================================

class ApplicationStatus(StrEnum):
    """Auditable candidate job application lifecycle states."""
    SAVED = "SAVED"
    PLANNING_TO_APPLY = "PLANNING_TO_APPLY"
    APPLIED = "APPLIED"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    GHOSTED = "GHOSTED"
    CLOSED = "CLOSED"


class NoteType(StrEnum):
    """Categorization for application notes."""
    GENERAL = "GENERAL"
    INTERVIEW = "INTERVIEW"
    FOLLOW_UP = "FOLLOW_UP"
    REFERRAL = "REFERRAL"
    ASSESSMENT = "ASSESSMENT"


class ReminderType(StrEnum):
    """Categorization for scheduled candidate tasks and deadlines."""
    FOLLOW_UP = "FOLLOW_UP"
    INTERVIEW = "INTERVIEW"
    ASSESSMENT_DEADLINE = "ASSESSMENT_DEADLINE"
    CUSTOM = "CUSTOM"


class InterviewFormat(StrEnum):
    """Format of an interview round."""
    VIDEO = "VIDEO"
    PHONE = "PHONE"
    ON_SITE = "ON_SITE"
    TAKE_HOME = "TAKE_HOME"


class InterviewRoundStatus(StrEnum):
    """Status of an individual interview round."""
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MockSessionType(StrEnum):
    """Interview type for mock practice."""
    BEHAVIORAL = "BEHAVIORAL"
    TECHNICAL = "TECHNICAL"
    MIXED = "MIXED"
    SPRINT_48_HOUR = "SPRINT_48_HOUR"


class NotificationCategory(StrEnum):
    """Category classification for notifications."""
    INTERVIEW_REMINDER = "INTERVIEW_REMINDER"
    APPLICATION_FOLLOW_UP = "APPLICATION_FOLLOW_UP"
    ASSESSMENT_DEADLINE = "ASSESSMENT_DEADLINE"
    PREP_MILESTONE = "PREP_MILESTONE"
    SYSTEM = "SYSTEM"


# ==============================================================================
# CRM Application DTOs
# ==============================================================================

class ApplicationCreateRequest(BaseModel):
    opportunity_id: Optional[str] = Field(default=None, description="Linked canonical opportunity UUID if applicable")
    company_name: Optional[str] = Field(default=None, max_length=150)
    job_title: Optional[str] = Field(default=None, max_length=150)
    custom_company_name: Optional[str] = Field(default=None, max_length=150, description="Alias for company_name")
    custom_job_title: Optional[str] = Field(default=None, max_length=150, description="Alias for job_title")
    application_url: Optional[str] = Field(default=None, max_length=1000)
    status: ApplicationStatus = Field(default=ApplicationStatus.SAVED)
    initial_notes: Optional[str] = Field(default=None, max_length=2000)
    contact_name: Optional[str] = Field(default=None, max_length=100)
    contact_email: Optional[str] = Field(default=None, max_length=150)
    salary_offered: Optional[float] = None
    salary_currency: Optional[str] = Field(default="USD", max_length=10)

    @model_validator(mode="before")
    @classmethod
    def resolve_company_and_title(cls, data: Any) -> Any:
        if isinstance(data, dict):
            c_name = data.get("company_name") or data.get("custom_company_name")
            j_title = data.get("job_title") or data.get("custom_job_title")
            if c_name:
                data["company_name"] = str(c_name).strip()
            else:
                data["company_name"] = "Target Employer"
            if j_title:
                data["job_title"] = str(j_title).strip()
            else:
                data["job_title"] = "Prospective Opportunity"
        return data


class ApplicationUpdateRequest(BaseModel):
    company_name: Optional[str] = Field(default=None, max_length=150)
    job_title: Optional[str] = Field(default=None, max_length=150)
    application_url: Optional[str] = Field(default=None, max_length=1000)
    current_stage: Optional[str] = Field(default=None, max_length=100)
    contact_name: Optional[str] = Field(default=None, max_length=100)
    contact_email: Optional[str] = Field(default=None, max_length=150)
    salary_offered: Optional[float] = None
    salary_currency: Optional[str] = Field(default=None, max_length=10)


class ApplicationTransitionRequest(BaseModel):
    to_status: ApplicationStatus = Field(..., description="Target lifecycle state")
    reason: Optional[str] = Field(default=None, max_length=500, description="Audit reason for state transition")
    confirm_submission: bool = Field(
        default=False,
        description="Must be explicitly True when transitioning to APPLIED to confirm candidate submitted externally"
    )


class StatusHistoryItem(BaseModel):
    id: str
    from_status: Optional[str] = None
    to_status: str
    changed_at: datetime
    actor_type: str
    actor_id: str
    reason: Optional[str] = None


class ApplicationNoteCreate(BaseModel):
    note_type: NoteType = Field(default=NoteType.GENERAL)
    content: str = Field(..., min_length=1, max_length=5000)


class ApplicationNoteResponse(BaseModel):
    id: str
    application_id: str
    user_id: str
    note_type: NoteType
    content: str
    created_at: datetime
    updated_at: datetime


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    opportunity_id: Optional[str] = None
    company_name: str
    job_title: str
    company_display: Optional[str] = None
    title_display: Optional[str] = None
    application_url: Optional[str] = None
    status: ApplicationStatus
    applied_at: Optional[datetime] = None
    apply_link_opened_at: Optional[datetime] = None
    is_submission_confirmed: bool = False
    current_stage: Optional[str] = None
    salary_offered: Optional[float] = None
    salary_currency: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    notes_count: int = 0
    status_history: List[StatusHistoryItem] = Field(default_factory=list)
    recent_notes: List[ApplicationNoteResponse] = Field(default_factory=list)


class ApplicationStatsResponse(BaseModel):
    total_applications: int
    by_status: Dict[str, int] = Field(default_factory=dict)
    active_interviews: int = 0
    pending_follow_ups: int = 0
    offers_received: int = 0
    active_pipeline: int = 0
    interviews_scheduled: int = 0
    rejections_received: int = 0
    stalled_or_ghosted: int = 0


# ==============================================================================
# Reminders & Calendar DTOs
# ==============================================================================

class ReminderCreateRequest(BaseModel):
    application_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    reminder_type: ReminderType = Field(default=ReminderType.FOLLOW_UP)
    due_at_utc: datetime = Field(..., description="Target deadline in UTC")
    timezone: str = Field(default="UTC", description="Candidate IANA timezone, e.g. Asia/Kolkata")


class ReminderResponse(BaseModel):
    id: str
    user_id: str
    application_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    reminder_type: ReminderType
    due_at_utc: datetime
    timezone: str
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime


class CalendarEventResponse(BaseModel):
    id: str
    event_type: str  # "REMINDER" or "INTERVIEW_ROUND"
    title: str
    description: Optional[str] = None
    start_time_utc: datetime
    end_time_utc: Optional[datetime] = None
    candidate_timezone: str
    application_id: Optional[str] = None
    company_name: Optional[str] = None
    is_completed: bool = False


# ==============================================================================
# Interview Intelligence & 48-Hour Mode DTOs
# ==============================================================================

class InterviewRoundCreate(BaseModel):
    round_number: int = Field(default=1, ge=1)
    round_name: str = Field(..., min_length=1, max_length=150)
    scheduled_at_utc: Optional[datetime] = None
    interview_format: InterviewFormat = Field(default=InterviewFormat.VIDEO)
    interviewer_names: Optional[str] = Field(default=None, max_length=200)
    focus_areas: List[str] = Field(default_factory=list)


class InterviewRoundResponse(BaseModel):
    id: str
    plan_id: str
    round_number: int
    round_name: str
    scheduled_at_utc: Optional[datetime] = None
    interview_format: InterviewFormat
    interviewer_names: Optional[str] = None
    focus_areas: List[str] = Field(default_factory=list)
    status: InterviewRoundStatus


class InterviewPlanCreate(BaseModel):
    application_id: str
    title: str = Field(..., min_length=1, max_length=150)
    role_title: str = Field(..., min_length=1, max_length=150)
    company_name: str = Field(..., min_length=1, max_length=150)
    job_description_excerpt: Optional[str] = None
    rounds: List[InterviewRoundCreate] = Field(default_factory=list)


class InterviewPlanResponse(BaseModel):
    id: str
    application_id: str
    user_id: str
    title: str
    role_title: str
    company_name: str
    job_description_excerpt: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    rounds: List[InterviewRoundResponse] = Field(default_factory=list)


class PreparationMilestone(BaseModel):
    hour_bucket: str  # e.g. "T-48h to T-24h", "T-24h to T-6h", "Final T-6h"
    priority: str     # HIGH, MEDIUM, LOW
    action: str
    rationale: str
    is_completed: bool = False


class Sprint48HourResponse(BaseModel):
    interview_date_utc: datetime
    remaining_hours: float
    role_title: str
    company_name: str
    focus_skills_identified: List[str] = Field(default_factory=list)
    prioritized_milestones: List[PreparationMilestone] = Field(default_factory=list)
    predicted_question_categories: List[str] = Field(default_factory=list)
    sample_practice_questions: List[str] = Field(default_factory=list)
    revision_checklist: List[str] = Field(default_factory=list)
    evidence_grounding_notice: str = (
        "Preparation plan is dynamically prioritized based on candidate resume evidence and job requirements. "
        "Questions are synthetic practice suggestions and do not represent proprietary employer materials."
    )


# ==============================================================================
# STAR Answer Builder DTOs
# ==============================================================================

class STARAnswerCreate(BaseModel):
    plan_id: Optional[str] = None
    question: str = Field(..., min_length=3, max_length=500)
    category: str = Field(default="TECHNICAL_CHALLENGE", max_length=80)
    situation: str = Field(..., min_length=5)
    task: str = Field(..., min_length=5)
    action: str = Field(..., min_length=5)
    result: str = Field(..., min_length=5)
    supporting_evidence_reference: Optional[str] = Field(
        default=None,
        description="Pointer to verified resume section, project, or experience entry"
    )
    is_candidate_approved: bool = Field(default=False)


class STARAnswerResponse(BaseModel):
    id: str
    user_id: str
    plan_id: Optional[str] = None
    question: str
    category: str
    situation: str
    task: str
    action: str
    result: str
    supporting_evidence_reference: Optional[str] = None
    missing_information_notes: Optional[str] = None
    is_candidate_approved: bool = False
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Mock Interview & Rubric Evaluation DTOs
# ==============================================================================

class RubricScoreBreakdown(BaseModel):
    relevance: float = Field(..., ge=0, le=10, description="Relevance to question [0-10]")
    clarity: float = Field(..., ge=0, le=10, description="Communication clarity [0-10]")
    structure: float = Field(..., ge=0, le=10, description="STAR structure adherence [0-10]")
    evidence: float = Field(..., ge=0, le=10, description="Concrete evidence backing [0-10]")
    technical_correctness: float = Field(..., ge=0, le=10, description="Technical validity [0-10]")
    communication: float = Field(..., ge=0, le=10, description="Conciseness and delivery [0-10]")
    overall_score: float = Field(..., ge=0, le=10)
    feedback: str
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)


class MockQuestionAnswerRequest(BaseModel):
    question_id: str
    candidate_answer: str = Field(..., min_length=5, max_length=10000)


class MockQuestionResponse(BaseModel):
    id: str
    session_id: str
    question_text: str
    category: str
    order_index: int
    candidate_answer: Optional[str] = None
    rubric_evaluation: Optional[RubricScoreBreakdown] = None
    follow_up_question: Optional[str] = None
    answered_at: Optional[datetime] = None


class MockSessionCreateRequest(BaseModel):
    plan_id: Optional[str] = None
    role_title: str = Field(..., min_length=2, max_length=150)
    session_type: MockSessionType = Field(default=MockSessionType.BEHAVIORAL)
    question_count: int = Field(default=3, ge=1, le=10)


class MockSessionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: Optional[str] = None
    role_title: str
    session_type: MockSessionType
    status: str
    average_score: Optional[float] = None
    overall_feedback_summary: Optional[str] = None
    questions: List[MockQuestionResponse] = Field(default_factory=list)
    created_at: datetime
    completed_at: Optional[datetime] = None


# ==============================================================================
# Interview Debrief & Conflict Tracking DTOs
# ==============================================================================

class InterviewDebriefCreate(BaseModel):
    application_id: str
    round_name: str = Field(..., min_length=1, max_length=150)
    interview_date: datetime
    questions_asked: List[str] = Field(default_factory=list)
    topics_discussed: Optional[str] = None
    candidate_reflections: Optional[str] = None
    strengths: Optional[str] = None
    areas_to_improve: Optional[str] = None
    recruiter_commitments: Optional[str] = None
    expected_response_date: Optional[datetime] = None
    next_step: Optional[str] = None


class InterviewDebriefResponse(BaseModel):
    id: str
    application_id: str
    user_id: str
    round_name: str
    interview_date: datetime
    questions_asked: List[str] = Field(default_factory=list)
    topics_discussed: Optional[str] = None
    candidate_reflections: Optional[str] = None
    strengths: Optional[str] = None
    areas_to_improve: Optional[str] = None
    recruiter_commitments: Optional[str] = None
    expected_response_date: Optional[datetime] = None
    next_step: Optional[str] = None
    created_at: datetime


class ScheduleConflictCheck(BaseModel):
    has_conflicts: bool
    conflict_count: int
    conflicting_events: List[CalendarEventResponse] = Field(default_factory=list)


# ==============================================================================
# Central Notifications DTOs
# ==============================================================================

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    category: NotificationCategory
    title: str
    message: str
    reference_link: Optional[str] = None
    is_read: bool = False
    delivery_channel: str
    delivery_status: str
    created_at: datetime


class NotificationPreferencesUpdate(BaseModel):
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    interview_reminders: Optional[bool] = None
    application_follow_ups: Optional[bool] = None
    assessment_deadlines: Optional[bool] = None
    prep_milestones: Optional[bool] = None
    frequency: Optional[str] = None  # INSTANT, DAILY_DIGEST, WEEKLY_DIGEST
    quiet_hours_start: Optional[str] = None  # e.g. "22:00"
    quiet_hours_end: Optional[str] = None    # e.g. "08:00"
    timezone: Optional[str] = None
    job_alerts_enabled: Optional[bool] = None
    digest_email_enabled: Optional[bool] = None
    market_intelligence_alerts: Optional[bool] = None


class NotificationPreferencesResponse(BaseModel):
    user_id: str
    in_app_enabled: bool = True
    email_enabled: bool = False
    interview_reminders: bool = True
    application_follow_ups: bool = True
    assessment_deadlines: bool = True
    prep_milestones: bool = True
    frequency: str = "DAILY_DIGEST"
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "08:00"
    timezone: str = "UTC"
    job_alerts_enabled: bool = True
    digest_email_enabled: bool = False
    market_intelligence_alerts: bool = True
    updated_at: datetime

