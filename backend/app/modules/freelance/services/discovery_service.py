"""
Freelance Discovery Service — Coordinates Google Maps business search, cleaning, evidence logging, and canonical opportunity ingestion.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import ContactEvidenceRecord, FreelanceOpportunityRecord, utc_now
from app.modules.freelance.collectors.apify_collector import ApifyCollector
from app.modules.freelance.collectors.base_collector import BaseCollector, DiscoveredLead
from app.modules.freelance.collectors.serpapi_collector import SerpApiCollector
from app.modules.freelance.repositories.freelance_repository import FreelanceRepository
from app.modules.freelance.utils.data_cleaner import DataCleaner

logger = logging.getLogger(__name__)


class FreelanceDiscoveryService:
    """Orchestrates lead search, deduplication, and persistence into Core."""

    @classmethod
    async def resolve_collector_and_key(
        cls, session: AsyncSession, user_id: Optional[str] = None
    ) -> tuple[BaseCollector, str]:
        user_settings = None
        if user_id:
            repo = FreelanceRepository(session)
            user_settings = await repo.get_candidate_settings(user_id)

        maps_provider = "serpapi"
        serpapi_key = os.getenv("SERPAPI_KEY", "")
        apify_token = os.getenv("APIFY_API_TOKEN", "")

        if user_settings:
            maps_provider = user_settings.maps_provider or "serpapi"
            if user_settings.encrypted_serpapi_key:
                serpapi_key = user_settings.encrypted_serpapi_key
            if user_settings.encrypted_apify_token:
                apify_token = user_settings.encrypted_apify_token

        if maps_provider == "apify" and apify_token:
            return ApifyCollector(default_token=apify_token), apify_token

        return SerpApiCollector(default_api_key=serpapi_key), serpapi_key

    @classmethod
    def synthesize_opportunity_fields(cls, lead: DiscoveredLead) -> Dict[str, Any]:
        """Maps a DiscoveredLead into canonical FreelanceOpportunity fields."""
        business_name = lead.name or "Local Business"
        city = lead.city or "Remote"
        category = lead.category or "Small Business"
        website = lead.website or ""
        is_broken = lead.is_broken_website
        rating = lead.rating
        reviews = lead.reviews
        phone = lead.phone
        email = lead.email

        skills: List[str] = []
        if not website:
            classification_state = "VERIFIED_OPPORTUNITY"
            classification_reason = "Business currently lacks a website on Google Maps."
            suggested_service = "Custom Modern Website & SEO Setup"
            opportunity_title = f"New Modern Website & Digital Presence — {business_name}"
            skills = ["Web Development", "Responsive Design", "Domain & Hosting Setup", "Local SEO"]
        elif is_broken:
            classification_state = "VERIFIED_OPPORTUNITY"
            classification_reason = "Business website failed health checks (DNS/HTTP/SSL error)."
            suggested_service = "Website Technical Repair & Modern Redesign"
            opportunity_title = f"Website Restoration & Redesign — {business_name}"
            skills = ["Web Development", "SSL Configuration", "Performance Optimization", "Mobile Responsive"]
        elif rating > 0 and rating < 4.0:
            classification_state = "POTENTIAL_FREELANCE_OPPORTUNITY"
            classification_reason = f"Rating is {rating}/5 with {reviews} reviews; opportunity for review funnel automation."
            suggested_service = "Reputation Management & Review Funnel"
            opportunity_title = f"Customer Review Automation & Local SEO — {business_name}"
            skills = ["Local SEO", "Reputation Management", "Customer Engagement"]
        else:
            classification_state = "DISCOVERED_LEAD"
            classification_reason = "Standard business listing discovered via search scan."
            suggested_service = "Digital Optimization & Marketing Audit"
            opportunity_title = f"Digital Growth & Web Presence for {business_name}"
            skills = ["Digital Strategy", "Website Audit", "Technical Consulting"]

        priority = lead.priority or DataCleaner.assign_priority(lead)

        return {
            "business_name": business_name,
            "opportunity_title": opportunity_title,
            "service_category": category,
            "description": f"Freelance opportunity for {business_name} in {city}. {classification_reason}",
            "city": city,
            "location": f"{city}, IN" if "India" in city else city,
            "is_remote": True,
            "website": website or None,
            "is_broken_website": is_broken,
            "rating": rating,
            "reviews_count": reviews,
            "phone": phone or None,
            "email": email or None,
            "required_skills": skills,
            "suggested_service": suggested_service,
            "suggested_pitch": lead.custom_pitch or None,
            "classification_state": classification_state,
            "classification_reason": classification_reason,
            "priority": priority,
            "relevance_score": 95.0 if priority == "HIGH" else (85.0 if priority == "MEDIUM" else 75.0),
            "source": lead.source or "google_maps",
            "original_source_url": f"https://www.google.com/maps/search/?api=1&query={business_name}+{city}",
            "discovered_at": utc_now(),
            "last_verified_at": utc_now(),
        }

    @classmethod
    async def import_discovered_lead(
        cls, session: AsyncSession, lead: DiscoveredLead
    ) -> FreelanceOpportunityRecord:
        """Idempotently imports or updates a lead as a canonical Core opportunity."""
        repo = FreelanceRepository(session)
        mapped = cls.synthesize_opportunity_fields(lead)

        existing = await repo.find_existing_opportunity(
            place_id=lead.place_id,
            business_name=lead.name,
            city=lead.city,
        )

        if existing:
            existing.last_verified_at = utc_now()
            existing.is_broken_website = mapped["is_broken_website"]
            existing.rating = mapped["rating"]
            existing.reviews_count = mapped["reviews_count"]
            existing.priority = mapped["priority"]
            if mapped["email"] and not existing.email:
                existing.email = mapped["email"]
            if mapped["phone"] and not existing.phone:
                existing.phone = mapped["phone"]
            opp = existing
        else:
            opp = FreelanceOpportunityRecord(
                place_id=lead.place_id or None,
                business_name=mapped["business_name"],
                opportunity_title=mapped["opportunity_title"],
                service_category=mapped["service_category"],
                description=mapped["description"],
                city=mapped["city"],
                location=mapped["location"],
                is_remote=mapped["is_remote"],
                website=mapped["website"],
                is_broken_website=mapped["is_broken_website"],
                rating=mapped["rating"],
                reviews_count=mapped["reviews_count"],
                phone=mapped["phone"],
                email=mapped["email"],
                required_skills=mapped["required_skills"],
                suggested_service=mapped["suggested_service"],
                suggested_pitch=mapped["suggested_pitch"],
                classification_state=mapped["classification_state"],
                classification_reason=mapped["classification_reason"],
                priority=mapped["priority"],
                relevance_score=mapped["relevance_score"],
                source=mapped["source"],
                original_source_url=mapped["original_source_url"],
                discovered_at=mapped["discovered_at"],
                last_verified_at=mapped["last_verified_at"],
            )
            session.add(opp)
            await session.flush()

        # Add Contact Evidence records for phone, email, website
        if mapped["phone"]:
            session.add(
                ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type="PHONE",
                    contact_value=mapped["phone"],
                    source="google_maps",
                    source_evidence_url=mapped["original_source_url"],
                    evidence_status="VERIFIED",
                    discovered_at=utc_now(),
                )
            )
        if mapped["email"]:
            session.add(
                ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type="EMAIL",
                    contact_value=mapped["email"],
                    source="google_maps",
                    source_evidence_url=mapped["original_source_url"],
                    evidence_status="OBSERVED",
                    discovered_at=utc_now(),
                )
            )
        if mapped["website"]:
            session.add(
                ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type="WEBSITE",
                    contact_value=mapped["website"],
                    source="google_maps",
                    source_evidence_url=mapped["original_source_url"],
                    evidence_status="UNVERIFIED" if mapped["is_broken_website"] else "VERIFIED",
                    verification_method="HTTP_HEALTH_CHECK",
                    verification_notes="Failed health check" if mapped["is_broken_website"] else "Active",
                    discovered_at=utc_now(),
                )
            )

        await session.flush()
        return opp

    @classmethod
    async def discover_leads(
        cls,
        session: AsyncSession,
        user_id: str,
        query: str,
        city: str,
        max_results: int = 20,
        include_with_website: bool = False,
        deep_scan: bool = False,
        zones: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Executes full discovery pipeline: provider fetch -> clean & audit -> ingest to Core DB."""
        collector, api_key = await cls.resolve_collector_and_key(session, user_id)

        raw_leads: List[DiscoveredLead] = []
        try:
            if deep_scan and zones:
                leads_per_zone = max(10, max_results // len(zones))
                for zone in zones:
                    z = zone.strip()
                    if not z:
                        continue
                    zone_leads = collector.search(query, f"{z}, {city}", leads_per_zone, api_key=api_key)
                    raw_leads.extend(zone_leads)
            else:
                raw_leads = collector.search(query, city, max_results, api_key=api_key)
        except Exception as exc:
            logger.error(f"[FreelanceDiscoveryService] Collector search failed: {exc}", exc_info=True)
            raise RuntimeError(f"Search provider ({collector.platform_name}) error: {exc}") from exc

        # Clean and categorize leads
        cleaned_leads = DataCleaner.clean_leads(raw_leads)
        filtered_leads = DataCleaner.filter_leads(cleaned_leads, include_with_website)[:max_results]

        # Ingest into Core database
        imported_opportunities: List[FreelanceOpportunityRecord] = []
        for lead in filtered_leads:
            opp = await cls.import_discovered_lead(session, lead)
            imported_opportunities.append(opp)

        # Save search history log if a valid user is present
        if user_id:
            try:
                repo = FreelanceRepository(session)
                await repo.save_search_history(
                    user_id=user_id,
                    query=query,
                    city=city,
                    results_count=len(cleaned_leads),
                    leads_count=len(imported_opportunities),
                    deep_scan=deep_scan,
                    zones=zones,
                    include_with_website=include_with_website,
                )
            except Exception as history_err:
                logger.warning(f"[FreelanceDiscoveryService] Note: search history not saved: {history_err}")

        stats = {
            "total_found": len(cleaned_leads),
            "leads_imported": len(imported_opportunities),
            "high_priority": sum(1 for l in filtered_leads if l.priority == "HIGH"),
            "medium_priority": sum(1 for l in filtered_leads if l.priority == "MEDIUM"),
            "low_priority": sum(1 for l in filtered_leads if l.priority == "LOW"),
            "broken_websites": sum(1 for l in filtered_leads if l.is_broken_website),
            "without_website": sum(1 for l in filtered_leads if not l.website),
            "with_phone": sum(1 for l in filtered_leads if l.phone),
        }

        return {
            "success": True,
            "query": f"{query} in {city}",
            "stats": stats,
            "opportunities": [
                {
                    "id": o.id,
                    "business_name": o.business_name,
                    "opportunity_title": o.opportunity_title,
                    "service_category": o.service_category,
                    "city": o.city,
                    "website": o.website,
                    "is_broken_website": o.is_broken_website,
                    "rating": o.rating,
                    "reviews_count": o.reviews_count,
                    "phone": o.phone,
                    "email": o.email,
                    "priority": o.priority,
                    "classification_state": o.classification_state,
                    "relevance_score": o.relevance_score,
                }
                for o in imported_opportunities
            ],
        }
