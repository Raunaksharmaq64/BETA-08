"""
Freelance Audit Service — Coordinates website technical audits, email discovery, and contact evidence creation.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ContactEvidenceRecord, FreelanceOpportunityRecord, utc_now
from app.modules.freelance.repositories.freelance_repository import FreelanceRepository
from app.modules.freelance.utils.email_scraper import EmailScraper
from app.modules.freelance.utils.website_auditor import audit_website

logger = logging.getLogger(__name__)


class FreelanceAuditService:
    """Orchestrates technical auditing and email enrichment for freelance leads."""

    @staticmethod
    async def audit_opportunity(
        session: AsyncSession, opportunity_id: str
    ) -> Dict[str, Any]:
        repo = FreelanceRepository(session)
        opp = await repo.get_opportunity_by_id(opportunity_id)
        if not opp:
            raise ValueError(f"Freelance opportunity not found: {opportunity_id}")

        if not opp.website:
            return {
                "success": False,
                "message": "Opportunity has no website listed.",
                "audit": {
                    "overall_score": 0,
                    "status": "NO_WEBSITE",
                    "scores": {"speed": 0, "seo": 0, "mobile": 0, "ssl": 0, "alt": 0},
                    "recommendations": [
                        {
                            "category": "Digital Presence",
                            "title": "No Website Listed",
                            "description": "Business currently has no website on Google Maps.",
                            "severity": "HIGH",
                        }
                    ],
                },
            }

        # 1. Run technical audit
        audit_result = audit_website(opp.website)

        # 2. Update opportunity metadata
        opp.is_broken_website = (audit_result.get("status") == "BROKEN")
        opp.last_verified_at = utc_now()
        opp.description = f"{opp.description.split('Website Audit Score')[0].strip()} — Website Audit Score: {audit_result.get('overall_score')}/100"

        # 3. Deep Contact & Socials Enrichment
        socials_discovered: Dict[str, str] = {}
        try:
            enrichment = EmailScraper.deep_enrich_contacts(opp.website)
            discovered_email = enrichment.get("email")
            if discovered_email and not opp.email:
                opp.email = discovered_email
                evidence = ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type="EMAIL",
                    contact_value=discovered_email,
                    source="website_scraper",
                    source_evidence_url=opp.website,
                    evidence_status="VERIFIED",
                    verification_method="HTTP_WEBSITE_SCRAPE",
                    verification_notes="Discovered during technical website audit.",
                    discovered_at=utc_now(),
                    verified_at=utc_now(),
                )
                session.add(evidence)

            # Discover and link social profiles
            socials = enrichment.get("socials", {})
            for platform, url in socials.items():
                if url:
                    current_val = getattr(opp, platform, None)
                    if not current_val:
                        setattr(opp, platform, url)
                        socials_discovered[platform] = url
                        evidence = ContactEvidenceRecord(
                            opportunity_id=opp.id,
                            contact_type=platform.upper(),
                            contact_value=url,
                            source="website_social_scraper",
                            source_evidence_url=opp.website,
                            evidence_status="VERIFIED",
                            verification_method="HTML_LINK_EXTRACT",
                            verification_notes=f"Discovered official {platform.capitalize()} profile.",
                            discovered_at=utc_now(),
                            verified_at=utc_now(),
                        )
                        session.add(evidence)
        except Exception as e:
            logger.debug(f"[AuditService] Contact enrichment error: {e}")

        await session.flush()
        return {
            "success": True,
            "opportunity_id": opp.id,
            "website": opp.website,
            "audit": audit_result,
            "email_discovered": opp.email,
            "socials_discovered": socials_discovered,
        }

    @staticmethod
    async def enrich_contacts(
        session: AsyncSession,
        opportunity_id: str,
        custom_website: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dedicated fast contact & social profiles enrichment without full technical audit overhead."""
        repo = FreelanceRepository(session)
        opp = await repo.get_opportunity_by_id(opportunity_id)
        if not opp:
            raise ValueError(f"Freelance opportunity not found: {opportunity_id}")

        if custom_website:
            clean_url = custom_website.strip()
            if not clean_url.startswith(("http://", "https://")):
                clean_url = "https://" + clean_url
            opp.website = clean_url
            opp.is_broken_website = False
            session.add(
                ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type="WEBSITE",
                    contact_value=clean_url,
                    source="user_submission",
                    source_evidence_url=clean_url,
                    evidence_status="VERIFIED",
                    verification_method="DIRECT_INPUT",
                    verification_notes="Website provided for outreach contact enrichment.",
                    discovered_at=utc_now(),
                    verified_at=utc_now(),
                )
            )

        if not opp.website:
            return {
                "success": False,
                "message": "Opportunity has no website listed to crawl. Provide a website URL to enrich contacts.",
                "email": opp.email,
                "socials": {
                    "instagram": opp.instagram,
                    "facebook": opp.facebook,
                    "linkedin": opp.linkedin,
                    "twitter": opp.twitter,
                },
            }

        enrichment = EmailScraper.deep_enrich_contacts(opp.website)
        discovered_email = enrichment.get("email")
        if discovered_email:
            opp.email = discovered_email
            session.add(
                ContactEvidenceRecord(
                    opportunity_id=opp.id,
                    contact_type="EMAIL",
                    contact_value=discovered_email,
                    source="website_scraper",
                    source_evidence_url=opp.website,
                    evidence_status="VERIFIED",
                    verification_method="HTTP_WEBSITE_SCRAPE",
                    verification_notes="Discovered during fast contact enrichment.",
                    discovered_at=utc_now(),
                    verified_at=utc_now(),
                )
            )

        socials = enrichment.get("socials", {})
        socials_added: Dict[str, str] = {}
        for platform, url in socials.items():
            if url:
                setattr(opp, platform, url)
                socials_added[platform] = url
                session.add(
                    ContactEvidenceRecord(
                        opportunity_id=opp.id,
                        contact_type=platform.upper(),
                        contact_value=url,
                        source="website_social_scraper",
                        source_evidence_url=opp.website,
                        evidence_status="VERIFIED",
                        verification_method="HTML_LINK_EXTRACT",
                        verification_notes=f"Discovered official {platform.capitalize()} profile.",
                        discovered_at=utc_now(),
                        verified_at=utc_now(),
                    )
                )

        opp.last_verified_at = utc_now()
        await session.flush()
        return {
            "success": True,
            "opportunity_id": opp.id,
            "website": opp.website,
            "email": opp.email,
            "socials": {
                "instagram": opp.instagram,
                "facebook": opp.facebook,
                "linkedin": opp.linkedin,
                "twitter": opp.twitter,
            },
            "newly_added_socials": socials_added,
        }
