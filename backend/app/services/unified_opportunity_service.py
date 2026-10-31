"""
RIGHT FIT Core — Unified Opportunities Aggregation Engine & Dashboard Service
Version: 1.0.0
Phase: 11 — Unified Opportunities Engine and Dashboard

Provides canonical opportunity aggregation, common envelope formatting,
cross-source filtering, dashboard metric reconciliation, and candidate relevance feedback.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    ApplicationRecord,
    CandidateOpportunityFeedbackRecord,
    CanonicalOpportunityRecord,
    FreelanceOpportunityRecord,
    SavedFreelanceOpportunityRecord,
    SavedJobRecord,
    SavedStartupOpportunityRecord,
    StartupOpportunityRecord,
    User,
    utc_now,
)
from app.integrations.leadhunter.adapter import leadhunter_adapter
from app.integrations.startup_intelligence.adapter import StartupIntelligenceAdapter

logger = logging.getLogger(__name__)
startup_adapter = StartupIntelligenceAdapter()


class UnifiedOpportunityService:
    """Core domain service for unified opportunity aggregation, dashboard analytics, and feedback."""

    @staticmethod
    def format_job_envelope(job: CanonicalOpportunityRecord, is_saved: bool = False) -> Dict[str, Any]:
        """Formats canonical job record into common opportunity envelope."""
        org_name = getattr(job, "company_name", None) or "Unknown Employer"
        title = getattr(job, "title", None) or "Software Opportunity"
        desc = getattr(job, "description_clean", "") or ""
        skills = getattr(job, "required_skills_json", None) or getattr(job, "skills_extracted", []) or []

        loc_parts = [p for p in [getattr(job, "city", None), getattr(job, "country", None)] if p]
        location = ", ".join(loc_parts) if loc_parts else (getattr(job, "location_raw", None) or "Remote")

        source_name = getattr(job, "source_type", None)
        try:
            if not source_name and "source" in job.__dict__ and job.source:
                source_name = getattr(job.source, "name", None)
        except Exception:
            pass
        if not source_name:
            source_name = "ATS Connector"

        app_url = getattr(job, "application_url", None) or getattr(job, "apply_url", None) or getattr(job, "source_url", "")
        pub_dt = getattr(job, "source_published_at", None) or getattr(job, "published_at", None)

        return {
            "schema_version": "1.0",
            "opportunity_id": job.id,
            "opportunity_type": "JOB",
            "title": title,
            "short_description": desc[:280] + ("..." if len(desc) > 280 else ""),
            "organization_name": org_name,
            "source_service": "core",
            "source_name": source_name,
            "source_record_id": getattr(job, "external_job_id", None) or getattr(job, "source_id", ""),
            "source_url": app_url,
            "location": location,
            "is_remote": getattr(job, "is_remote", True),
            "published_at": pub_dt.isoformat() if pub_dt else "Publication date unavailable",
            "first_discovered_at": job.first_seen_at.isoformat() if getattr(job, "first_seen_at", None) else None,
            "last_checked_at": job.last_checked_at.isoformat() if getattr(job, "last_checked_at", None) else None,
            "freshness_state": "FRESH" if (getattr(job, "verification_status", "VERIFIED") == "VERIFIED") else "STALE",
            "classification_state": getattr(job, "verification_status", "OPEN_CONFIRMED"),
            "evidence_count": 1,
            "is_saved": is_saved,
            "type_specific_payload": {
                "employer": org_name,
                "job_role": title,
                "employment_type": getattr(job, "employment_type", "FULL_TIME") or "FULL_TIME",
                "required_skills": skills if isinstance(skills, list) else [skills],
                "salary_min": getattr(job, "min_salary", None) or getattr(job, "compensation_min", None),
                "salary_max": getattr(job, "max_salary", None) or getattr(job, "compensation_max", None),
                "salary_currency": getattr(job, "currency", None) or getattr(job, "compensation_currency", "USD"),
                "apply_url": app_url,
                "fit_score": 0.85,
            },
        }

    @staticmethod
    def format_freelance_envelope(freelance: FreelanceOpportunityRecord, is_saved: bool = False) -> Dict[str, Any]:
        """Formats freelance opportunity record into common opportunity envelope."""
        client_name = getattr(freelance, "business_name", None) or "Local Business"
        title = getattr(freelance, "opportunity_title", None) or f"Website Optimization for {client_name}"
        desc = getattr(freelance, "description", None) or getattr(freelance, "classification_reason", None) or f"Discovered lead requiring technical improvements for {client_name}"
        
        raw_skills = getattr(freelance, "required_skills", None)
        if isinstance(raw_skills, list):
            skills = raw_skills
        elif isinstance(raw_skills, str):
            skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
        else:
            skills = []

        source_platform = getattr(freelance, "source", None) or getattr(freelance, "source_platform", None) or "Google Places / LeadHunter"
        site_url = getattr(freelance, "original_source_url", None) or getattr(freelance, "website", "") or ""

        return {
            "schema_version": "1.0",
            "opportunity_id": freelance.id,
            "opportunity_type": "FREELANCE",
            "title": title,
            "short_description": desc[:280] + ("..." if len(desc) > 280 else ""),
            "organization_name": client_name,
            "source_service": "leadhunter",
            "source_name": source_platform,
            "source_record_id": getattr(freelance, "leadhunter_lead_id", None) or getattr(freelance, "place_id", ""),
            "source_url": site_url,
            "location": getattr(freelance, "city", None) or getattr(freelance, "location", "Local / Remote"),
            "is_remote": getattr(freelance, "is_remote", True),
            "published_at": freelance.discovered_at.isoformat() if getattr(freelance, "discovered_at", None) else "Publication date unavailable",
            "first_discovered_at": freelance.discovered_at.isoformat() if getattr(freelance, "discovered_at", None) else None,
            "last_checked_at": freelance.last_verified_at.isoformat() if getattr(freelance, "last_verified_at", None) else None,
            "freshness_state": "FRESH",
            "classification_state": getattr(freelance, "classification_state", "POTENTIAL_FREELANCE_OPPORTUNITY"),
            "evidence_count": len(freelance.contact_evidence) if ("contact_evidence" in freelance.__dict__ and freelance.contact_evidence) else 1,
            "is_saved": is_saved,
            "type_specific_payload": {
                "client_name": client_name,
                "service_category": getattr(freelance, "service_category", "Web Engineering"),
                "required_skills": skills,
                "rating": getattr(freelance, "rating", 0.0),
                "reviews_count": getattr(freelance, "reviews_count", 0),
                "is_broken_website": getattr(freelance, "is_broken_website", False),
                "contact_evidence_status": "OBSERVED" if getattr(freelance, "phone", None) or getattr(freelance, "email", None) else "UNVERIFIED",
                "suggested_service": getattr(freelance, "suggested_service", "Website Modernization"),
                "phone": getattr(freelance, "phone", None),
                "email": getattr(freelance, "email", None),
            },
        }

    @staticmethod
    def format_startup_envelope(startup: StartupOpportunityRecord, is_saved: bool = False) -> Dict[str, Any]:
        """Formats startup problem opportunity into common opportunity envelope."""
        name = startup.startup_name or "Startup Prospect"
        title = startup.detected_signal or f"Technical Pain Point at {name}"
        desc = startup.pain_point_description or startup.ai_insight or title

        return {
            "schema_version": "1.0",
            "opportunity_id": startup.id,
            "opportunity_type": "STARTUP_PAIN_POINT",
            "title": title,
            "short_description": desc[:280] + ("..." if len(desc) > 280 else ""),
            "organization_name": name,
            "source_service": "startup_intelligence",
            "source_name": startup.primary_source or "Startup Community Feed",
            "source_record_id": startup.service_record_id,
            "source_url": startup.website_url or startup.source_url or "",
            "location": "Global / Remote",
            "is_remote": True,
            "published_at": startup.published_at.isoformat() if startup.published_at else "Publication date unavailable",
            "first_discovered_at": startup.first_seen_at.isoformat() if startup.first_seen_at else None,
            "last_checked_at": startup.last_checked_at.isoformat() if startup.last_checked_at else None,
            "freshness_state": "FRESH",
            "classification_state": startup.status or "DISCOVERED",
            "evidence_count": startup.corroboration_count or 1,
            "is_saved": is_saved,
            "type_specific_payload": {
                "startup_name": name,
                "domain": startup.domain,
                "category": startup.category,
                "urgency_score": startup.urgency_score,
                "pain_point_description": desc,
                "corroboration_count": startup.corroboration_count,
                "has_conflicting_evidence": startup.has_conflicting_evidence,
                "ai_summary": startup.ai_insight or startup.ai_opportunity,
                "tech_stack": [tf.technology_name for tf in startup.tech_findings] if ("tech_findings" in startup.__dict__ and startup.tech_findings) else [],
            },
        }

    @staticmethod
    async def aggregate_opportunities(
        session: AsyncSession,
        opportunity_type: str = "ALL",
        search: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        min_score: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes multi-source aggregation across Jobs, Freelance, and Startups.
        Returns common envelopes, per-type counts, and service availability metadata.
        """
        jobs_list: List[Dict[str, Any]] = []
        freelance_list: List[Dict[str, Any]] = []
        startups_list: List[Dict[str, Any]] = []

        # Determine saved opportunity IDs for user
        saved_job_ids = set()
        saved_freelance_ids = set()
        saved_startup_ids = set()

        if user_id:
            sj_res = await session.execute(select(SavedJobRecord.opportunity_id).where(SavedJobRecord.user_id == user_id))
            saved_job_ids = set(sj_res.scalars().all())

            sf_res = await session.execute(select(SavedFreelanceOpportunityRecord.opportunity_id).where(SavedFreelanceOpportunityRecord.user_id == user_id))
            saved_freelance_ids = set(sf_res.scalars().all())

            ss_res = await session.execute(select(SavedStartupOpportunityRecord.opportunity_id).where(SavedStartupOpportunityRecord.user_id == user_id))
            saved_startup_ids = set(ss_res.scalars().all())

        # 1. Fetch Jobs
        if opportunity_type in ("ALL", "JOB"):
            jq = select(CanonicalOpportunityRecord)
            if search:
                s_term = f"%{search.strip()}%"
                jq = jq.where(or_(CanonicalOpportunityRecord.title.ilike(s_term), CanonicalOpportunityRecord.company_name.ilike(s_term)))
            if source and source != "All":
                jq = jq.where(CanonicalOpportunityRecord.company_name.ilike(f"%{source}%"))
            jq = jq.order_by(CanonicalOpportunityRecord.first_seen_at.desc()).limit(100)
            j_res = await session.execute(jq)
            for j in j_res.scalars().all():
                jobs_list.append(UnifiedOpportunityService.format_job_envelope(j, is_saved=j.id in saved_job_ids))

        # 2. Fetch Freelance
        if opportunity_type in ("ALL", "FREELANCE"):
            fq = select(FreelanceOpportunityRecord)
            if search:
                s_term = f"%{search.strip()}%"
                fq = fq.where(or_(FreelanceOpportunityRecord.business_name.ilike(s_term), FreelanceOpportunityRecord.opportunity_title.ilike(s_term)))
            if category and category != "All":
                fq = fq.where(FreelanceOpportunityRecord.service_category == category)
            if source and source != "All":
                fq = fq.where(FreelanceOpportunityRecord.source.ilike(f"%{source}%"))
            fq = fq.order_by(FreelanceOpportunityRecord.discovered_at.desc()).limit(100)
            f_res = await session.execute(fq)
            for f in f_res.scalars().all():
                freelance_list.append(UnifiedOpportunityService.format_freelance_envelope(f, is_saved=f.id in saved_freelance_ids))

        # 3. Fetch Startups
        if opportunity_type in ("ALL", "STARTUP_PAIN_POINT"):
            sq = select(StartupOpportunityRecord)
            if search:
                s_term = f"%{search.strip()}%"
                sq = sq.where(or_(StartupOpportunityRecord.startup_name.ilike(s_term), StartupOpportunityRecord.detected_signal.ilike(s_term)))
            if category and category != "All":
                sq = sq.where(StartupOpportunityRecord.category == category)
            if source and source != "All":
                sq = sq.where(StartupOpportunityRecord.primary_source.ilike(f"%{source}%"))
            if min_score:
                sq = sq.where(StartupOpportunityRecord.urgency_score >= min_score)
            sq = sq.order_by(StartupOpportunityRecord.urgency_score.desc(), StartupOpportunityRecord.first_seen_at.desc()).limit(100)
            s_res = await session.execute(sq)
            for s in s_res.scalars().all():
                startups_list.append(UnifiedOpportunityService.format_startup_envelope(s, is_saved=s.id in saved_startup_ids))

        # Interleave / merge according to selected type
        combined: List[Dict[str, Any]] = []
        if opportunity_type == "JOB":
            combined = jobs_list
        elif opportunity_type == "FREELANCE":
            combined = freelance_list
        elif opportunity_type == "STARTUP_PAIN_POINT":
            combined = startups_list
        else:
            # Round-robin or sort by first_discovered_at
            combined = jobs_list + freelance_list + startups_list
            combined.sort(key=lambda x: x.get("first_discovered_at") or "", reverse=True)

        total_count = len(combined)
        offset = max(0, (page - 1) * per_page)
        paged_items = combined[offset : offset + per_page]

        # Service Health Metadata
        lh_state = leadhunter_adapter.circuit_breaker.state.value
        si_state = startup_adapter.circuit_breaker.state.value
        all_available = lh_state == "CLOSED" and si_state == "CLOSED"

        return {
            "success": True,
            "data": paged_items,
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "counts_by_type": {
                "jobs": len(jobs_list),
                "freelance": len(freelance_list),
                "startup_pain_points": len(startups_list),
                "total": total_count,
            },
            "service_availability": {
                "aggregation_state": "ALL_SERVICES_AVAILABLE" if all_available else "ONE_OR_MORE_SERVICES_UNAVAILABLE",
                "core": "AVAILABLE",
                "leadhunter": "AVAILABLE" if lh_state == "CLOSED" else "DEGRADED",
                "startup_intelligence": "AVAILABLE" if si_state == "CLOSED" else "DEGRADED",
                "is_partial_results": not all_available,
            },
        }

    @staticmethod
    async def get_unified_dashboard_metrics(
        session: AsyncSession,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculates reconciled summary counts across all opportunity types and candidate CRM records."""
        # 1. Total Jobs
        jobs_count_res = await session.execute(select(func.count(CanonicalOpportunityRecord.id)))
        total_jobs = jobs_count_res.scalar() or 0

        # 2. Total Freelance
        freelance_count_res = await session.execute(select(func.count(FreelanceOpportunityRecord.id)))
        total_freelance = freelance_count_res.scalar() or 0

        # 3. Total Startups
        startups_count_res = await session.execute(select(func.count(StartupOpportunityRecord.id)))
        total_startups = startups_count_res.scalar() or 0

        # 4. Total Saved
        total_saved = 0
        active_apps = 0
        if user_id:
            sj = await session.execute(select(func.count(SavedJobRecord.id)).where(SavedJobRecord.user_id == user_id))
            sf = await session.execute(select(func.count(SavedFreelanceOpportunityRecord.id)).where(SavedFreelanceOpportunityRecord.user_id == user_id))
            ss = await session.execute(select(func.count(SavedStartupOpportunityRecord.id)).where(SavedStartupOpportunityRecord.user_id == user_id))
            total_saved = (sj.scalar() or 0) + (sf.scalar() or 0) + (ss.scalar() or 0)

            # CRM Active Applications
            app_res = await session.execute(select(func.count(ApplicationRecord.id)).where(ApplicationRecord.user_id == user_id))
            active_apps = app_res.scalar() or 0

        # 5. High Urgency Startups (Urgency >= 8)
        high_urgency_res = await session.execute(
            select(func.count(StartupOpportunityRecord.id)).where(StartupOpportunityRecord.urgency_score >= 8)
        )
        high_urgency = high_urgency_res.scalar() or 0

        # 6. New This Week (discovered within last 7 days)
        one_week_ago = utc_now() - timedelta(days=7)
        new_jobs = await session.execute(select(func.count(CanonicalOpportunityRecord.id)).where(CanonicalOpportunityRecord.first_seen_at >= one_week_ago))
        new_freelance = await session.execute(select(func.count(FreelanceOpportunityRecord.id)).where(FreelanceOpportunityRecord.discovered_at >= one_week_ago))
        new_startups = await session.execute(select(func.count(StartupOpportunityRecord.id)).where(StartupOpportunityRecord.first_seen_at >= one_week_ago))
        new_this_week = (new_jobs.scalar() or 0) + (new_freelance.scalar() or 0) + (new_startups.scalar() or 0)

        # 7. Recent 6 Opportunities Across Modules
        recent_agg = await UnifiedOpportunityService.aggregate_opportunities(session, per_page=6, user_id=user_id)

        # 8. Service Health Check
        lh_state = leadhunter_adapter.circuit_breaker.state.value
        si_state = startup_adapter.circuit_breaker.state.value

        return {
            "summary_metrics": {
                "total_opportunities": total_jobs + total_freelance + total_startups,
                "total_jobs": total_jobs,
                "total_freelance": total_freelance,
                "total_startups": total_startups,
                "total_saved": total_saved,
                "active_applications": active_apps,
                "high_urgency_signals": high_urgency,
                "new_this_week": new_this_week,
            },
            "source_health": {
                "core_career_engine": "HEALTHY",
                "leadhunter_satellite": "DEGRADED" if lh_state == "OPEN" else "HEALTHY",
                "startup_intelligence_satellite": "DEGRADED" if si_state == "OPEN" else "HEALTHY",
                "all_systems_operational": lh_state != "OPEN" and si_state != "OPEN",
            },
            "recent_opportunities": recent_agg["data"],
        }

    @staticmethod
    async def list_all_saved_opportunities(
        user_id: str,
        session: AsyncSession,
    ) -> List[Dict[str, Any]]:
        """Retrieves unified saved items for a candidate across Jobs, Freelance, and Startups."""
        results: List[Dict[str, Any]] = []

        # 1. Saved Jobs
        sj_stmt = (
            select(SavedJobRecord)
            .options(selectinload(SavedJobRecord.opportunity))
            .where(SavedJobRecord.user_id == user_id)
            .order_by(SavedJobRecord.created_at.desc())
        )
        sj_res = await session.execute(sj_stmt)
        for sj in sj_res.scalars().all():
            if sj.opportunity:
                env = UnifiedOpportunityService.format_job_envelope(sj.opportunity, is_saved=True)
                env["saved_id"] = sj.id
                env["saved_notes"] = sj.notes
                env["saved_at"] = sj.created_at.isoformat() if sj.created_at else None
                results.append(env)

        # 2. Saved Freelance
        sf_stmt = (
            select(SavedFreelanceOpportunityRecord)
            .options(selectinload(SavedFreelanceOpportunityRecord.opportunity))
            .where(SavedFreelanceOpportunityRecord.user_id == user_id)
            .order_by(SavedFreelanceOpportunityRecord.created_at.desc())
        )
        sf_res = await session.execute(sf_stmt)
        for sf in sf_res.scalars().all():
            if sf.opportunity:
                env = UnifiedOpportunityService.format_freelance_envelope(sf.opportunity, is_saved=True)
                env["saved_id"] = sf.id
                env["saved_notes"] = sf.notes
                env["saved_at"] = sf.created_at.isoformat() if sf.created_at else None
                results.append(env)

        # 3. Saved Startups
        ss_stmt = (
            select(SavedStartupOpportunityRecord)
            .options(selectinload(SavedStartupOpportunityRecord.opportunity))
            .where(SavedStartupOpportunityRecord.user_id == user_id)
            .order_by(SavedStartupOpportunityRecord.created_at.desc())
        )
        ss_res = await session.execute(ss_stmt)
        for ss in ss_res.scalars().all():
            if ss.opportunity:
                env = UnifiedOpportunityService.format_startup_envelope(ss.opportunity, is_saved=True)
                env["saved_id"] = ss.id
                env["saved_notes"] = ss.notes
                env["saved_at"] = ss.created_at.isoformat() if ss.created_at else None
                results.append(env)

        # Sort all saved items newest first
        results.sort(key=lambda x: x.get("saved_at") or "", reverse=True)
        return results

    @staticmethod
    async def save_unified_opportunity(
        user_id: str,
        opportunity_type: str,
        opportunity_id: str,
        notes: Optional[str],
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """Polymorphically bookmarks an opportunity of any supported type."""
        opp_type = opportunity_type.upper()
        if opp_type == "JOB":
            # Check existing
            stmt = select(SavedJobRecord).where(SavedJobRecord.user_id == user_id, SavedJobRecord.opportunity_id == opportunity_id)
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                existing.notes = notes
                await session.commit()
                return {"saved_id": existing.id, "opportunity_type": "JOB", "opportunity_id": opportunity_id}
            new_s = SavedJobRecord(user_id=user_id, opportunity_id=opportunity_id, notes=notes)
            session.add(new_s)
            await session.commit()
            return {"saved_id": new_s.id, "opportunity_type": "JOB", "opportunity_id": opportunity_id}

        elif opp_type == "FREELANCE":
            stmt = select(SavedFreelanceOpportunityRecord).where(
                SavedFreelanceOpportunityRecord.user_id == user_id, SavedFreelanceOpportunityRecord.opportunity_id == opportunity_id
            )
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                existing.notes = notes
                await session.commit()
                return {"saved_id": existing.id, "opportunity_type": "FREELANCE", "opportunity_id": opportunity_id}
            new_s = SavedFreelanceOpportunityRecord(user_id=user_id, opportunity_id=opportunity_id, notes=notes)
            session.add(new_s)
            await session.commit()
            return {"saved_id": new_s.id, "opportunity_type": "FREELANCE", "opportunity_id": opportunity_id}

        elif opp_type in ("STARTUP_PAIN_POINT", "STARTUP"):
            stmt = select(SavedStartupOpportunityRecord).where(
                SavedStartupOpportunityRecord.user_id == user_id, SavedStartupOpportunityRecord.opportunity_id == opportunity_id
            )
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                existing.notes = notes
                await session.commit()
                return {"saved_id": existing.id, "opportunity_type": "STARTUP_PAIN_POINT", "opportunity_id": opportunity_id}
            new_s = SavedStartupOpportunityRecord(user_id=user_id, opportunity_id=opportunity_id, notes=notes)
            session.add(new_s)
            await session.commit()
            return {"saved_id": new_s.id, "opportunity_type": "STARTUP_PAIN_POINT", "opportunity_id": opportunity_id}

        raise ValueError(f"Unsupported opportunity type: {opportunity_type}")

    @staticmethod
    async def unsave_unified_opportunity(
        user_id: str,
        opportunity_type: str,
        opportunity_id: str,
        session: AsyncSession,
    ) -> bool:
        """Polymorphically removes bookmark."""
        opp_type = opportunity_type.upper()
        if opp_type == "JOB":
            res = await session.execute(delete(SavedJobRecord).where(SavedJobRecord.user_id == user_id, SavedJobRecord.opportunity_id == opportunity_id))
            await session.commit()
            return res.rowcount > 0
        elif opp_type == "FREELANCE":
            res = await session.execute(delete(SavedFreelanceOpportunityRecord).where(SavedFreelanceOpportunityRecord.user_id == user_id, SavedFreelanceOpportunityRecord.opportunity_id == opportunity_id))
            await session.commit()
            return res.rowcount > 0
        elif opp_type in ("STARTUP_PAIN_POINT", "STARTUP"):
            res = await session.execute(delete(SavedStartupOpportunityRecord).where(SavedStartupOpportunityRecord.user_id == user_id, SavedStartupOpportunityRecord.opportunity_id == opportunity_id))
            await session.commit()
            return res.rowcount > 0
        return False

    @staticmethod
    async def record_candidate_feedback(
        user_id: str,
        opportunity_type: str,
        opportunity_id: str,
        feedback_category: str,
        explanation: Optional[str],
        session: AsyncSession,
    ) -> CandidateOpportunityFeedbackRecord:
        """
        Records candidate relevance feedback without altering source evidence or universal verification.
        Preserves candidate isolation.
        """
        feedback = CandidateOpportunityFeedbackRecord(
            user_id=user_id,
            opportunity_type=opportunity_type.upper(),
            opportunity_id=opportunity_id,
            feedback_category=feedback_category.upper(),
            explanation=explanation,
        )
        session.add(feedback)
        await session.commit()
        return feedback
