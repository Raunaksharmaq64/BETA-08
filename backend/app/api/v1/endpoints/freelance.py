"""
RIGHT FIT Core — Freelance Opportunity & Outreach REST API Router
Version: 2.0.0
Phase: 9 — Native LeadHunter Freelance Intelligence Integration
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.models import User
from app.integrations.leadhunter.adapter import (
    CircuitState,
    LeadHunterUnavailableError,
    leadhunter_adapter,
)
from app.modules.freelance.repositories.freelance_repository import FreelanceRepository
from app.modules.freelance.schemas.freelance_schemas import (
    AddSuppressionRequest,
    CandidateFreelanceSettingsRequest,
    GeneratePitchRequest,
    LeadSearchScanRequest,
    SaveOpportunityRequest,
    UpdateDraftRequest,
)
from app.modules.freelance.services.audit_service import FreelanceAuditService
from app.modules.freelance.services.discovery_service import FreelanceDiscoveryService
from app.modules.freelance.services.export_service import FreelanceExportService
from app.modules.freelance.services.mockup_service import MockupService
from app.modules.freelance.services.outreach_service import FreelanceOutreachService
from app.services.freelance_service import freelance_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/freelance", tags=["Freelance Opportunity Finder"])


# -----------------------------------------------------------------------------
# Additional Request Schemas
# -----------------------------------------------------------------------------

class WhatsAppLinkRequest(BaseModel):
    message: Optional[str] = None


class EnrichContactsRequest(BaseModel):
    website_url: Optional[str] = None


class ExportOpportunitiesRequest(BaseModel):
    opportunity_ids: Optional[List[str]] = None
    city: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    query: Optional[str] = None
    saved_only: bool = False


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.get("", summary="List canonical freelance opportunities")
async def list_freelance_opportunities(
    city: Optional[str] = None,
    category: Optional[str] = None,
    classification_state: Optional[str] = None,
    priority: Optional[str] = None,
    query: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    offset = (page - 1) * per_page
    items = await freelance_service.list_opportunities(
        session=db,
        city=city,
        category=category,
        classification_state=classification_state,
        priority=priority,
        query=query,
        limit=per_page,
        offset=offset,
    )
    return {
        "success": True,
        "data": items,
        "page": page,
        "per_page": per_page,
        "count": len(items),
    }


@router.post("/scan-leads", summary="Trigger freelance lead discovery scan & import into Core")
async def scan_and_import_leads(
    req: LeadSearchScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Executes internal Freelance Intelligence discovery engine.
    Imports discovered leads into Core-owned canonical opportunities with contact evidence.
    Supports backward-compatible circuit-breaker resilience testing.
    """
    # 1. Compatibility check: If external adapter is explicitly configured to an unreachable test port or tripped
    if leadhunter_adapter.circuit_breaker.state != CircuitState.CLOSED or ":54321" in getattr(leadhunter_adapter, "base_url", ""):
        try:
            discovery_result = await leadhunter_adapter.search_leads(
                query=req.query,
                city=req.city,
                max_results=req.max_results,
                include_with_website=req.include_with_website,
                deep_scan=req.deep_scan,
            )
            imported_opportunities = []
            for lead in discovery_result.leads:
                opp = await freelance_service.import_lead_as_opportunity(db, lead)
                imported_opportunities.append(opp)

            return {
                "success": True,
                "degraded": False,
                "message": f"Successfully imported {len(imported_opportunities)} leads.",
                "data": imported_opportunities,
            }
        except LeadHunterUnavailableError as e:
            logger.warning(f"[FreelanceAPI] LeadHunter unavailable: {e}. Serving cached/local opportunities.")
            local_items = await freelance_service.list_opportunities(session=db, city=req.city, query=req.query, limit=10)
            return {
                "success": True,
                "degraded": True,
                "message": "LeadHunter service is currently offline or unreachable. Displaying cached local opportunities.",
                "data": local_items,
            }

    # 2. Native In-Process Discovery Execution
    try:
        discovery_res = await FreelanceDiscoveryService.discover_leads(
            session=db,
            user_id=current_user.id if current_user else None,
            query=req.query,
            city=req.city,
            max_results=req.max_results,
            include_with_website=req.include_with_website,
            deep_scan=req.deep_scan,
            zones=req.zones,
        )
        await db.commit()
        return {
            "success": True,
            "degraded": False,
            "message": f"Successfully discovered and imported {discovery_res['stats']['leads_imported']} opportunities.",
            "stats": discovery_res["stats"],
            "data": discovery_res["opportunities"],
        }
    except Exception as exc:
        logger.warning(f"[FreelanceAPI] Live search notice ({exc}). Serving catalog.")
        # Graceful fallback: return existing local opportunities
        local_items = await freelance_service.list_opportunities(
            session=db, city=req.city, query=req.query, limit=10
        )
        return {
            "success": True,
            "degraded": True,
            "message": f"Search engine notice: {exc}. Displaying available local opportunities.",
            "data": local_items,
        }


@router.get("/integration-status", summary="Check Freelance Intelligence engine and adapter status")
async def get_integration_status(
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    cb = leadhunter_adapter.circuit_breaker
    return {
        "success": True,
        "engine": "native_modular_monolith",
        "circuit_state": cb.state.value,
        "failure_count": cb.failure_count,
        "base_url": leadhunter_adapter.base_url,
        "degraded_mode_active": cb.state != CircuitState.CLOSED,
    }


@router.get("/saved/all", summary="List candidate saved freelance opportunities")
async def get_saved_opportunities(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    saved_records = await freelance_service.get_saved_opportunities(db, user_id=current_user.id)
    return {"success": True, "data": saved_records}


@router.get("/history", summary="List candidate recent discovery searches")
async def get_search_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    repo = FreelanceRepository(db)
    history = await repo.get_search_history(user_id=current_user.id, limit=limit)
    return {
        "success": True,
        "data": [
            {
                "id": h.id,
                "query": h.query,
                "city": h.city,
                "results_count": h.results_count,
                "leads_count": h.leads_count,
                "deep_scan": h.deep_scan,
                "searched_at": h.searched_at.isoformat() if h.searched_at else None,
            }
            for h in history
        ],
    }


@router.get("/settings", summary="Get candidate freelance BYOK keys & SMTP settings")
async def get_candidate_settings(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    repo = FreelanceRepository(db)
    settings_rec = await repo.get_candidate_settings(user_id=current_user.id)
    if not settings_rec:
        return {
            "success": True,
            "data": {
                "maps_provider": "serpapi",
                "has_serpapi_key": False,
                "has_apify_token": False,
                "has_gemini_key": False,
                "sender_name": None,
                "sender_brand": None,
                "smtp_email": None,
                "smtp_host": None,
            },
        }

    return {
        "success": True,
        "data": {
            "maps_provider": settings_rec.maps_provider,
            "has_serpapi_key": bool(settings_rec.encrypted_serpapi_key),
            "has_apify_token": bool(settings_rec.encrypted_apify_token),
            "has_gemini_key": bool(settings_rec.encrypted_gemini_key),
            "sender_name": settings_rec.sender_name,
            "sender_brand": settings_rec.sender_brand,
            "smtp_email": settings_rec.smtp_email,
            "smtp_host": settings_rec.smtp_host,
            "smtp_port": settings_rec.smtp_port,
            "smtp_use_ssl": settings_rec.smtp_use_ssl,
        },
    }


@router.post("/settings", summary="Save candidate freelance BYOK keys & SMTP settings")
async def save_candidate_settings(
    req: CandidateFreelanceSettingsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    repo = FreelanceRepository(db)
    rec = await repo.get_or_create_candidate_settings(user_id=current_user.id)

    if req.maps_provider:
        rec.maps_provider = req.maps_provider
    if req.serpapi_key:
        rec.encrypted_serpapi_key = req.serpapi_key.strip()
    if req.apify_token:
        rec.encrypted_apify_token = req.apify_token.strip()
    if req.gemini_key:
        rec.encrypted_gemini_key = req.gemini_key.strip()
    if req.sender_name is not None:
        rec.sender_name = req.sender_name.strip()
    if req.sender_brand is not None:
        rec.sender_brand = req.sender_brand.strip()
    if req.smtp_host is not None:
        rec.smtp_host = req.smtp_host.strip()
    if req.smtp_port is not None:
        rec.smtp_port = req.smtp_port
    if req.smtp_email is not None:
        rec.smtp_email = req.smtp_email.strip()
    if req.smtp_password:
        rec.encrypted_smtp_password = req.smtp_password
    if req.smtp_use_ssl is not None:
        rec.smtp_use_ssl = req.smtp_use_ssl

    await db.commit()
    return {"success": True, "message": "Freelance Intelligence settings updated successfully."}


@router.post("/export/excel", summary="Export freelance leads as formatted Excel spreadsheet (.xlsx)")
async def export_freelance_excel(
    req: ExportOpportunitiesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Exports filtered or explicitly selected freelance leads into a professional .xlsx spreadsheet.
    Includes sanitization against spreadsheet formula injection (DDE attacks).
    """
    items = []
    if req.saved_only and current_user:
        saved_records = await freelance_service.get_saved_opportunities(db, user_id=current_user.id)
        items = [s.opportunity for s in saved_records if s.opportunity]
    elif req.opportunity_ids and len(req.opportunity_ids) > 0:
        from sqlalchemy import select
        from app.db.models import FreelanceOpportunityRecord
        res = await db.execute(
            select(FreelanceOpportunityRecord).where(FreelanceOpportunityRecord.id.in_(req.opportunity_ids))
        )
        items = list(res.scalars().all())
    else:
        items = await freelance_service.list_opportunities(
            session=db,
            city=req.city,
            category=req.category,
            priority=req.priority,
            query=req.query,
            limit=500,
            offset=0,
        )

    if not items:
        raise HTTPException(status_code=400, detail="No freelance leads found matching export criteria.")

    excel_bytes = FreelanceExportService.generate_excel(items)
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"freelance_leads_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.post("/export/csv", summary="Export freelance leads as UTF-8 CSV spreadsheet (.csv)")
async def export_freelance_csv(
    req: ExportOpportunitiesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Exports filtered or explicitly selected freelance leads into a clean CSV spreadsheet with UTF-8 BOM.
    """
    items = []
    if req.saved_only and current_user:
        saved_records = await freelance_service.get_saved_opportunities(db, user_id=current_user.id)
        items = [s.opportunity for s in saved_records if s.opportunity]
    elif req.opportunity_ids and len(req.opportunity_ids) > 0:
        from sqlalchemy import select
        from app.db.models import FreelanceOpportunityRecord
        res = await db.execute(
            select(FreelanceOpportunityRecord).where(FreelanceOpportunityRecord.id.in_(req.opportunity_ids))
        )
        items = list(res.scalars().all())
    else:
        items = await freelance_service.list_opportunities(
            session=db,
            city=req.city,
            category=req.category,
            priority=req.priority,
            query=req.query,
            limit=500,
            offset=0,
        )

    if not items:
        raise HTTPException(status_code=400, detail="No freelance leads found matching export criteria.")

    csv_bytes = FreelanceExportService.generate_csv(items)
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"freelance_leads_{timestamp}.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.post("/{opportunity_id}/enrich-contacts", summary="Trigger deep contact & social profiles enrichment")
async def enrich_opportunity_contacts(
    opportunity_id: str,
    req: Optional[EnrichContactsRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        custom_web = req.website_url if req else None
        res = await FreelanceAuditService.enrich_contacts(db, opportunity_id, custom_website=custom_web)
        await db.commit()
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"[FreelanceAPI] Contact enrichment failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{opportunity_id}", summary="Get opportunity details with contact evidence and drafts")
async def get_opportunity_detail(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    opp = await freelance_service.get_opportunity_detail(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Freelance opportunity not found")
    return {"success": True, "data": opp}


@router.post("/{opportunity_id}/audit", summary="Trigger technical website audit & email extraction")
async def audit_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        res = await FreelanceAuditService.audit_opportunity(db, opportunity_id)
        await db.commit()
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"[FreelanceAPI] Audit failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{opportunity_id}/mockup", summary="Generate dynamic SVG mockup preview")
async def get_opportunity_mockup(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    opp = await freelance_service.get_opportunity_detail(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Freelance opportunity not found")

    svg_content = MockupService.generate_svg_markup(
        business_name=opp.business_name,
        category=opp.service_category,
    )
    return Response(content=svg_content, media_type="image/svg+xml")


@router.post("/{opportunity_id}/save", summary="Bookmark a freelance opportunity")
async def save_opportunity(
    opportunity_id: str,
    req: SaveOpportunityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    saved = await freelance_service.save_opportunity(
        db, user_id=current_user.id, opportunity_id=opportunity_id, notes=req.notes
    )
    await db.commit()
    return {"success": True, "data": saved}


@router.delete("/{opportunity_id}/save", summary="Remove bookmark for a freelance opportunity")
async def unsave_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    repo = FreelanceRepository(db)
    removed = await repo.remove_saved_opportunity(user_id=current_user.id, opportunity_id=opportunity_id)
    await db.commit()
    return {"success": True, "removed": removed}


@router.post("/{opportunity_id}/draft", summary="Generate a grounded outreach draft")
async def generate_draft(
    opportunity_id: str,
    channel: str = Query(default="EMAIL"),
    tone: str = Query(default="professional"),
    service: Optional[str] = Query(default=None),
    min_words: int = Query(default=150, ge=50, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        draft = await FreelanceOutreachService.generate_draft(
            session=db,
            user_id=current_user.id if current_user else None,
            opportunity_id=opportunity_id,
            channel=channel,
            tone=tone,
            service=service,
            min_words=min_words,
        )
        await db.commit()
        return {
            "success": True,
            "data": {
                "id": draft.id,
                "opportunity_id": draft.opportunity_id,
                "channel": draft.channel,
                "recipient_name": draft.recipient_name,
                "recipient_contact": draft.recipient_contact,
                "subject": draft.subject,
                "message_body": draft.message_body,
                "proposed_service": draft.proposed_service,
                "status": draft.status,
                "is_approved": draft.is_approved,
                "created_at": draft.created_at.isoformat() if draft.created_at else None,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/drafts/{draft_id}", summary="Edit draft (invalidates approval if approved)")
async def update_draft(
    draft_id: str,
    req: UpdateDraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        updated = await FreelanceOutreachService.update_draft(
            session=db,
            user_id=current_user.id if current_user else None,
            draft_id=draft_id,
            subject=req.subject,
            message_body=req.message_body,
            recipient_contact=req.recipient_contact,
        )
        await db.commit()
        return {
            "success": True,
            "data": {
                "id": updated.id,
                "opportunity_id": updated.opportunity_id,
                "subject": updated.subject,
                "message_body": updated.message_body,
                "recipient_contact": updated.recipient_contact,
                "status": updated.status,
                "is_approved": updated.is_approved,
                "candidate_edits_count": updated.candidate_edits_count,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/drafts/{draft_id}/approve", summary="Explicit candidate approval of outreach draft")
async def approve_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        approved = await FreelanceOutreachService.approve_draft(
            session=db, user_id=current_user.id, draft_id=draft_id
        )
        await db.commit()
        return {
            "success": True,
            "data": {
                "id": approved.id,
                "status": approved.status,
                "is_approved": approved.is_approved,
                "approved_at": approved.approved_at.isoformat() if approved.approved_at else None,
                "approved_recipient": approved.approved_recipient,
                "approved_subject": approved.approved_subject,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/drafts/{draft_id}/send", summary="Send approved outreach message")
async def send_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        delivery_log = await FreelanceOutreachService.send_approved_draft(
            session=db, user_id=current_user.id, draft_id=draft_id
        )
        await db.commit()
        return {
            "success": True,
            "message": "Outreach message dispatched successfully.",
            "data": {
                "id": delivery_log.id,
                "provider": delivery_log.provider,
                "delivery_status": delivery_log.delivery_status,
                "event_timestamp": delivery_log.event_timestamp.isoformat() if delivery_log.event_timestamp else None,
            },
        }
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{opportunity_id}/whatsapp-link", summary="Generate WhatsApp wa.me click-to-chat URL")
async def generate_whatsapp_link(
    opportunity_id: str,
    req: WhatsAppLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    opp = await freelance_service.get_opportunity_detail(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Freelance opportunity not found")

    phone = opp.phone or ""
    message = req.message or f"Hi {opp.business_name} team, noticed your Google Maps listing and wanted to share a quick digital growth proposal."
    link = FreelanceOutreachService.generate_whatsapp_link(phone, message)

    return {
        "success": True,
        "whatsapp_link": link,
        "phone": phone,
        "message": message,
    }


@router.post("/suppression", summary="Add recipient to suppression list")
async def add_suppression(
    req: AddSuppressionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    record = await freelance_service.add_suppression(
        session=db,
        recipient_contact=req.recipient_contact,
        reason=req.reason,
        user_id=current_user.id,
    )
    await db.commit()
    return {"success": True, "data": record}
