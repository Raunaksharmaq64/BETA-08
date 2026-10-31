"""
RIGHT FIT Core — API v1 Master Router
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.candidate import router as candidate_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.privacy import router as privacy_router
from app.api.v1.endpoints.resume import router as resume_router
from app.api.v1.endpoints.sources import router as sources_router
from app.api.v1.endpoints.verification import router as verification_router
from app.api.v1.endpoints.matching import router as matching_router
from app.api.v1.endpoints.crm import router as crm_router
from app.api.v1.endpoints.reminders import router as reminders_router
from app.api.v1.endpoints.interview_intelligence import router as interview_intelligence_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.freelance import router as freelance_router
from app.api.v1.endpoints.startups import router as startups_router
from app.api.v1.endpoints.unified_opportunities import router as unified_opportunities_router
from app.api.v1.endpoints.market import router as market_router
from app.api.v1.endpoints.beta import router as beta_router
from app.api.v1.endpoints.discovery import router as discovery_router

api_v1_router = APIRouter()

# Include Sub-Routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(candidate_router)
api_v1_router.include_router(privacy_router)
api_v1_router.include_router(resume_router)
api_v1_router.include_router(unified_opportunities_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(beta_router)
api_v1_router.include_router(sources_router)
api_v1_router.include_router(verification_router)
api_v1_router.include_router(matching_router)
api_v1_router.include_router(crm_router)
api_v1_router.include_router(reminders_router)
api_v1_router.include_router(interview_intelligence_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(freelance_router)
api_v1_router.include_router(startups_router)
api_v1_router.include_router(discovery_router)
