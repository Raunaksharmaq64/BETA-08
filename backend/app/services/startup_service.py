"""
RIGHT FIT Core — Startup Intelligence Service
Version: 1.0.0
Phase: 10 — Startup Intelligence Integration

Manages canonical startup opportunities, evidence ledgers, technology findings,
corroborations, saved bookmarks, and candidate pitch drafts with explicit assumptions.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    CandidateSkillRecord,
    SavedStartupOpportunityRecord,
    StartupCorroborationRecord,
    StartupEvidenceRecord,
    StartupOpportunityRecord,
    StartupOpportunityWorkspaceRecord,
    StartupPitchDraftRecord,
    StartupTechFindingRecord,
    User,
    utc_now,
)

logger = logging.getLogger(__name__)


def classify_source_type(source_name: str) -> str:
    """Classifies source into governance taxonomy."""
    s = (source_name or "").lower()
    if "github" in s:
        return "OFFICIAL_API"
    if any(k in s for k in ["rss", "reddit", "product hunt", "hacker news", "dev.to", "google news"]):
        return "OFFICIAL_FEED"
    if "audit" in s or "pagespeed" in s:
        return "PERMITTED_PUBLIC_SOURCE"
    if any(k in s for k in ["duckduckgo", "yahoo", "indiehackers", "search"]):
        return "DISCOVERY_ONLY"
    return "PERMITTED_PUBLIC_SOURCE"


def extract_domain(url: Optional[str]) -> Optional[str]:
    """Extracts clean hostname domain from URL."""
    if not url:
        return None
    try:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc if netloc else None
    except Exception:
        return None


class StartupService:
    """Core domain service for Startup Intelligence and Candidate Opportunities."""

    @staticmethod
    async def import_startup_leads(
        leads: List[Dict[str, Any]],
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Idempotently ingests raw leads from Startup Intelligence into Core canonical models.
        Preserves evidence provenance, technology findings, and corroborations.
        """
        imported_count = 0
        updated_count = 0
        skipped_count = 0

        for item in leads:
            raw_id = item.get("id")
            service_record_id = str(raw_id) if raw_id is not None else None
            name = (item.get("startup_name") or "Unnamed Startup").strip()[:150]
            raw_url = (item.get("url") or "").strip()
            url = raw_url[:500] if raw_url else None
            domain = extract_domain(url)
            if domain:
                domain = domain[:150]
            category = (item.get("category") or "Development").strip()[:50]
            detected_signal = (item.get("detected_signal") or item.get("title") or "Technical Problem Detected").strip()
            insight = item.get("insight") or ""
            opportunity_text = item.get("opportunity") or ""
            pitch_idea = item.get("pitch_idea") or ""
            score = item.get("score")
            try:
                urgency_score = int(score) if score is not None else 5
            except (ValueError, TypeError):
                urgency_score = 5
            urgency_score = max(1, min(10, urgency_score))

            score_explanation = item.get("score_explanation")
            primary_source = item.get("source") or "Startup Intelligence Feed"
            source_type = classify_source_type(primary_source)

            # Deduplication: Match existing record by service_record_id or (domain/name + category)
            existing_record: Optional[StartupOpportunityRecord] = None
            if service_record_id:
                res = await session.execute(
                    select(StartupOpportunityRecord).where(
                        StartupOpportunityRecord.service_record_id == service_record_id
                    ).limit(1)
                )
                existing_record = res.scalars().first()

            if not existing_record and domain:
                res = await session.execute(
                    select(StartupOpportunityRecord).where(
                        StartupOpportunityRecord.domain == domain,
                        StartupOpportunityRecord.category == category,
                    ).limit(1)
                )
                existing_record = res.scalars().first()

            if not existing_record:
                res = await session.execute(
                    select(StartupOpportunityRecord).where(
                        StartupOpportunityRecord.startup_name == name,
                        StartupOpportunityRecord.detected_signal == detected_signal,
                    ).limit(1)
                )
                existing_record = res.scalars().first()

            # Parse timestamps
            created_at_raw = item.get("created_at")
            published_at = None
            if created_at_raw:
                try:
                    published_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
                    if published_at.tzinfo is None:
                        published_at = published_at.replace(tzinfo=timezone.utc)
                except Exception:
                    published_at = None

            now = utc_now()

            # Contact channels
            contact_info = item.get("contact_info") or {}
            c_email = (contact_info.get("email") or item.get("email") or item.get("contact_email") or "")[:255] or None
            c_tw = (contact_info.get("twitter") or item.get("twitter") or item.get("twitter_url") or "")[:500] or None
            c_li = (contact_info.get("linkedin") or item.get("linkedin") or item.get("linkedin_url") or "")[:500] or None
            c_gh = (contact_info.get("github") or item.get("github") or item.get("github_url") or "")[:500] or None
            c_cp = (contact_info.get("contact_page") or item.get("contact_page") or item.get("contact_page_url") or "")[:500] or None

            if existing_record:
                # Update status and timestamps
                existing_record.last_checked_at = now
                existing_record.urgency_score = max(existing_record.urgency_score, urgency_score)
                if insight and not existing_record.ai_insight:
                    existing_record.ai_insight = insight
                if opportunity_text and not existing_record.ai_opportunity:
                    existing_record.ai_opportunity = opportunity_text
                if pitch_idea and not existing_record.ai_pitch_idea:
                    existing_record.ai_pitch_idea = pitch_idea
                if item.get("problem_explanation") and not existing_record.problem_explanation:
                    existing_record.problem_explanation = item.get("problem_explanation")
                if item.get("how_to_solve_strategy") and not existing_record.how_to_solve_strategy:
                    existing_record.how_to_solve_strategy = item.get("how_to_solve_strategy")

                if c_email and not existing_record.contact_email:
                    existing_record.contact_email = c_email
                if c_tw and not existing_record.twitter_url:
                    existing_record.twitter_url = c_tw
                if c_li and not existing_record.linkedin_url:
                    existing_record.linkedin_url = c_li
                if c_gh and not existing_record.github_url:
                    existing_record.github_url = c_gh
                if c_cp and not existing_record.contact_page_url:
                    existing_record.contact_page_url = c_cp

                # Record corroborating evidence if observation source differs
                excerpt = item.get("raw_text") or detected_signal
                existing_ev_res = await session.execute(
                    select(StartupEvidenceRecord).where(
                        StartupEvidenceRecord.opportunity_id == existing_record.id,
                        StartupEvidenceRecord.publisher == primary_source,
                    ).limit(1)
                )
                existing_ev = existing_ev_res.scalars().first()
                if not existing_ev:
                    evidence = StartupEvidenceRecord(
                        opportunity_id=existing_record.id,
                        source_title=detected_signal,
                        source_url=url,
                        publisher=primary_source,
                        source_type=source_type,
                        observation_excerpt=excerpt[:2000],
                        collection_method="RSS_FEED" if "rss" in primary_source.lower() else "PUBLIC_SCRAPE",
                        source_limitations="Community forum post, unverified public claim" if "reddit" in primary_source.lower() else "Public feed observation",
                        published_at=published_at,
                        retrieved_at=now,
                        first_seen_at=now,
                        last_checked_at=now,
                        is_corroborating=True,
                    )
                    session.add(evidence)

                    corroboration = StartupCorroborationRecord(
                        opportunity_id=existing_record.id,
                        source_identifier=service_record_id or f"{name}-{primary_source}",
                        source_name=primary_source,
                        is_independent=True,
                        conflicts_with_primary=False,
                        notes=f"Corroborating signal from {primary_source}.",
                    )
                    session.add(corroboration)
                    existing_record.corroboration_count = (existing_record.corroboration_count or 1) + 1

                session.add(existing_record)
                updated_count += 1
                opp_id = existing_record.id
            else:
                # Create canonical opportunity
                opp = StartupOpportunityRecord(
                    service_record_id=service_record_id,
                    startup_name=name,
                    domain=domain,
                    website_url=url,
                    category=category,
                    detected_signal=detected_signal,
                    pain_point_description=insight or detected_signal,
                    urgency_score=urgency_score,
                    score_explanation=score_explanation,
                    primary_source=primary_source,
                    source_url=url if url and not domain else None,
                    status="DISCOVERED",
                    ai_insight=insight if insight else None,
                    ai_opportunity=opportunity_text if opportunity_text else None,
                    ai_pitch_idea=pitch_idea if pitch_idea else None,
                    ai_model="gemini-2.0-flash" if item.get("analyzed") else "template",
                    ai_generated_at=now if item.get("analyzed") else None,
                    problem_explanation=item.get("problem_explanation"),
                    how_to_solve_strategy=item.get("how_to_solve_strategy"),
                    contact_email=c_email,
                    twitter_url=c_tw,
                    linkedin_url=c_li,
                    github_url=c_gh,
                    contact_page_url=c_cp,
                    corroboration_count=1,
                    has_conflicting_evidence=False,
                    published_at=published_at,
                    retrieved_at=now,
                    first_seen_at=now,
                    last_checked_at=now,
                )
                session.add(opp)
                await session.flush()
                opp_id = opp.id
                imported_count += 1

                # Create Evidence Record
                excerpt = item.get("raw_text") or detected_signal
                evidence = StartupEvidenceRecord(
                    opportunity_id=opp_id,
                    source_title=detected_signal,
                    source_url=url,
                    publisher=primary_source,
                    source_type=source_type,
                    observation_excerpt=excerpt[:2000],
                    collection_method="RSS_FEED" if "rss" in primary_source.lower() else "PUBLIC_SCRAPE",
                    source_limitations="Community forum post, unverified public claim" if "reddit" in primary_source.lower() else "Public feed observation",
                    published_at=published_at,
                    retrieved_at=now,
                    first_seen_at=now,
                    last_checked_at=now,
                    is_corroborating=True,
                )
                session.add(evidence)
                await session.flush()

                # Create Corroboration Record
                corroboration = StartupCorroborationRecord(
                    opportunity_id=opp_id,
                    source_identifier=service_record_id or f"{name}-{primary_source}",
                    source_name=primary_source,
                    is_independent=True,
                    conflicts_with_primary=False,
                    notes="Initial discovery observation.",
                )
                session.add(corroboration)

                # Extract and store Technology Findings
                tech_findings_list: List[str] = []
                tech_audit = item.get("tech_audit")
                if isinstance(tech_audit, dict):
                    stack = tech_audit.get("tech_stack", [])
                    if isinstance(stack, list):
                        tech_findings_list.extend([str(t) for t in stack if t])

                matched_skills = item.get("matched_skills")
                if isinstance(matched_skills, list):
                    tech_findings_list.extend([str(s) for s in matched_skills if s])

                # Deduplicate technologies
                seen_techs = set()
                for tech in tech_findings_list:
                    clean_tech = tech.strip()
                    if clean_tech and clean_tech.lower() not in seen_techs:
                        seen_techs.add(clean_tech.lower())
                        tf = StartupTechFindingRecord(
                            opportunity_id=opp_id,
                            evidence_id=evidence.id,
                            technology_name=clean_tech,
                            category="Observed Stack",
                            finding_type="AUDIT_DETECTED" if tech_audit else "KEYWORD_MENTION",
                            confidence_score=0.95 if tech_audit else 0.75,
                            traceable_evidence=f"Observed in {primary_source} context for {name}",
                        )
                        session.add(tf)

        await session.commit()
        return {
            "imported_count": imported_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "total_processed": len(leads),
        }

    @staticmethod
    async def list_startup_opportunities(
        session: AsyncSession,
        category: Optional[str] = None,
        min_score: Optional[int] = None,
        source: Optional[str] = None,
        technology: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[StartupOpportunityRecord], int]:
        """Lists canonical startup opportunities with robust filtering and pagination."""
        query = select(StartupOpportunityRecord)

        if category and category != "All":
            query = query.where(StartupOpportunityRecord.category == category)
        if min_score is not None:
            query = query.where(StartupOpportunityRecord.urgency_score >= min_score)
        if source and source != "All":
            query = query.where(StartupOpportunityRecord.primary_source.ilike(f"%{source}%"))
        if search:
            search_clean = f"%{search.strip()}%"
            query = query.where(
                or_(
                    StartupOpportunityRecord.startup_name.ilike(search_clean),
                    StartupOpportunityRecord.detected_signal.ilike(search_clean),
                    StartupOpportunityRecord.pain_point_description.ilike(search_clean),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Sort: urgency_score DESC, first_seen_at DESC
        query = query.order_by(
            StartupOpportunityRecord.urgency_score.desc(),
            StartupOpportunityRecord.first_seen_at.desc(),
        )

        offset = max(0, (page - 1) * limit)
        query = query.offset(offset).limit(limit)

        res = await session.execute(query)
        items = list(res.scalars().all())
        return items, total

    @staticmethod
    async def get_startup_opportunity_detail(
        opportunity_id: str,
        session: AsyncSession,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves comprehensive details with separated observations, AI summary, tech stack, and corroborations."""
        stmt = (
            select(StartupOpportunityRecord)
            .options(
                selectinload(StartupOpportunityRecord.evidence_records),
                selectinload(StartupOpportunityRecord.tech_findings),
                selectinload(StartupOpportunityRecord.corroboration_records),
            )
            .where(StartupOpportunityRecord.id == opportunity_id)
        )
        res = await session.execute(stmt)
        opp = res.scalar_one_or_none()
        if not opp:
            return None

        # Format observations ledger
        evidence_list = [
            {
                "id": ev.id,
                "source_title": ev.source_title,
                "source_url": ev.source_url,
                "publisher": ev.publisher,
                "source_type": ev.source_type,
                "observation_excerpt": ev.observation_excerpt,
                "collection_method": ev.collection_method,
                "source_limitations": ev.source_limitations,
                "published_at": ev.published_at.isoformat() if ev.published_at else "Publication date unavailable",
                "retrieved_at": ev.retrieved_at.isoformat() if ev.retrieved_at else None,
                "is_corroborating": ev.is_corroborating,
            }
            for ev in opp.evidence_records
        ]

        # Format tech findings
        tech_list = [
            {
                "id": tf.id,
                "technology_name": tf.technology_name,
                "category": tf.category,
                "finding_type": tf.finding_type,
                "confidence_score": tf.confidence_score,
                "traceable_evidence": tf.traceable_evidence,
            }
            for tf in opp.tech_findings
        ]

        # Format corroboration
        corroborations_list = [
            {
                "id": cr.id,
                "source_identifier": cr.source_identifier,
                "source_name": cr.source_name,
                "is_independent": cr.is_independent,
                "conflicts_with_primary": cr.conflicts_with_primary,
                "notes": cr.notes,
            }
            for cr in opp.corroboration_records
        ]

        # Compute validation state
        if opp.has_conflicting_evidence:
            val_state = "CUSTOMER_VALIDATION_REQUIRED"
        elif opp.corroboration_count >= 3:
            val_state = "INDEPENDENTLY_CORROBORATED"
        elif opp.corroboration_count >= 2:
            val_state = "REPEATED_OBSERVATIONS"
        else:
            val_state = "OBSERVED_PROBLEM"

        return {
            "opportunity": {
                "id": opp.id,
                "service_record_id": opp.service_record_id,
                "startup_name": opp.startup_name,
                "domain": opp.domain,
                "website_url": opp.website_url,
                "category": opp.category,
                "detected_signal": opp.detected_signal,
                "pain_point_description": opp.pain_point_description,
                "urgency_score": opp.urgency_score,
                "score_explanation": opp.score_explanation,
                "primary_source": opp.primary_source,
                "source_url": opp.source_url,
                "status": opp.status,
                "published_at": opp.published_at.isoformat() if opp.published_at else "Publication date unavailable",
                "first_seen_at": opp.first_seen_at.isoformat() if opp.first_seen_at else None,
                "last_checked_at": opp.last_checked_at.isoformat() if opp.last_checked_at else None,
                "corroboration_count": opp.corroboration_count,
                "has_conflicting_evidence": opp.has_conflicting_evidence,
                "validation_state": val_state,
                "problem_explanation": opp.problem_explanation,
                "how_to_solve_strategy": opp.how_to_solve_strategy,
                "contact_email": opp.contact_email,
                "twitter_url": opp.twitter_url,
                "linkedin_url": opp.linkedin_url,
                "github_url": opp.github_url,
                "contact_page_url": opp.contact_page_url,
                "contact_info": {
                    "email": opp.contact_email,
                    "twitter": opp.twitter_url,
                    "linkedin": opp.linkedin_url,
                    "github": opp.github_url,
                    "contact_page": opp.contact_page_url,
                },
            },
            "ai_summary": {
                "is_ai_generated": True,
                "model": opp.ai_model or "template",
                "generated_at": opp.ai_generated_at.isoformat() if opp.ai_generated_at else None,
                "insight": opp.ai_insight,
                "opportunity": opp.ai_opportunity,
                "pitch_idea": opp.ai_pitch_idea,
                "problem_explanation": opp.problem_explanation,
                "how_to_solve_strategy": opp.how_to_solve_strategy,
                "disclaimer": "This summary is machine-generated based on public signals and does not represent an official statement or budget commitment from the target organization.",
            },
            "evidence_ledger": evidence_list,
            "technology_findings": tech_list,
            "corroboration_ledger": corroborations_list,
        }

    @staticmethod
    async def save_startup_opportunity(
        user_id: str,
        opportunity_id: str,
        notes: Optional[str],
        session: AsyncSession,
    ) -> SavedStartupOpportunityRecord:
        """Saves/bookmarks a startup opportunity for a candidate."""
        # Check if already saved
        stmt = select(SavedStartupOpportunityRecord).where(
            SavedStartupOpportunityRecord.user_id == user_id,
            SavedStartupOpportunityRecord.opportunity_id == opportunity_id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            if notes is not None:
                existing.notes = notes
                session.add(existing)
                await session.commit()
            return existing

        saved = SavedStartupOpportunityRecord(
            user_id=user_id,
            opportunity_id=opportunity_id,
            notes=notes,
        )
        session.add(saved)
        await session.commit()
        return saved

    @staticmethod
    async def unsave_startup_opportunity(
        user_id: str,
        opportunity_id: str,
        session: AsyncSession,
    ) -> bool:
        """Removes a saved bookmark."""
        stmt = delete(SavedStartupOpportunityRecord).where(
            SavedStartupOpportunityRecord.user_id == user_id,
            SavedStartupOpportunityRecord.opportunity_id == opportunity_id,
        )
        res = await session.execute(stmt)
        await session.commit()
        return res.rowcount > 0

    @staticmethod
    async def list_saved_startup_opportunities(
        user_id: str,
        session: AsyncSession,
    ) -> List[Dict[str, Any]]:
        """Lists all bookmarked startup opportunities for a candidate."""
        stmt = (
            select(SavedStartupOpportunityRecord)
            .options(selectinload(SavedStartupOpportunityRecord.opportunity))
            .where(SavedStartupOpportunityRecord.user_id == user_id)
            .order_by(SavedStartupOpportunityRecord.created_at.desc())
        )
        res = await session.execute(stmt)
        saved_items = res.scalars().all()

        results = []
        for s in saved_items:
            opp = s.opportunity
            results.append({
                "saved_id": s.id,
                "notes": s.notes,
                "saved_at": s.created_at.isoformat() if s.created_at else None,
                "opportunity": {
                    "id": opp.id,
                    "startup_name": opp.startup_name,
                    "domain": opp.domain,
                    "website_url": opp.website_url,
                    "category": opp.category,
                    "detected_signal": opp.detected_signal,
                    "urgency_score": opp.urgency_score,
                    "primary_source": opp.primary_source,
                }
            })
        return results

    @staticmethod
    async def generate_startup_pitch_draft(
        user_id: str,
        opportunity_id: str,
        tone: str,
        session: AsyncSession,
    ) -> StartupPitchDraftRecord:
        """
        Generates a candidate-facing pitch draft grounded in confirmed candidate skills.
        Explicitly includes mandatory assumptions checklist.
        STRICT COMPLIANCE: Draft only. No automatic sending.
        """
        # Fetch opportunity
        opp_stmt = select(StartupOpportunityRecord).where(StartupOpportunityRecord.id == opportunity_id)
        opp_res = await session.execute(opp_stmt)
        opp = opp_res.scalar_one_or_none()
        if not opp:
            raise ValueError(f"Startup opportunity {opportunity_id} not found")

        # Fetch candidate's confirmed skills
        skills_stmt = (
            select(CandidateSkillRecord.skill_name)
            .join(User, User.id == user_id)
            .where(CandidateSkillRecord.profile_id == User.id) # through profile
        )
        # Or directly query candidate's skills via profile
        prof_res = await session.execute(
            select(CandidateSkillRecord.skill_name)
            .join(CandidateSkillRecord.profile)
            .where(CandidateSkillRecord.profile.has(user_id=user_id))
        )
        skills = [r[0] for r in prof_res.fetchall()]
        grounded_skills = skills[:4] if skills else ["Full Stack Engineering", "Performance Optimization"]

        # Formulate explicit assumptions checklist
        explicit_assumptions = [
            "Assumption 1: The startup is currently experiencing the observed technical bottleneck.",
            "Assumption 2: The startup is actively seeking external help and open to engaging an external developer or consultant.",
            "Assumption 3: The proposed solution fits their current technical roadmap.",
            "Assumption 4: The company has allocated budget for technical improvements.",
            "Assumption 5: The suggested expertise aligns with their engineering stack priorities.",
        ]

        # Get candidate's name
        user_res = await session.execute(select(User.full_name).where(User.id == user_id))
        candidate_name = user_res.scalar_one_or_none() or "Engineering Specialist"

        # Construct grounded pitch based on tone
        skills_str = ", ".join(grounded_skills)
        problem = opp.detected_signal
        name = opp.startup_name

        if tone.lower() == "short":
            subject = f"Quick question regarding {opp.category} for {name}"
            body = (
                f"Hi {name} Team,\n\n"
                f"I noticed your recent update regarding: \"{problem}\".\n\n"
                f"I specialize in {skills_str} and help startups resolve bottlenecks like this efficiently. "
                f"Would you be open to a 10-minute introductory call next week to see if I can assist?\n\n"
                f"Best,\n{candidate_name}"
            )
        elif tone.lower() == "formal":
            subject = f"Technical Consultation Proposal for {name} ({opp.category})"
            body = (
                f"Dear {name} Engineering Team,\n\n"
                f"I hope this message finds you well. I recently came across your public technical discussion regarding \"{problem}\".\n\n"
                f"With demonstrated background in {skills_str}, I work with early-stage and scaling platforms to diagnose and resolve {opp.category} challenges.\n\n"
                f"I have compiled a brief assessment of potential approaches. Would you be receptive to scheduling a 15-minute briefing next week to review these observations?\n\n"
                f"Sincerely,\n{candidate_name}"
            )
        else: # casual
            subject = f"Idea for {name}'s {opp.category} workflow"
            body = (
                f"Hi {name} Team! 👋\n\n"
                f"Saw your post about \"{problem}\" and thought I'd reach out. "
                f"I work with startups on {skills_str}, specifically optimizing {opp.category.lower()} pipelines and developer workflows.\n\n"
                f"Happy to share some quick thoughts on how other teams tackled this. Let me know if you'd like to connect for a quick 10-minute chat!\n\n"
                f"Cheers,\n{candidate_name}"
            )

        draft = StartupPitchDraftRecord(
            opportunity_id=opportunity_id,
            candidate_id=user_id,
            subject=subject,
            body=body,
            tone=tone.lower(),
            candidate_grounded_skills=json.dumps(grounded_skills),
            explicit_assumptions=json.dumps(explicit_assumptions),
            is_archived=False,
            candidate_edits_count=0,
        )
        session.add(draft)
        await session.commit()
        return draft

    @staticmethod
    async def update_startup_pitch_draft(
        draft_id: str,
        user_id: str,
        subject: Optional[str],
        body: Optional[str],
        tone: Optional[str],
        session: AsyncSession,
    ) -> StartupPitchDraftRecord:
        """Updates pitch draft content while tracking candidate edits."""
        stmt = select(StartupPitchDraftRecord).where(
            StartupPitchDraftRecord.id == draft_id,
            StartupPitchDraftRecord.candidate_id == user_id,
        )
        res = await session.execute(stmt)
        draft = res.scalar_one_or_none()
        if not draft:
            raise ValueError(f"Draft {draft_id} not found or unauthorized")

        if subject is not None:
            draft.subject = subject.strip()
        if body is not None:
            draft.body = body.strip()
        if tone is not None:
            draft.tone = tone.strip().lower()

        draft.candidate_edits_count += 1
        draft.updated_at = utc_now()
        session.add(draft)
        await session.commit()
        return draft

    @staticmethod
    async def get_or_create_workspace(
        opportunity_id: str,
        user_id: str,
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """Retrieves or creates candidate's opportunity workspace canvas."""
        # Verify opportunity exists
        opp_stmt = select(StartupOpportunityRecord).where(StartupOpportunityRecord.id == opportunity_id)
        opp_res = await session.execute(opp_stmt)
        opp = opp_res.scalar_one_or_none()
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        stmt = select(StartupOpportunityWorkspaceRecord).where(
            StartupOpportunityWorkspaceRecord.opportunity_id == opportunity_id,
            StartupOpportunityWorkspaceRecord.user_id == user_id,
        )
        res = await session.execute(stmt)
        workspace = res.scalar_one_or_none()

        # Compute validation state
        if opp.has_conflicting_evidence:
            val_state = "CUSTOMER_VALIDATION_REQUIRED"
        elif opp.corroboration_count >= 3:
            val_state = "INDEPENDENTLY_CORROBORATED"
        elif opp.corroboration_count >= 2:
            val_state = "REPEATED_OBSERVATIONS"
        else:
            val_state = "OBSERVED_PROBLEM"

        if not workspace:
            default_checklist = [
                {"id": "c1", "label": "Review raw community signals and verified context", "completed": True},
                {"id": "c2", "label": "Formulate core problem statement & target user persona", "completed": False},
                {"id": "c3", "label": "Benchmark existing competitor solutions & workarounds", "completed": False},
                {"id": "c4", "label": "Draft customer discovery interview script", "completed": False},
                {"id": "c5", "label": "Design technical solution architecture / MVP blueprint", "completed": False},
            ]
            default_hypotheses = [
                f"The target team experiences operational overhead due to {opp.detected_signal[:80]}",
                "Existing commercial alternatives fail due to high cost or complex onboarding",
            ]
            default_questions = [
                "What is your current workflow or workaround for this problem?",
                "How many engineering hours per week are lost to this bottleneck?",
                "What criteria would make an external solution an immediate purchase decision?",
            ]
            workspace = StartupOpportunityWorkspaceRecord(
                opportunity_id=opportunity_id,
                user_id=user_id,
                target_persona=f"CTO / Engineering Lead at {opp.startup_name}",
                hypotheses_json=default_hypotheses,
                competitor_notes="Evaluating in-house scripts vs managed vendor tools",
                interview_questions_json=default_questions,
                validation_checklist_json=default_checklist,
                solution_architecture=opp.how_to_solve_strategy or "Lightweight serverless microservice or SDK integration.",
                candidate_notes=opp.ai_insight or "Initiated opportunity workspace.",
            )
            session.add(workspace)
            await session.commit()
            await session.refresh(workspace)

        return {
            "id": workspace.id,
            "opportunity_id": workspace.opportunity_id,
            "user_id": workspace.user_id,
            "startup_name": opp.startup_name,
            "detected_signal": opp.detected_signal,
            "pain_point_description": opp.pain_point_description,
            "urgency_score": opp.urgency_score,
            "validation_state": val_state,
            "target_persona": workspace.target_persona,
            "hypotheses": workspace.hypotheses_json or [],
            "competitor_notes": workspace.competitor_notes,
            "interview_questions": workspace.interview_questions_json or [],
            "validation_checklist": workspace.validation_checklist_json or [],
            "solution_architecture": workspace.solution_architecture,
            "candidate_notes": workspace.candidate_notes,
            "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
        }

    @staticmethod
    async def update_workspace(
        opportunity_id: str,
        user_id: str,
        update_data: Dict[str, Any],
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """Updates candidate's opportunity workspace canvas."""
        stmt = select(StartupOpportunityWorkspaceRecord).where(
            StartupOpportunityWorkspaceRecord.opportunity_id == opportunity_id,
            StartupOpportunityWorkspaceRecord.user_id == user_id,
        )
        res = await session.execute(stmt)
        workspace = res.scalar_one_or_none()
        if not workspace:
            raise ValueError("Workspace not initialized for this opportunity")

        if "target_persona" in update_data:
            workspace.target_persona = update_data["target_persona"]
        if "hypotheses" in update_data:
            workspace.hypotheses_json = update_data["hypotheses"]
        if "competitor_notes" in update_data:
            workspace.competitor_notes = update_data["competitor_notes"]
        if "interview_questions" in update_data:
            workspace.interview_questions_json = update_data["interview_questions"]
        if "validation_checklist" in update_data:
            workspace.validation_checklist_json = update_data["validation_checklist"]
        if "solution_architecture" in update_data:
            workspace.solution_architecture = update_data["solution_architecture"]
        if "candidate_notes" in update_data:
            workspace.candidate_notes = update_data["candidate_notes"]

        workspace.updated_at = utc_now()
        session.add(workspace)
        await session.commit()
        await session.refresh(workspace)

        return await StartupService.get_or_create_workspace(opportunity_id, user_id, session)


    @staticmethod
    def _generate_heuristic_blueprint(opp: StartupOpportunityRecord, developer_skills: str) -> Dict[str, Any]:
        """Generates comprehensive domain-grounded engineering problem and solution blueprints."""
        name = opp.startup_name or "Target Startup"
        cat = (opp.category or "Development").upper()
        sig = opp.detected_signal or "Architectural Bottleneck"
        skills = developer_skills or "Python, React, TypeScript, FastAPI, PostgreSQL, Docker, Redis"

        if "AI" in cat:
            prob = (
                f"{name} is experiencing heavy performance overhead in its AI inference / embedding pipelines. "
                f"Specifically: {sig}. As query throughput scales, high token latency, unoptimized context chunking, "
                f"and excessive vector retrieval costs cause GPU memory throttling and worker queue exhaustion. "
                "This leads to request timeouts and degraded developer satisfaction."
            )
            sol = (
                f"Step-by-Step AI Engineering Roadmap using [{skills}]:\n"
                "1. Pipeline Profiling: Benchmark embedding latency and token consumption using OpenTelemetry.\n"
                "2. Streaming Vector Cache: Deploy Redis with semantic vector caching to eliminate redundant LLM calls.\n"
                "3. Asynchronous Worker Pool: Offload long-running embedding jobs to an isolated Celery/Redis worker cluster.\n"
                "4. Local Quantization: Evaluate lightweight local models (FastEmbed / ONNX) for real-time preprocessing.\n"
                "5. Verification: Deploy end-to-end regression benchmarks verifying p95 latency drops below 250ms."
            )
        elif "PERF" in cat:
            prob = (
                f"{name} suffers from client-side render lag and server latency bottlenecks. "
                f"Specifically: {sig}. Excessive bundle sizes, blocking third-party scripts, and lack of edge-level caching "
                "degrade Core Web Vitals (LCP > 3.8s, INP > 200ms), resulting in lower conversion rates and search ranking penalties."
            )
            sol = (
                f"Step-by-Step Performance Remediation Plan using [{skills}]:\n"
                "1. Bundle & Asset Audit: Run Webpack/Next bundle analyzer to isolate tree-shaking failures and oversized chunks.\n"
                "2. SSR & Edge Caching: Migrate dynamic routes to Incremental Static Regeneration (ISR) with Cloudflare CDN edge caching.\n"
                "3. Database Indexing & Query Tuning: Audit database slow queries, add missing composite indexes, and configure PgBouncer pooling.\n"
                "4. Core Web Vitals Verification: Measure real-user metrics (RUM) ensuring LCP < 1.8s and sub-100ms API response times."
            )
        elif "UI" in cat or "UX" in cat:
            prob = (
                f"{name} is confronting customer friction and signup abandonment. "
                f"Specifically: {sig}. Complex user flows, lack of responsive mobile design, and unintuitive UX patterns "
                "create significant drop-off during user onboarding and workspace setup."
            )
            sol = (
                f"Step-by-Step UI/UX Modernization Roadmap using [{skills}]:\n"
                "1. Funnel Telemetry: Instrument PostHog/Mixpanel to pinpoint the exact step where users abandon the workflow.\n"
                "2. Component Refactoring: Rebuild interactive views using Tailwind CSS and Radix UI primitives for accessible, responsive layouts.\n"
                "3. Form State Machine: Replace fragile multi-step forms with a deterministic state machine (XState / React Hook Form).\n"
                "4. User Testing: Conduct interactive A/B testing on staging to validate a 20%+ increase in onboarding completion."
            )
        else:
            prob = (
                f"{name} is facing operational bottlenecks and technical debt in its core services. "
                f"Specifically: {sig}. Monolithic couplings and insufficient test automation slow down release frequency "
                "and introduce regression risks into production deployments."
            )
            sol = (
                f"Step-by-Step Engineering Execution Guide using [{skills}]:\n"
                "1. Architecture Decoupling: Break tightly coupled logic into modular service boundaries with typed interfaces.\n"
                "2. Asynchronous Queueing: Isolate background workloads using FastAPI and background task queues.\n"
                "3. CI/CD Hardening: Implement GitHub Actions pipelines with automated unit tests and Docker image builds.\n"
                "4. Observability: Configure Prometheus metrics and structured logging for full system visibility."
            )

        return {
            "problem_explanation": prob,
            "how_to_solve_strategy": sol,
            "ai_insight": f"Observed bottleneck for {name}: {sig}. Strategic developer opportunity to resolve with {skills}.",
            "ai_opportunity": f"Technical optimization and engineering architecture consulting for {name}.",
            "ai_pitch_idea": (
                f"Hi {name} Team,\n\nI noticed you are currently dealing with {sig}. "
                f"I specialize in {cat.title()} architecture and have resolved similar bottlenecks using {skills}. "
                "I've mapped out a 3-step action plan to solve this. Happy to share a quick technical overview if helpful!\n\nBest,\n[Your Name]"
            )
        }

    @staticmethod
    async def analyze_startup_with_gemini(
        opportunity_id: str,
        developer_skills: Optional[str],
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Executes on-demand Gemini AI analysis for a startup pain point.
        Derives problem root-cause diagnosis, operational impact, and step-by-step
        developer implementation strategy tailored to the candidate's skills.
        """
        import os
        from app.core.config import settings
        from app.modules.startup_intelligence import ai_agent

        stmt = (
            select(StartupOpportunityRecord)
            .options(selectinload(StartupOpportunityRecord.tech_findings))
            .where(StartupOpportunityRecord.id == opportunity_id)
        )
        res = await session.execute(stmt)
        opp = res.scalar_one_or_none()
        if not opp:
            raise ValueError(f"Startup opportunity {opportunity_id} not found")

        api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
        skills_str = developer_skills or "Python, React, TypeScript, Next.js, FastAPI, PostgreSQL, Docker, Redis"

        lead_payload = {
            "startup_name": opp.startup_name,
            "detected_signal": opp.detected_signal,
            "insight": opp.ai_insight or opp.pain_point_description or "",
            "opportunity": opp.ai_opportunity or "",
            "category": opp.category,
            "tech_audit": {
                "tech_stack": [tf.technology_name for tf in opp.tech_findings] if opp.tech_findings else [],
                "domain": opp.domain,
                "category": opp.category,
            }
        }

        problem_expl = ""
        how_to_solve = ""
        ai_insight = opp.ai_insight or ""
        ai_opp = opp.ai_opportunity or ""
        ai_pitch = opp.ai_pitch_idea or ""
        used_model = "gemini-2.5-flash-lite"

        # Try Gemini AI Agent
        if api_key:
            try:
                guide = await ai_agent.generate_explanation_and_solution(
                    lead_data=lead_payload,
                    api_key=api_key,
                    developer_skills=skills_str,
                    model_name="gemini-2.5-flash-lite"
                )
                if isinstance(guide, dict):
                    problem_expl = guide.get("problem_explanation", "")
                    how_to_solve = guide.get("how_to_solve_strategy", "")
            except Exception as e:
                logger.warning(f"Gemini API call failed in analyze_startup_with_gemini: {e}")

        # Fallback to intelligent technical blueprint if Gemini API is unavailable or quota exhausted
        if not problem_expl or not how_to_solve:
            fallback = StartupService._generate_heuristic_blueprint(opp, skills_str)
            if not problem_expl:
                problem_expl = fallback["problem_explanation"]
            if not how_to_solve:
                how_to_solve = fallback["how_to_solve_strategy"]
            if not ai_insight:
                ai_insight = fallback["ai_insight"]
            if not ai_opp:
                ai_opp = fallback["ai_opportunity"]
            if not ai_pitch:
                ai_pitch = fallback["ai_pitch_idea"]
            used_model = "gemini-heuristic-engine"

        now = utc_now()
        opp.problem_explanation = problem_expl
        opp.how_to_solve_strategy = how_to_solve
        if ai_insight:
            opp.ai_insight = ai_insight
        if ai_opp:
            opp.ai_opportunity = ai_opp
        if ai_pitch:
            opp.ai_pitch_idea = ai_pitch
        opp.ai_model = used_model
        opp.ai_generated_at = now
        opp.last_checked_at = now

        session.add(opp)
        await session.commit()
        await session.refresh(opp)

        return {
            "opportunity_id": opp.id,
            "startup_name": opp.startup_name,
            "domain": opp.domain,
            "category": opp.category,
            "detected_signal": opp.detected_signal,
            "problem_explanation": opp.problem_explanation,
            "how_to_solve_strategy": opp.how_to_solve_strategy,
            "ai_insight": opp.ai_insight,
            "ai_opportunity": opp.ai_opportunity,
            "ai_pitch_idea": opp.ai_pitch_idea,
            "ai_model": opp.ai_model,
            "ai_generated_at": opp.ai_generated_at.isoformat() if opp.ai_generated_at else None,
            "contact_email": opp.contact_email,
            "twitter_url": opp.twitter_url,
            "linkedin_url": opp.linkedin_url,
            "github_url": opp.github_url,
            "contact_page_url": opp.contact_page_url,
            "contact_info": {
                "email": opp.contact_email,
                "twitter": opp.twitter_url,
                "linkedin": opp.linkedin_url,
                "github": opp.github_url,
                "contact_page": opp.contact_page_url,
            }
        }
