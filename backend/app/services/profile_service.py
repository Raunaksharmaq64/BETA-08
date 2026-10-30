"""
RIGHT FIT Core — Candidate Profile & Provenance Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    CandidatePreferenceRecord,
    CandidateProfile,
    CandidateSkillRecord,
    EducationRecord,
    ExperienceRecord,
    utc_now,
)
from contracts.profile.schemas import (
    CandidateProfileResponse,
    CandidateProfileUpdate,
    EducationCreate,
    EducationResponse,
    ExperienceCreate,
    ExperienceResponse,
    ProfileCompletenessResponse,
    SkillCreate,
    SkillResponse,
)


class ProfileService:
    @staticmethod
    async def get_or_create_profile(db: AsyncSession, user_id: str) -> CandidateProfile:
        """Retrieves or creates candidate profile for user."""
        query = (
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(
                selectinload(CandidateProfile.education),
                selectinload(CandidateProfile.experience),
                selectinload(CandidateProfile.skills),
                selectinload(CandidateProfile.preferences),
            )
        )
        res = await db.execute(query)
        profile = res.scalar_one_or_none()

        if not profile:
            profile = CandidateProfile(
                user_id=user_id,
                headline="Candidate",
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
            # Reload with relationships
            return await ProfileService.get_or_create_profile(db, user_id)
        return profile

    @staticmethod
    async def get_profile_response(db: AsyncSession, user_id: str) -> CandidateProfileResponse:
        """Returns normalized candidate profile schema."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            headline=profile.headline,
            summary=profile.summary,
            phone=profile.phone,
            city=profile.city,
            state=profile.state,
            country=profile.country,
            timezone=profile.timezone,
            education=[
                EducationResponse(
                    id=e.id,
                    institution=e.institution,
                    degree=e.degree,
                    field_of_study=e.field_of_study,
                    start_date=e.start_date,
                    end_date=e.end_date,
                    is_current=e.is_current,
                    achievements=e.achievements,
                    provenance=e.provenance,
                )
                for e in profile.education
            ],
            experience=[
                ExperienceResponse(
                    id=exp.id,
                    company=exp.company,
                    role=exp.role,
                    employment_type=exp.employment_type,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    is_current=exp.is_current,
                    description=exp.description,
                    skills=exp.skills_json or [],
                    provenance=exp.provenance,
                )
                for exp in profile.experience
            ],
            skills=[
                SkillResponse(
                    id=s.id,
                    skill_name=s.skill_name,
                    category=s.category,
                    proficiency=s.proficiency,
                    years_experience=s.years_experience,
                    provenance=s.provenance,
                )
                for s in profile.skills
            ],
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: str,
        update_data: CandidateProfileUpdate,
    ) -> CandidateProfileResponse:
        """Updates personal and contact details."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        profile.updated_at = utc_now()
        await db.commit()
        return await ProfileService.get_profile_response(db, user_id)

    @staticmethod
    async def add_education(
        db: AsyncSession,
        user_id: str,
        edu_data: EducationCreate,
    ) -> EducationResponse:
        """Appends an education credential to profile."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        record = EducationRecord(
            profile_id=profile.id,
            institution=edu_data.institution,
            degree=edu_data.degree,
            field_of_study=edu_data.field_of_study,
            start_date=edu_data.start_date,
            end_date=edu_data.end_date,
            is_current=edu_data.is_current,
            achievements=edu_data.achievements,
            provenance=str(edu_data.provenance),
        )
        db.add(record)
        profile.updated_at = utc_now()
        await db.commit()
        await db.refresh(record)
        return EducationResponse(
            id=record.id,
            institution=record.institution,
            degree=record.degree,
            field_of_study=record.field_of_study,
            start_date=record.start_date,
            end_date=record.end_date,
            is_current=record.is_current,
            achievements=record.achievements,
            provenance=record.provenance,
        )

    @staticmethod
    async def delete_education(db: AsyncSession, user_id: str, edu_id: str) -> None:
        """Deletes an education record with strict ownership verification."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        query = select(EducationRecord).where(
            EducationRecord.id == edu_id,
            EducationRecord.profile_id == profile.id,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Education record not found or not owned by user.",
            )
        await db.delete(record)
        profile.updated_at = utc_now()
        await db.commit()

    @staticmethod
    async def add_experience(
        db: AsyncSession,
        user_id: str,
        exp_data: ExperienceCreate,
    ) -> ExperienceResponse:
        """Appends a professional experience entry to profile."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        record = ExperienceRecord(
            profile_id=profile.id,
            company=exp_data.company,
            role=exp_data.role,
            employment_type=exp_data.employment_type,
            start_date=exp_data.start_date,
            end_date=exp_data.end_date,
            is_current=exp_data.is_current,
            description=exp_data.description,
            skills_json=exp_data.skills,
            provenance=str(exp_data.provenance),
        )
        db.add(record)
        profile.updated_at = utc_now()
        await db.commit()
        await db.refresh(record)
        return ExperienceResponse(
            id=record.id,
            company=record.company,
            role=record.role,
            employment_type=record.employment_type,
            start_date=record.start_date,
            end_date=record.end_date,
            is_current=record.is_current,
            description=record.description,
            skills=record.skills_json,
            provenance=record.provenance,
        )

    @staticmethod
    async def delete_experience(db: AsyncSession, user_id: str, exp_id: str) -> None:
        """Deletes a professional experience record with strict ownership verification."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        query = select(ExperienceRecord).where(
            ExperienceRecord.id == exp_id,
            ExperienceRecord.profile_id == profile.id,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience record not found or not owned by user.",
            )
        await db.delete(record)
        profile.updated_at = utc_now()
        await db.commit()

    @staticmethod
    async def add_skill(
        db: AsyncSession,
        user_id: str,
        skill_data: SkillCreate,
    ) -> SkillResponse:
        """Appends a skill attribute to profile."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        record = CandidateSkillRecord(
            profile_id=profile.id,
            skill_name=skill_data.skill_name.strip(),
            category=skill_data.category,
            proficiency=skill_data.proficiency,
            years_experience=skill_data.years_experience,
            provenance=str(skill_data.provenance),
        )
        db.add(record)
        profile.updated_at = utc_now()
        await db.commit()
        await db.refresh(record)
        return SkillResponse(
            id=record.id,
            skill_name=record.skill_name,
            category=record.category,
            proficiency=record.proficiency,
            years_experience=record.years_experience,
            provenance=record.provenance,
        )

    @staticmethod
    async def delete_skill(db: AsyncSession, user_id: str, skill_id: str) -> None:
        """Deletes a skill record with strict ownership verification."""
        profile = await ProfileService.get_or_create_profile(db, user_id)
        query = select(CandidateSkillRecord).where(
            CandidateSkillRecord.id == skill_id,
            CandidateSkillRecord.profile_id == profile.id,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill record not found or not owned by user.",
            )
        await db.delete(record)
        profile.updated_at = utc_now()
        await db.commit()

    @staticmethod
    async def calculate_completeness(db: AsyncSession, user_id: str) -> ProfileCompletenessResponse:
        """Calculates transparent completeness percentage and identifies missing sections."""
        profile = await ProfileService.get_or_create_profile(db, user_id)

        has_basic = bool(profile.headline and profile.summary)
        has_edu = len(profile.education) > 0
        has_exp = len(profile.experience) > 0
        has_skills = len(profile.skills) >= 3

        prefs = profile.preferences
        has_prefs = bool(prefs and len(prefs.preferred_roles_json) > 0)

        score = 0
        missing: List[str] = []

        if has_basic:
            score += 20
        else:
            missing.append("Basic Profile Info (Headline & Summary)")

        if has_edu:
            score += 20
        else:
            missing.append("Education Credentials")

        if has_exp:
            score += 20
        else:
            missing.append("Professional Experience")

        if has_skills:
            score += 20
        else:
            missing.append("Skills (Add at least 3 skills)")

        if has_prefs:
            score += 20
        else:
            missing.append("Career Preferences")

        return ProfileCompletenessResponse(
            score_percentage=score,
            has_basic_info=has_basic,
            has_education=has_edu,
            has_experience=has_exp,
            has_skills=has_skills,
            has_preferences=has_prefs,
            missing_sections=missing,
        )

