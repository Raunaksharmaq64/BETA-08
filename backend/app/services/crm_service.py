"""
RIGHT FIT — Application CRM & Lifecycle State Machine Service
Phase: 8 — CRM and Interview Intelligence

Implements:
1. Strict, auditable application state machine
2. External Apply link tracking with mandatory manual confirmation for APPLIED status
3. Application status history trail and candidate private notes
4. CRM metrics & dashboard summaries
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    ApplicationNoteRecord,
    ApplicationRecord,
    ApplicationStatusHistoryRecord,
    CanonicalOpportunityRecord,
)
from contracts.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationNoteCreate,
    ApplicationNoteResponse,
    ApplicationResponse,
    ApplicationStatsResponse,
    ApplicationStatus,
    ApplicationTransitionRequest,
    ApplicationUpdateRequest,
    NoteType,
    StatusHistoryItem,
)


# Explicit State Machine Graph
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    ApplicationStatus.SAVED.value: {
        ApplicationStatus.PLANNING_TO_APPLY.value,
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.WITHDRAWN.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.PLANNING_TO_APPLY.value: {
        ApplicationStatus.SAVED.value,
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.ASSESSMENT.value,
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.OFFER.value,
        ApplicationStatus.REJECTED.value,
        ApplicationStatus.WITHDRAWN.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.APPLIED.value: {
        ApplicationStatus.PLANNING_TO_APPLY.value,
        ApplicationStatus.ASSESSMENT.value,
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.OFFER.value,
        ApplicationStatus.REJECTED.value,
        ApplicationStatus.GHOSTED.value,
        ApplicationStatus.WITHDRAWN.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.ASSESSMENT.value: {
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.OFFER.value,
        ApplicationStatus.REJECTED.value,
        ApplicationStatus.GHOSTED.value,
        ApplicationStatus.WITHDRAWN.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.INTERVIEW.value: {
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.ASSESSMENT.value,
        ApplicationStatus.OFFER.value,
        ApplicationStatus.REJECTED.value,
        ApplicationStatus.GHOSTED.value,
        ApplicationStatus.WITHDRAWN.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.OFFER.value: {
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.CLOSED.value,
        ApplicationStatus.REJECTED.value,
        ApplicationStatus.WITHDRAWN.value,
        ApplicationStatus.APPLIED.value,
    },
    ApplicationStatus.REJECTED.value: {
        ApplicationStatus.SAVED.value,
        ApplicationStatus.PLANNING_TO_APPLY.value,
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.WITHDRAWN.value: {
        ApplicationStatus.SAVED.value,
        ApplicationStatus.PLANNING_TO_APPLY.value,
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.GHOSTED.value: {
        ApplicationStatus.INTERVIEW.value,
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.REJECTED.value,
        ApplicationStatus.CLOSED.value,
    },
    ApplicationStatus.CLOSED.value: {
        ApplicationStatus.SAVED.value,
        ApplicationStatus.PLANNING_TO_APPLY.value,
        ApplicationStatus.APPLIED.value,
        ApplicationStatus.INTERVIEW.value,
    },
}


class CRMService:
    """Manages the full lifecycle of candidate career applications and notes."""

    @classmethod
    def create_application(
        cls,
        session: Session,
        user_id: str,
        req: ApplicationCreateRequest,
    ) -> ApplicationResponse:
        """Initializes a new job application tracking entity."""
        now = datetime.now(timezone.utc)

        # Populate from canonical opportunity if linked
        app_url = req.application_url
        if req.opportunity_id and not app_url:
            opp = session.get(CanonicalOpportunityRecord, req.opportunity_id)
            if opp:
                app_url = opp.application_url

        app_record = ApplicationRecord(
            user_id=user_id,
            opportunity_id=req.opportunity_id,
            company_name=req.company_name,
            job_title=req.job_title,
            application_url=app_url,
            status=req.status.value,
            salary_offered=req.salary_offered,
            salary_currency=req.salary_currency,
            contact_name=req.contact_name,
            contact_email=req.contact_email,
            is_submission_confirmed=(req.status == ApplicationStatus.APPLIED),
            applied_at=now if req.status == ApplicationStatus.APPLIED else None,
        )
        session.add(app_record)
        session.flush()

        # Initial history record
        hist = ApplicationStatusHistoryRecord(
            application_id=app_record.id,
            from_status=None,
            to_status=app_record.status,
            changed_at=now,
            actor_type="CANDIDATE",
            actor_id=user_id,
            reason="Application created in CRM.",
        )
        session.add(hist)

        # Initial note if provided
        if req.initial_notes:
            note = ApplicationNoteRecord(
                application_id=app_record.id,
                user_id=user_id,
                note_type=NoteType.GENERAL.value,
                content=req.initial_notes,
            )
            session.add(note)

        session.commit()
        session.refresh(app_record)
        return cls._to_application_response(app_record)

    @classmethod
    def transition_status(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
        req: ApplicationTransitionRequest,
    ) -> ApplicationResponse:
        """
        Validates and executes an explicit application state machine transition.
        Enforces candidate confirmation before marking as APPLIED.
        """
        app_record = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app_record:
            raise ValueError(f"Application '{application_id}' not found.")

        current_status = app_record.status
        target_status = req.to_status.value

        if current_status == target_status:
            return cls._to_application_response(app_record)

        # Validate against allowed transitions
        allowed = VALID_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise ValueError(
                f"Invalid transition from '{current_status}' to '{target_status}'. "
                f"Allowed target states: {sorted(list(allowed))}"
            )

        # Critical rule: Cannot mark as APPLIED without explicit submission confirmation
        if target_status == ApplicationStatus.APPLIED.value and not req.confirm_submission:
            raise ValueError(
                "Mandatory requirement: Candidate must explicitly confirm submission before status can transition to APPLIED. "
                "Opening the employer application link does not constitute a completed submission."
            )

        now = datetime.now(timezone.utc)
        app_record.status = target_status
        if target_status == ApplicationStatus.APPLIED.value:
            app_record.is_submission_confirmed = True
            if not app_record.applied_at:
                app_record.applied_at = now

        # Record history
        hist = ApplicationStatusHistoryRecord(
            application_id=app_record.id,
            from_status=current_status,
            to_status=target_status,
            changed_at=now,
            actor_type="CANDIDATE",
            actor_id=user_id,
            reason=req.reason or f"Transitioned from {current_status} to {target_status}.",
        )
        session.add(hist)
        session.commit()
        session.refresh(app_record)
        return cls._to_application_response(app_record)

    @classmethod
    def record_apply_link_opened(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
    ) -> ApplicationResponse:
        """
        Records that candidate opened the employer's external application page.
        Transitions SAVED to PLANNING_TO_APPLY, but NEVER automatically marks as APPLIED.
        """
        app_record = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app_record:
            raise ValueError(f"Application '{application_id}' not found.")

        now = datetime.now(timezone.utc)
        app_record.apply_link_opened_at = now

        # Move to PLANNING_TO_APPLY if currently SAVED
        if app_record.status == ApplicationStatus.SAVED.value:
            app_record.status = ApplicationStatus.PLANNING_TO_APPLY.value
            hist = ApplicationStatusHistoryRecord(
                application_id=app_record.id,
                from_status=ApplicationStatus.SAVED.value,
                to_status=ApplicationStatus.PLANNING_TO_APPLY.value,
                changed_at=now,
                actor_type="SYSTEM",
                actor_id="system",
                reason="Candidate opened employer application portal.",
            )
            session.add(hist)

        session.commit()
        session.refresh(app_record)
        return cls._to_application_response(app_record)

    @classmethod
    def list_applications(
        cls,
        session: Session,
        user_id: str,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ApplicationResponse]:
        """Lists candidate applications with optional status and company/title filtering."""
        query = select(ApplicationRecord).where(ApplicationRecord.user_id == user_id)

        if status:
            query = query.where(ApplicationRecord.status == status.upper())
        if search:
            term = f"%{search.strip().lower()}%"
            query = query.where(
                func.lower(ApplicationRecord.company_name).ilike(term) |
                func.lower(ApplicationRecord.job_title).ilike(term)
            )

        query = query.order_by(ApplicationRecord.updated_at.desc())
        records = session.execute(query).scalars().all()
        return [cls._to_application_response(r) for r in records]

    @classmethod
    def get_application(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
    ) -> Optional[ApplicationResponse]:
        """Retrieves single application with complete status history and recent notes."""
        app_record = session.execute(
            select(ApplicationRecord)
            .options(
                joinedload(ApplicationRecord.status_history),
                joinedload(ApplicationRecord.notes),
            )
            .where(
                ApplicationRecord.id == application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app_record:
            return None

        return cls._to_application_response(app_record)

    @classmethod
    def update_application(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
        req: ApplicationUpdateRequest,
    ) -> Optional[ApplicationResponse]:
        """Updates editable application fields."""
        app_record = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app_record:
            return None

        if req.company_name is not None:
            app_record.company_name = req.company_name
        if req.job_title is not None:
            app_record.job_title = req.job_title
        if req.application_url is not None:
            app_record.application_url = req.application_url
        if req.current_stage is not None:
            app_record.current_stage = req.current_stage
        if req.contact_name is not None:
            app_record.contact_name = req.contact_name
        if req.contact_email is not None:
            app_record.contact_email = req.contact_email
        if req.salary_offered is not None:
            app_record.salary_offered = req.salary_offered
        if req.salary_currency is not None:
            app_record.salary_currency = req.salary_currency

        session.commit()
        session.refresh(app_record)
        return cls._to_application_response(app_record)

    @classmethod
    def delete_application(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
    ) -> bool:
        """Deletes an application and cascades all child notes, history, and reminders."""
        app_record = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app_record:
            return False

        session.delete(app_record)
        session.commit()
        return True

    # --------------------------------------------------------------------------
    # Application Notes
    # --------------------------------------------------------------------------

    @classmethod
    def add_note(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
        req: ApplicationNoteCreate,
    ) -> ApplicationNoteResponse:
        """Adds a private note to candidate application."""
        app_record = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app_record:
            raise ValueError(f"Application '{application_id}' not found.")

        note = ApplicationNoteRecord(
            application_id=application_id,
            user_id=user_id,
            note_type=req.note_type.value,
            content=req.content,
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        return ApplicationNoteResponse(
            id=note.id,
            application_id=note.application_id,
            user_id=note.user_id,
            note_type=NoteType(note.note_type),
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    @classmethod
    def list_notes(
        cls,
        session: Session,
        application_id: str,
        user_id: str,
    ) -> List[ApplicationNoteResponse]:
        """Lists all private notes for specified application."""
        notes = session.execute(
            select(ApplicationNoteRecord)
            .where(
                ApplicationNoteRecord.application_id == application_id,
                ApplicationNoteRecord.user_id == user_id,
            )
            .order_by(ApplicationNoteRecord.created_at.desc())
        ).scalars().all()

        return [
            ApplicationNoteResponse(
                id=n.id,
                application_id=n.application_id,
                user_id=n.user_id,
                note_type=NoteType(n.note_type),
                content=n.content,
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in notes
        ]

    @classmethod
    def delete_note(
        cls,
        session: Session,
        note_id: str,
        user_id: str,
    ) -> bool:
        """Deletes a private note."""
        note = session.execute(
            select(ApplicationNoteRecord).where(
                ApplicationNoteRecord.id == note_id,
                ApplicationNoteRecord.user_id == user_id,
            )
        ).scalars().first()

        if not note:
            return False

        session.delete(note)
        session.commit()
        return True

    # --------------------------------------------------------------------------
    # CRM Stats & Dashboard
    # --------------------------------------------------------------------------

    @classmethod
    def get_stats(cls, session: Session, user_id: str) -> ApplicationStatsResponse:
        """Computes live CRM pipeline statistics."""
        apps = session.execute(
            select(ApplicationRecord).where(ApplicationRecord.user_id == user_id)
        ).scalars().all()

        total = len(apps)
        by_status: Dict[str, int] = {}
        for a in apps:
            by_status[a.status] = by_status.get(a.status, 0) + 1

        active_interviews = by_status.get(ApplicationStatus.INTERVIEW.value, 0)
        offers_received = by_status.get(ApplicationStatus.OFFER.value, 0)
        pending_follow_ups = by_status.get(ApplicationStatus.APPLIED.value, 0) + by_status.get(ApplicationStatus.ASSESSMENT.value, 0)
        active_pipeline = (
            by_status.get(ApplicationStatus.PLANNING_TO_APPLY.value, 0)
            + by_status.get(ApplicationStatus.APPLIED.value, 0)
            + by_status.get(ApplicationStatus.ASSESSMENT.value, 0)
            + by_status.get(ApplicationStatus.INTERVIEW.value, 0)
        )
        rejections_received = by_status.get(ApplicationStatus.REJECTED.value, 0)
        stalled_or_ghosted = by_status.get(ApplicationStatus.GHOSTED.value, 0)

        return ApplicationStatsResponse(
            total_applications=total,
            by_status=by_status,
            active_interviews=active_interviews,
            pending_follow_ups=pending_follow_ups,
            offers_received=offers_received,
            active_pipeline=active_pipeline,
            interviews_scheduled=active_interviews,
            rejections_received=rejections_received,
            stalled_or_ghosted=stalled_or_ghosted,
        )

    @classmethod
    def _to_application_response(cls, app: ApplicationRecord) -> ApplicationResponse:
        hist_items = []
        if hasattr(app, "status_history") and app.status_history:
            hist_items = [
                StatusHistoryItem(
                    id=h.id,
                    from_status=h.from_status,
                    to_status=h.to_status,
                    changed_at=h.changed_at,
                    actor_type=h.actor_type,
                    actor_id=h.actor_id,
                    reason=h.reason,
                )
                for h in app.status_history
            ]

        recent_notes = []
        notes_count = 0
        if hasattr(app, "notes") and app.notes:
            notes_count = len(app.notes)
            recent_notes = [
                ApplicationNoteResponse(
                    id=n.id,
                    application_id=n.application_id,
                    user_id=n.user_id,
                    note_type=NoteType(n.note_type),
                    content=n.content,
                    created_at=n.created_at,
                    updated_at=n.updated_at,
                )
                for n in app.notes[:5]
            ]

        return ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            opportunity_id=app.opportunity_id,
            company_name=app.company_name,
            job_title=app.job_title,
            company_display=app.company_name,
            title_display=app.job_title,
            application_url=app.application_url,
            status=ApplicationStatus(app.status),
            applied_at=app.applied_at,
            apply_link_opened_at=app.apply_link_opened_at,
            is_submission_confirmed=app.is_submission_confirmed,
            current_stage=app.current_stage,
            salary_offered=app.salary_offered,
            salary_currency=app.salary_currency,
            contact_name=app.contact_name,
            contact_email=app.contact_email,
            created_at=app.created_at,
            updated_at=app.updated_at,
            notes_count=notes_count,
            status_history=hist_items,
            recent_notes=recent_notes,
        )

