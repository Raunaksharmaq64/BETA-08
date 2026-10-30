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

api_v1_router = APIRouter()

# Include Sub-Routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(candidate_router)
api_v1_router.include_router(privacy_router)
