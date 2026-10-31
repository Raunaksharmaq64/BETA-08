"""
RIGHT FIT — Reminders, Calendar & Timezone Service
Phase: 8 — CRM and Interview Intelligence

Implements:
1. Candidate IANA timezone conversion & DST handling
2. Scheduled task and deadline reminders
3. Calendar event aggregation across reminders and interview rounds
4. Interview schedule conflict detection
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    ApplicationRecord,
    InterviewPlanRecord,
    InterviewRoundRecord,
    ReminderRecord,
)
from contracts.applications.schemas import (
    CalendarEventResponse,
    ReminderCreateRequest,
    ReminderResponse,
    ReminderType,
    ScheduleConflictCheck,
)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_in_timezone(dt_utc: datetime, target_tz: str) -> str:
    """Formats a UTC datetime in candidate's configured IANA timezone."""
    try:
        tz = ZoneInfo(target_tz)
    except Exception:
        tz = ZoneInfo("UTC")
    aware_utc = ensure_utc(dt_utc)
    local_dt = aware_utc.astimezone(tz)
    return local_dt.strftime("%Y-%m-%d %H:%M %Z")


class ReminderService:
    """Orchestrates reminders, calendar aggregation, and interview conflict detection."""

    @classmethod
    def create_reminder(
        cls,
        session: Session,
        user_id: str,
        req: ReminderCreateRequest,
    ) -> ReminderResponse:
        """Schedules a new reminder with candidate IANA timezone metadata."""
        due_utc = ensure_utc(req.due_at_utc)

        # Validate application ownership if attached
        if req.application_id:
            app = session.execute(
                select(ApplicationRecord).where(
                    ApplicationRecord.id == req.application_id,
                    ApplicationRecord.user_id == user_id,
                )
            ).scalars().first()
            if not app:
                raise ValueError(f"Application '{req.application_id}' not found.")

        # Validate IANA timezone
        candidate_tz = req.timezone
        try:
            ZoneInfo(candidate_tz)
        except Exception:
            candidate_tz = "UTC"

        record = ReminderRecord(
            user_id=user_id,
            application_id=req.application_id,
            title=req.title,
            description=req.description,
            reminder_type=req.reminder_type.value,
            due_at_utc=due_utc,
            timezone=candidate_tz,
            is_completed=False,
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        return cls._to_reminder_response(record)

    @classmethod
    def list_reminders(
        cls,
        session: Session,
        user_id: str,
        is_completed: Optional[bool] = None,
    ) -> List[ReminderResponse]:
        """Lists candidate reminders, sorted by due date."""
        query = select(ReminderRecord).where(ReminderRecord.user_id == user_id)
        if is_completed is not None:
            query = query.where(ReminderRecord.is_completed == is_completed)

        query = query.order_by(ReminderRecord.due_at_utc.asc())
        records = session.execute(query).scalars().all()
        return [cls._to_reminder_response(r) for r in records]

    @classmethod
    def complete_reminder(
        cls,
        session: Session,
        reminder_id: str,
        user_id: str,
    ) -> Optional[ReminderResponse]:
        """Marks a reminder as completed."""
        record = session.execute(
            select(ReminderRecord).where(
                ReminderRecord.id == reminder_id,
                ReminderRecord.user_id == user_id,
            )
        ).scalars().first()

        if not record:
            return None

        record.is_completed = True
        record.completed_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(record)
        return cls._to_reminder_response(record)

    @classmethod
    def delete_reminder(
        cls,
        session: Session,
        reminder_id: str,
        user_id: str,
    ) -> bool:
        """Deletes a reminder."""
        record = session.execute(
            select(ReminderRecord).where(
                ReminderRecord.id == reminder_id,
                ReminderRecord.user_id == user_id,
            )
        ).scalars().first()

        if not record:
            return False

        session.delete(record)
        session.commit()
        return True

    @classmethod
    def get_calendar_events(
        cls,
        session: Session,
        user_id: str,
        start_utc: Optional[datetime] = None,
        end_utc: Optional[datetime] = None,
        candidate_timezone: str = "UTC",
    ) -> List[CalendarEventResponse]:
        """
        Aggregates calendar events across:
        1. Scheduled candidate reminders
        2. Scheduled interview rounds from interview plans
        """
        now = datetime.now(timezone.utc)
        start = ensure_utc(start_utc) or (now - timedelta(days=30))
        end = ensure_utc(end_utc) or (now + timedelta(days=90))

        events: List[CalendarEventResponse] = []

        # 1. Fetch Reminders
        rem_q = select(ReminderRecord).options(
            joinedload(ReminderRecord.application)
        ).where(
            ReminderRecord.user_id == user_id,
            ReminderRecord.due_at_utc >= start,
            ReminderRecord.due_at_utc <= end,
        )
        reminders = session.execute(rem_q).scalars().all()
        for r in reminders:
            events.append(
                CalendarEventResponse(
                    id=f"rem_{r.id}",
                    event_type="REMINDER",
                    title=f"Reminder: {r.title}",
                    description=r.description,
                    start_time_utc=ensure_utc(r.due_at_utc),
                    candidate_timezone=r.timezone or candidate_timezone,
                    application_id=r.application_id,
                    company_name=r.application.company_name if r.application else None,
                    is_completed=r.is_completed,
                )
            )

        # 2. Fetch Interview Rounds
        rounds_q = select(InterviewRoundRecord).join(
            InterviewRoundRecord.plan
        ).options(
            joinedload(InterviewRoundRecord.plan).joinedload(InterviewPlanRecord.application)
        ).where(
            InterviewRoundRecord.plan.has(user_id=user_id),
            InterviewRoundRecord.scheduled_at_utc.is_not(None),
            InterviewRoundRecord.scheduled_at_utc >= start,
            InterviewRoundRecord.scheduled_at_utc <= end,
        )
        rounds = session.execute(rounds_q).scalars().all()
        for rnd in rounds:
            rnd_start = ensure_utc(rnd.scheduled_at_utc)
            events.append(
                CalendarEventResponse(
                    id=f"rnd_{rnd.id}",
                    event_type="INTERVIEW_ROUND",
                    title=f"Interview: {rnd.plan.company_name} - {rnd.round_name}",
                    description=f"Format: {rnd.interview_format}. Focus: {', '.join(rnd.focus_areas_json)}",
                    start_time_utc=rnd_start,
                    end_time_utc=rnd_start + timedelta(minutes=60),
                    candidate_timezone=candidate_timezone,
                    application_id=rnd.plan.application_id,
                    company_name=rnd.plan.company_name,
                    is_completed=(rnd.status == "COMPLETED"),
                )
            )

        events.sort(key=lambda x: x.start_time_utc)
        return events

    @classmethod
    def check_schedule_conflicts(
        cls,
        session: Session,
        user_id: str,
        target_time_utc: datetime,
        duration_minutes: int = 60,
    ) -> ScheduleConflictCheck:
        """
        Detects schedule overlaps around target_time_utc (+/- duration_minutes)
        against candidate reminders and interview rounds.
        """
        target = ensure_utc(target_time_utc)
        start_win = target - timedelta(minutes=duration_minutes - 1)
        end_win = target + timedelta(minutes=duration_minutes - 1)

        events = cls.get_calendar_events(
            session=session,
            user_id=user_id,
            start_utc=start_win,
            end_utc=end_win,
        )

        return ScheduleConflictCheck(
            has_conflicts=len(events) > 0,
            conflict_count=len(events),
            conflicting_events=events,
        )

    @classmethod
    def _to_reminder_response(cls, r: ReminderRecord) -> ReminderResponse:
        return ReminderResponse(
            id=r.id,
            user_id=r.user_id,
            application_id=r.application_id,
            title=r.title,
            description=r.description,
            reminder_type=ReminderType(r.reminder_type),
            due_at_utc=ensure_utc(r.due_at_utc),
            timezone=r.timezone,
            is_completed=r.is_completed,
            completed_at=ensure_utc(r.completed_at),
            created_at=ensure_utc(r.created_at),
        )
