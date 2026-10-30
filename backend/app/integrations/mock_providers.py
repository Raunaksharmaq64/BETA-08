"""
RIGHT FIT — Mock Providers & Deterministic Scenario Simulator
Version: 1.0.0
Status: ACTIVE IMPLEMENTATION (Local Foundation & Contract Testing)

Provides deterministic, offline mock clients simulating LeadHunter AI
and Startup Intelligence satellite services without third-party API keys.
Includes transformation helpers to convert satellite outputs into canonical OpportunityEnvelopes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from contracts.common.errors import APIErrorResponse, ErrorCode, ErrorDetail, ErrorPayload
from contracts.health.models import DependencyHealth, HealthStatus, LivenessResponse, ReadinessResponse
from contracts.leads.models import (
    LeadDetailResponse,
    LeadDiscoveryRequest,
    LeadDiscoveryResult,
    LeadDiscoveryStatus,
    LeadSummary,
    ScanJobStatus,
    WebsiteAuditReport,
)
from contracts.opportunities.models import (
    EvidenceItem,
    FreelanceOpportunityPayload,
    JobOpportunityPayload,
    LocationInfo,
    OpportunityEnvelope,
    OpportunityType,
    OrganizationInfo,
    RemoteType,
    SourceProvenance,
    StartupProblemPayload,
    StatusInfo,
    VerificationStatus,
)
from contracts.pain_points.models import (
    StartupDiscoveryRequest,
    StartupDiscoveryResult,
    StartupDiscoveryStatus,
    StartupProblemDetailResponse,
    StartupProblemSummary,
    StartupScanStatus,
)


class MockLeadHunterClient:
    """Simulates communication with the LeadHunter AI satellite service."""

    def __init__(self, mode: str = "success") -> None:
        """
        Args:
            mode: Simulation scenario:
                  'success' | 'empty' | 'validation_error' | 'unavailable' | 'timeout'
        """
        self.mode = mode
        self.is_mock = True

    async def get_liveness(self) -> LivenessResponse:
        return LivenessResponse(status=HealthStatus.HEALTHY, service="leadhunter")

    async def get_readiness(self) -> ReadinessResponse:
        if self.mode == "unavailable":
            return ReadinessResponse(
                status=HealthStatus.UNHEALTHY,
                service="leadhunter",
                dependencies={
                    "database": DependencyHealth(status=HealthStatus.UNHEALTHY, message="Connection refused"),
                    "redis": DependencyHealth(status=HealthStatus.HEALTHY, latency_ms=1.2),
                },
            )
        return ReadinessResponse(
            status=HealthStatus.HEALTHY,
            service="leadhunter",
            dependencies={
                "database": DependencyHealth(status=HealthStatus.HEALTHY, latency_ms=2.1),
                "redis": DependencyHealth(status=HealthStatus.HEALTHY, latency_ms=0.9),
            },
        )

    async def trigger_discovery(self, request: LeadDiscoveryRequest, correlation_id: str) -> LeadDiscoveryStatus:
        if self.mode == "unavailable":
            raise RuntimeError("LeadHunter service unavailable (simulated 503)")
        if self.mode == "validation_error":
            raise ValueError("City parameter cannot be resolved (simulated 422)")

        return LeadDiscoveryStatus(
            discovery_id=f"disc_lh_{uuid.uuid4().hex[:8]}",
            status=ScanJobStatus.COMPLETED,
            progress_percentage=100,
            total_found=2 if self.mode == "success" else 0,
            completed_at=datetime.now(timezone.utc),
        )

    async def get_discovery_results(self, discovery_id: str) -> LeadDiscoveryResult:
        if self.mode == "empty":
            return LeadDiscoveryResult(discovery_id=discovery_id, leads=[], total_leads=0)

        leads = [
            LeadSummary(
                lead_id="lead_mock_001",
                business_name="Downtown Dental Clinic",
                category="Dental Clinic",
                city="Austin, TX",
                website="http://downtowndental-fake-broken.com",
                is_broken_website=True,
                phone="+1-512-555-0199",
                email="contact@downtowndental-fake.com",
                rating=4.6,
                reviews_count=84,
                suggested_pitch="Your website is currently throwing a 502 Bad Gateway error.",
            ),
            LeadSummary(
                lead_id="lead_mock_002",
                business_name="Austin Prime Accounting",
                category="Accounting",
                city="Austin, TX",
                website=None,
                is_broken_website=False,
                phone="+1-512-555-0144",
                email="info@austinprimeacct.com",
                rating=4.9,
                reviews_count=120,
                suggested_pitch="We noticed your business lacks an online presence.",
            ),
        ]
        return LeadDiscoveryResult(discovery_id=discovery_id, leads=leads, total_leads=len(leads))

    async def get_lead_detail(self, lead_id: str) -> LeadDetailResponse:
        lead = LeadSummary(
            lead_id=lead_id,
            business_name="Downtown Dental Clinic",
            category="Dental Clinic",
            city="Austin, TX",
            website="http://downtowndental-fake-broken.com",
            is_broken_website=True,
            phone="+1-512-555-0199",
            email="contact@downtowndental-fake.com",
            rating=4.6,
            reviews_count=84,
            suggested_pitch="Your website is currently throwing a 502 Bad Gateway error.",
        )
        audit = WebsiteAuditReport(
            url="http://downtowndental-fake-broken.com",
            dns_resolves=True,
            ssl_valid=False,
            http_status=502,
            load_time_seconds=8.4,
            mobile_friendly=False,
            tech_stack=["WordPress 4.9", "Apache"],
            issues=["Missing valid TLS/SSL certificate", "HTTP 502 Bad Gateway", "Viewport meta tag missing"],
        )
        return LeadDetailResponse(
            lead=lead,
            audit=audit,
            instagram="https://instagram.com/downtowndental_mock",
            facebook="https://facebook.com/downtowndental_mock",
        )

    def convert_to_opportunity_envelopes(self, result: LeadDiscoveryResult) -> List[OpportunityEnvelope]:
        """Translates LeadHunter outputs into normalized OpportunityEnvelopes."""
        envelopes: List[OpportunityEnvelope] = []
        for lead in result.leads:
            payload = FreelanceOpportunityPayload(
                business_category=lead.category,
                website_url=lead.website,
                is_broken_website=lead.is_broken_website,
                audit_status="COMPLETED",
                detected_issues=["SSL Certificate Missing", "HTTP Error"] if lead.is_broken_website else ["No Website"],
                suggested_pitch=lead.suggested_pitch,
                contact_email=lead.email,
                contact_phone=lead.phone,
            )
            env = OpportunityEnvelope(
                opportunity_id=f"opp_lead_{lead.lead_id}",
                opportunity_type=OpportunityType.FREELANCE,
                title=f"{lead.category} Web Modernization — {lead.business_name}",
                description=lead.suggested_pitch or f"Technical enhancement for {lead.business_name}",
                organization=OrganizationInfo(name=lead.business_name, website=lead.website),
                location=LocationInfo(city=lead.city, country="USA", remote_type=RemoteType.REMOTE),
                source=SourceProvenance(
                    provider="leadhunter",
                    original_url=lead.website or f"https://maps.google.com/?q={lead.business_name}",
                    external_id=lead.lead_id,
                ),
                status=StatusInfo(value=VerificationStatus.VERIFIED),
                evidence=[
                    EvidenceItem(
                        source_url=lead.website or "https://maps.google.com",
                        excerpt=f"Google Rating: {lead.rating} ({lead.reviews_count} reviews). Issues: {payload.detected_issues}",
                    )
                ],
                payload=payload,
            )
            envelopes.append(env)
        return envelopes


class MockStartupHunterClient:
    """Simulates communication with the Startup Intelligence satellite service."""

    def __init__(self, mode: str = "success") -> None:
        """
        Args:
            mode: Simulation scenario:
                  'success' | 'empty' | 'validation_error' | 'timeout'
        """
        self.mode = mode
        self.is_mock = True

    async def get_liveness(self) -> LivenessResponse:
        return LivenessResponse(status=HealthStatus.HEALTHY, service="startup_intelligence")

    async def get_readiness(self) -> ReadinessResponse:
        if self.mode == "timeout":
            return ReadinessResponse(
                status=HealthStatus.DEGRADED,
                service="startup_intelligence",
                dependencies={
                    "crawler_mesh": DependencyHealth(status=HealthStatus.DEGRADED, message="Reddit API latency high"),
                },
            )
        return ReadinessResponse(
            status=HealthStatus.HEALTHY,
            service="startup_intelligence",
            dependencies={
                "crawler_mesh": DependencyHealth(status=HealthStatus.HEALTHY, latency_ms=15.4),
            },
        )

    async def trigger_discovery(self, request: StartupDiscoveryRequest, correlation_id: str) -> StartupDiscoveryStatus:
        if self.mode == "timeout":
            raise TimeoutError("Startup Intelligence query timed out after 5.0s (simulated 504)")
        if self.mode == "validation_error":
            raise ValueError("Keywords list exceeds permitted maximum of 10 (simulated 422)")

        return StartupDiscoveryStatus(
            discovery_id=f"disc_si_{uuid.uuid4().hex[:8]}",
            status=StartupScanStatus.COMPLETED,
            progress_percentage=100,
            total_signals_analyzed=25,
            total_opportunities_found=2 if self.mode == "success" else 0,
            completed_at=datetime.now(timezone.utc),
        )

    async def get_discovery_results(self, discovery_id: str) -> StartupDiscoveryResult:
        if self.mode == "empty":
            return StartupDiscoveryResult(discovery_id=discovery_id, problems=[], total_count=0)

        problems = [
            StartupProblemSummary(
                signal_id="sig_mock_001",
                startup_name="CloudMetric SaaS",
                category="Database",
                pain_point="PostgreSQL connection pool exhaustions causing 504 timeouts during daily sync spikes.",
                detected_signal="Founder asking for help optimizing asyncpg pool on Reddit r/saas",
                community_source="Reddit r/saas",
                source_url="https://reddit.com/r/saas/comments/mock_post_1",
                tech_stack=["FastAPI", "PostgreSQL", "SQLAlchemy"],
                urgency_score=8,
                suggested_pitch="Hi team, I noticed your post regarding PostgreSQL pool exhaustion.",
                published_at=datetime.now(timezone.utc),
            ),
            StartupProblemSummary(
                signal_id="sig_mock_002",
                startup_name="DevShip.io",
                category="Performance",
                pain_point="Next.js SSR initial bundle size causing 4s Largest Contentful Paint (LCP).",
                detected_signal="Founder complaining on Hacker News about slow landing page lighthouse scores.",
                community_source="Hacker News",
                source_url="https://news.ycombinator.com/item?id=mock_item_2",
                tech_stack=["Next.js", "React", "TailwindCSS"],
                urgency_score=7,
                suggested_pitch="Hi DevShip team, noticed your HN discussion on LCP bottlenecks.",
                published_at=datetime.now(timezone.utc),
            ),
        ]
        return StartupDiscoveryResult(discovery_id=discovery_id, problems=problems, total_count=len(problems))

    async def get_problem_detail(self, signal_id: str) -> StartupProblemDetailResponse:
        problem = StartupProblemSummary(
            signal_id=signal_id,
            startup_name="CloudMetric SaaS",
            category="Database",
            pain_point="PostgreSQL connection pool exhaustions causing 504 timeouts during daily sync spikes.",
            detected_signal="Founder asking for help optimizing asyncpg pool on Reddit r/saas",
            community_source="Reddit r/saas",
            source_url="https://reddit.com/r/saas/comments/mock_post_1",
            tech_stack=["FastAPI", "PostgreSQL", "SQLAlchemy"],
            urgency_score=8,
            suggested_pitch="Hi team, I noticed your post regarding PostgreSQL pool exhaustion.",
            published_at=datetime.now(timezone.utc),
        )
        return StartupProblemDetailResponse(
            problem=problem,
            raw_excerpt="We are hitting massive production database connection pool exhaustion whenever 500+ users trigger batch analytics...",
            founder_contact_info={"reddit_user": "u/saas_dev_dan", "github": "https://github.com/saasdevdan"},
        )

    def convert_to_opportunity_envelopes(self, result: StartupDiscoveryResult) -> List[OpportunityEnvelope]:
        """Translates Startup Intelligence outputs into normalized OpportunityEnvelopes."""
        envelopes: List[OpportunityEnvelope] = []
        for prob in result.problems:
            payload = StartupProblemPayload(
                target_startup=prob.startup_name,
                pain_point_summary=prob.pain_point,
                problem_category=prob.category,
                community_source=prob.community_source,
                author="Founder",
                tech_stack_detected=prob.tech_stack,
                urgency_score=prob.urgency_score,
                recommended_solution=prob.suggested_pitch,
            )
            env = OpportunityEnvelope(
                opportunity_id=f"opp_startup_{prob.signal_id}",
                opportunity_type=OpportunityType.STARTUP_PROBLEM,
                title=f"Fix {prob.category} Bottleneck: {prob.startup_name}",
                description=prob.pain_point,
                organization=OrganizationInfo(name=prob.startup_name),
                location=LocationInfo(country="Global", remote_type=RemoteType.REMOTE),
                source=SourceProvenance(
                    provider="startup_intelligence",
                    original_url=prob.source_url,
                    external_id=prob.signal_id,
                ),
                status=StatusInfo(value=VerificationStatus.VERIFIED),
                evidence=[
                    EvidenceItem(
                        source_url=prob.source_url,
                        excerpt=prob.detected_signal,
                    )
                ],
                payload=payload,
            )
            envelopes.append(env)
        return envelopes
