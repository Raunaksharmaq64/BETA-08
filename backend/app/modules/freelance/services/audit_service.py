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

        # 3. If email is missing, attempt deep email scraping
        if not opp.email:
            try:
                discovered_email = EmailScraper.deep_scrape_business_emails(opp.website)
                if discovered_email:
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
            except Exception as e:
                logger.debug(f"[AuditService] Email extraction error: {e}")

        await session.flush()
        return {
            "success": True,
            "opportunity_id": opp.id,
            "website": opp.website,
            "audit": audit_result,
            "email_discovered": opp.email,
        }
