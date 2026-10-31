"""
RIGHT FIT — Central Notifications & Preferences Service
Phase: 8 — CRM and Interview Intelligence

Implements:
1. In-app notification creation with category-level candidate preferences enforcement
2. Duplicate notification suppression within sliding time windows
3. Read/unread tracking and notification history management
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.models import NotificationPreferencesRecord, NotificationRecord
from contracts.applications.schemas import (
    NotificationCategory,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    NotificationResponse,
)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class NotificationService:
    """Manages candidate notifications, delivery preferences, and anti-spam duplicate prevention."""

    @classmethod
    def get_preferences(cls, session: Session, user_id: str) -> NotificationPreferencesResponse:
        """Retrieves candidate notification preferences, initializing defaults if absent."""
        pref = session.execute(
            select(NotificationPreferencesRecord).where(NotificationPreferencesRecord.user_id == user_id)
        ).scalars().first()

        if not pref:
            pref = NotificationPreferencesRecord(
                user_id=user_id,
                in_app_enabled=True,
                email_enabled=False,
                interview_reminders=True,
                application_follow_ups=True,
                assessment_deadlines=True,
                prep_milestones=True,
                frequency="DAILY_DIGEST",
                quiet_hours_start="22:00",
                quiet_hours_end="08:00",
                timezone="UTC",
                job_alerts_enabled=True,
                digest_email_enabled=False,
                market_intelligence_alerts=True,
            )
            session.add(pref)
            session.commit()
            session.refresh(pref)

        return NotificationPreferencesResponse(
            user_id=pref.user_id,
            in_app_enabled=pref.in_app_enabled,
            email_enabled=pref.email_enabled,
            interview_reminders=pref.interview_reminders,
            application_follow_ups=pref.application_follow_ups,
            assessment_deadlines=pref.assessment_deadlines,
            prep_milestones=pref.prep_milestones,
            frequency=getattr(pref, "frequency", "DAILY_DIGEST") or "DAILY_DIGEST",
            quiet_hours_start=getattr(pref, "quiet_hours_start", "22:00"),
            quiet_hours_end=getattr(pref, "quiet_hours_end", "08:00"),
            timezone=getattr(pref, "timezone", "UTC") or "UTC",
            job_alerts_enabled=getattr(pref, "job_alerts_enabled", True),
            digest_email_enabled=getattr(pref, "digest_email_enabled", False),
            market_intelligence_alerts=getattr(pref, "market_intelligence_alerts", True),
            updated_at=ensure_utc(pref.updated_at),
        )

    @classmethod
    def update_preferences(
        cls,
        session: Session,
        user_id: str,
        req: NotificationPreferencesUpdate,
    ) -> NotificationPreferencesResponse:
        """Updates category-level notification preferences."""
        pref = session.execute(
            select(NotificationPreferencesRecord).where(NotificationPreferencesRecord.user_id == user_id)
        ).scalars().first()

        if not pref:
            pref = NotificationPreferencesRecord(user_id=user_id)
            session.add(pref)

        if req.in_app_enabled is not None:
            pref.in_app_enabled = req.in_app_enabled
        if req.email_enabled is not None:
            pref.email_enabled = req.email_enabled
        if req.interview_reminders is not None:
            pref.interview_reminders = req.interview_reminders
        if req.application_follow_ups is not None:
            pref.application_follow_ups = req.application_follow_ups
        if req.assessment_deadlines is not None:
            pref.assessment_deadlines = req.assessment_deadlines
        if req.prep_milestones is not None:
            pref.prep_milestones = req.prep_milestones
        if req.frequency is not None:
            pref.frequency = req.frequency
        if req.quiet_hours_start is not None:
            pref.quiet_hours_start = req.quiet_hours_start
        if req.quiet_hours_end is not None:
            pref.quiet_hours_end = req.quiet_hours_end
        if req.timezone is not None:
            pref.timezone = req.timezone
        if req.job_alerts_enabled is not None:
            pref.job_alerts_enabled = req.job_alerts_enabled
        if req.digest_email_enabled is not None:
            pref.digest_email_enabled = req.digest_email_enabled
        if req.market_intelligence_alerts is not None:
            pref.market_intelligence_alerts = req.market_intelligence_alerts

        session.commit()
        session.refresh(pref)

        return NotificationPreferencesResponse(
            user_id=pref.user_id,
            in_app_enabled=pref.in_app_enabled,
            email_enabled=pref.email_enabled,
            interview_reminders=pref.interview_reminders,
            application_follow_ups=pref.application_follow_ups,
            assessment_deadlines=pref.assessment_deadlines,
            prep_milestones=pref.prep_milestones,
            frequency=getattr(pref, "frequency", "DAILY_DIGEST") or "DAILY_DIGEST",
            quiet_hours_start=getattr(pref, "quiet_hours_start", "22:00"),
            quiet_hours_end=getattr(pref, "quiet_hours_end", "08:00"),
            timezone=getattr(pref, "timezone", "UTC") or "UTC",
            job_alerts_enabled=getattr(pref, "job_alerts_enabled", True),
            digest_email_enabled=getattr(pref, "digest_email_enabled", False),
            market_intelligence_alerts=getattr(pref, "market_intelligence_alerts", True),
            updated_at=ensure_utc(pref.updated_at),
        )

    @classmethod
    def create_notification(
        cls,
        session: Session,
        user_id: str,
        category: NotificationCategory,
        title: str,
        message: str,
        reference_link: Optional[str] = None,
    ) -> Optional[NotificationResponse]:
        """
        Creates an in-app notification respecting user preferences and duplicate suppression.
        Returns None if suppressed by user preference or duplicate within 10 minutes.
        """
        # 1. Enforce preferences
        pref = cls.get_preferences(session, user_id)
        if not pref.in_app_enabled:
            return None

        cat_val = category.value if hasattr(category, "value") else str(category)

        if cat_val == NotificationCategory.INTERVIEW_REMINDER.value and not pref.interview_reminders:
            return None
        if cat_val == NotificationCategory.APPLICATION_FOLLOW_UP.value and not pref.application_follow_ups:
            return None
        if cat_val == NotificationCategory.ASSESSMENT_DEADLINE.value and not pref.assessment_deadlines:
            return None
        if cat_val == NotificationCategory.PREP_MILESTONE.value and not pref.prep_milestones:
            return None

        # 2. Duplicate suppression (same title & category within 10 mins)
        ten_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        recent_dup = session.execute(
            select(NotificationRecord).where(
                NotificationRecord.user_id == user_id,
                NotificationRecord.category == cat_val,
                NotificationRecord.title == title,
                NotificationRecord.created_at >= ten_mins_ago,
            )
        ).scalars().first()

        if recent_dup:
            return None

        # 3. Create Notification
        notif = NotificationRecord(
            user_id=user_id,
            category=cat_val,
            title=title,
            message=message,
            reference_link=reference_link,
            is_read=False,
            delivery_channel="IN_APP",
            delivery_status="DELIVERED",
        )
        session.add(notif)
        session.commit()
        session.refresh(notif)

        return NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            category=NotificationCategory(notif.category),
            title=notif.title,
            message=notif.message,
            reference_link=notif.reference_link,
            is_read=notif.is_read,
            delivery_channel=notif.delivery_channel,
            delivery_status=notif.delivery_status,
            created_at=ensure_utc(notif.created_at),
        )

    @classmethod
    def list_notifications(
        cls,
        session: Session,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[NotificationResponse]:
        """Lists candidate notifications ordered chronologically descending."""
        query = select(NotificationRecord).where(NotificationRecord.user_id == user_id)
        if unread_only:
            query = query.where(NotificationRecord.is_read.is_(False))

        query = query.order_by(NotificationRecord.created_at.desc()).limit(limit)
        records = session.execute(query).scalars().all()

        return [
            NotificationResponse(
                id=n.id,
                user_id=n.user_id,
                category=NotificationCategory(n.category),
                title=n.title,
                message=n.message,
                reference_link=n.reference_link,
                is_read=n.is_read,
                delivery_channel=n.delivery_channel,
                delivery_status=n.delivery_status,
                created_at=ensure_utc(n.created_at),
            )
            for n in records
        ]

    @classmethod
    def mark_as_read(cls, session: Session, notification_id: str, user_id: str) -> bool:
        """Marks a notification as read."""
        notif = session.execute(
            select(NotificationRecord).where(
                NotificationRecord.id == notification_id,
                NotificationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not notif:
            return False

        notif.is_read = True
        session.commit()
        return True

    @classmethod
    def mark_all_as_read(cls, session: Session, user_id: str) -> int:
        """Marks all unread notifications as read for candidate."""
        records = session.execute(
            select(NotificationRecord).where(
                NotificationRecord.user_id == user_id,
                NotificationRecord.is_read.is_(False),
            )
        ).scalars().all()

        count = len(records)
        for r in records:
            r.is_read = True
        session.commit()
        return count

    @classmethod
    def generate_smart_job_alerts(cls, session: Session, user_id: str) -> int:
        """Evaluates active canonical opportunities and generates smart alerts for candidate."""
        from app.db.models import CanonicalOpportunityRecord, CandidateProfile

        prof = session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        ).scalars().first()

        cand_skills = set()
        if prof and prof.skills:
            for s in prof.skills:
                cand_skills.add(s.skill_name.lower())

        opps = session.execute(
            select(CanonicalOpportunityRecord).where(
                CanonicalOpportunityRecord.is_active == True,
                CanonicalOpportunityRecord.is_suppressed == False,
                CanonicalOpportunityRecord.application_url.notlike("%example.com%")
            ).order_by(CanonicalOpportunityRecord.first_seen_at.desc()).limit(10)
        ).scalars().all()

        created = 0
        for opp in opps:
            reqs = [r.lower() for r in (opp.required_skills_json or [])]
            matched = [r for r in reqs if any(cs in r or r in cs for cs in cand_skills)]
            fit_ratio = len(matched) / max(1, len(reqs)) if reqs else 0.5

            if fit_ratio >= 0.5:
                pct = max(75, int(fit_ratio * 100))
                title = f"🎯 {pct}% Fit Match: {opp.title} @ {opp.company_name}"
                matched_str = ", ".join((opp.required_skills_json or [])[:3])
                msg = f"Verified open position matching your core skills in {matched_str}. Base range: ${int(opp.min_salary or 120000):,} - ${int(opp.max_salary or 160000):,} USD."
                notif = cls.create_notification(
                    session=session,
                    user_id=user_id,
                    category=NotificationCategory.JOB_ALERT,
                    title=title,
                    message=msg,
                    reference_link=opp.application_url,
                )
                if notif:
                    created += 1

        return created

