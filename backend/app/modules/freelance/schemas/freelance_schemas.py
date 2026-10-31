"""
Pydantic Schemas for Freelance Intelligence Module Requests & Responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LeadSearchScanRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Target business category (e.g. 'Dentists', 'Lawyers')")
    city: str = Field(..., min_length=2, description="Target city/metro area (e.g. 'Indore', 'Austin, TX')")
    max_results: int = Field(default=20, ge=1, le=100)
    include_with_website: bool = Field(default=False)
    deep_scan: bool = Field(default=True)
    zones: Optional[List[str]] = Field(default=None)


class SaveOpportunityRequest(BaseModel):
    notes: Optional[str] = None


class UpdateDraftRequest(BaseModel):
    subject: Optional[str] = None
    message_body: Optional[str] = None
    recipient_contact: Optional[str] = None


class AddSuppressionRequest(BaseModel):
    recipient_contact: str = Field(..., min_length=3)
    reason: str = Field(default="UNSUBSCRIBED")


class GeneratePitchRequest(BaseModel):
    channel: str = Field(default="EMAIL")  # EMAIL or WHATSAPP
    tone: str = Field(default="professional")
    service: str = Field(default="Website Technical Repair & Modern Redesign")
    project_sample: Optional[str] = None
    refine_feedback: Optional[str] = None
    min_words: int = Field(default=150, ge=50, le=500)


class CandidateFreelanceSettingsRequest(BaseModel):
    maps_provider: Optional[str] = Field(default="serpapi")  # serpapi or apify
    serpapi_key: Optional[str] = None
    apify_token: Optional[str] = None
    gemini_key: Optional[str] = None
    sender_name: Optional[str] = None
    sender_brand: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 465
    smtp_email: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_ssl: Optional[bool] = True
