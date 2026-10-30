"""
RIGHT FIT Core — Candidate Preferences Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CandidatePreferenceRecord, utc_now
from app.services.profile_service import ProfileService
from contracts.profile.schemas import (
    CandidatePreferencesResponse,
    CandidatePreferencesUpdate,
    RemotePreference,
)


class PreferencesService:
    @staticmethod
    async def get_preferences(db: AsyncSession, user_id: str) -> CandidatePreferencesResponse:
        """Retrieves candidate career preferences."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        query = select(CandidatePreferenceRecord).where(CandidatePreferenceRecord.profile_id == profile.id)
        res = await db.execute(query)
        pref = res.scalar_one_or_none()

        if not pref:
            pref = CandidatePreferenceRecord(
                profile_id=profile.id,
                preferred_roles_json=[],
                preferred_skills_json=[],
                preferred_industries_json=[],
                preferred_locations_json=[],
                remote_preference="ANY",
                employment_types_json=["Full-time"],
                job_notification_frequency="DAILY",
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            db.add(pref)
            await db.commit()
            await db.refresh(pref)

        return CandidatePreferencesResponse(
            id=pref.id,
            user_id=user_id,
            preferred_roles=pref.preferred_roles_json or [],
            preferred_skills=pref.preferred_skills_json or [],
            preferred_industries=pref.preferred_industries_json or [],
            preferred_locations=pref.preferred_locations_json or [],
            remote_preference=RemotePreference(pref.remote_preference),
            min_salary=pref.min_salary,
            max_salary=pref.max_salary,
            currency=pref.currency,
            employment_types=pref.employment_types_json or [],
            job_notification_frequency=pref.job_notification_frequency,
            updated_at=pref.updated_at,
        )

    @staticmethod
    async def update_preferences(
        db: AsyncSession,
        user_id: str,
        update_data: CandidatePreferencesUpdate,
    ) -> CandidatePreferencesResponse:
        """Updates career and notification preferences."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        query = select(CandidatePreferenceRecord).where(CandidatePreferenceRecord.profile_id == profile.id)
        res = await db.execute(query)
        pref = res.scalar_one_or_none()

        if not pref:
            pref = CandidatePreferenceRecord(profile_id=profile.id)
            db.add(pref)

        pref.preferred_roles_json = update_data.preferred_roles
        pref.preferred_skills_json = update_data.preferred_skills
        pref.preferred_industries_json = update_data.preferred_industries
        pref.preferred_locations_json = update_data.preferred_locations
        pref.remote_preference = str(update_data.remote_preference)
        pref.min_salary = update_data.min_salary
        pref.max_salary = update_data.max_salary
        pref.currency = update_data.currency
        pref.employment_types_json = update_data.employment_types
        pref.job_notification_frequency = update_data.job_notification_frequency
        pref.updated_at = utc_now()

        await db.commit()
        await db.refresh(pref)

        return CandidatePreferencesResponse(
            id=pref.id,
            user_id=user_id,
            preferred_roles=pref.preferred_roles_json,
            preferred_skills=pref.preferred_skills_json,
            preferred_industries=pref.preferred_industries_json,
            preferred_locations=pref.preferred_locations_json,
            remote_preference=RemotePreference(pref.remote_preference),
            min_salary=pref.min_salary,
            max_salary=pref.max_salary,
            currency=pref.currency,
            employment_types=pref.employment_types_json,
            job_notification_frequency=pref.job_notification_frequency,
            updated_at=pref.updated_at,
        )

