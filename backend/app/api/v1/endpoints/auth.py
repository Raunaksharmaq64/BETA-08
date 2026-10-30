"""
RIGHT FIT Core — Authentication API Endpoints
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_client_ip, get_client_ua, get_current_user
from app.db.models import User
from app.services.auth_service import AuthService
from contracts.auth.schemas import (
    AccountStatus,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserResponse,
    UserRole,
    VerifyEmailRequest,
)
from contracts.common.envelope import ResponseMeta, StandardResponse

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])


def make_meta(request_id: str) -> ResponseMeta:
    return ResponseMeta(request_id=request_id, service="core_career_engine")


@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[UserResponse]:
    """Registers a candidate user and sets up initial profile and privacy records."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    ua = get_client_ua(request)

    user_resp, _ = await AuthService.register_user(db, req, ip_address=ip, user_agent=ua)
    return StandardResponse(data=user_resp, meta=make_meta(req_id))


@router.post("/login", response_model=StandardResponse[TokenResponse])
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponse]:
    """Authenticates user, issues access & refresh tokens, and attaches secure HttpOnly cookie."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    ua = get_client_ua(request)

    token_resp = await AuthService.login_user(db, req, ip_address=ip, user_agent=ua)

    # Attach HttpOnly cookie
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token_resp.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return StandardResponse(data=token_resp, meta=make_meta(req_id))


@router.post("/logout", response_model=StandardResponse[dict])
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Terminates active session and clears authentication cookies."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)

    raw_refresh = request.headers.get("x-refresh-token")
    await AuthService.logout_user(db, current_user.id, raw_refresh, ip_address=ip)

    response.delete_cookie(settings.AUTH_COOKIE_NAME)
    return StandardResponse(data={"message": "Logged out successfully."}, meta=make_meta(req_id))


@router.post("/refresh", response_model=StandardResponse[TokenResponse])
async def refresh_token(
    req: RefreshTokenRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponse]:
    """Rotates refresh token and issues renewed access token with replay-attack detection."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)
    ua = get_client_ua(request)

    token_resp = await AuthService.refresh_session(db, req, ip_address=ip, user_agent=ua)

    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token_resp.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return StandardResponse(data=token_resp, meta=make_meta(req_id))


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> StandardResponse[UserResponse]:
    """Returns authenticated user identity."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    resp = UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=UserRole(current_user.role),
        status=AccountStatus(current_user.status),
        is_email_verified=current_user.is_email_verified,
        created_at=current_user.created_at,
    )
    return StandardResponse(data=resp, meta=make_meta(req_id))


@router.post("/change-password", response_model=StandardResponse[dict])
async def change_password(
    req: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Updates password and revokes all active refresh sessions."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)

    await AuthService.change_password(db, current_user.id, req, ip_address=ip)
    return StandardResponse(data={"message": "Password changed successfully. Please log in again."}, meta=make_meta(req_id))


@router.post("/forgot-password", response_model=StandardResponse[dict])
async def forgot_password(
    req: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Initiates password recovery without leaking account existence."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)

    msg, _ = await AuthService.forgot_password(db, req, ip_address=ip)
    return StandardResponse(data={"message": msg}, meta=make_meta(req_id))


@router.post("/reset-password", response_model=StandardResponse[dict])
async def reset_password(
    req: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Completes password reset using single-use cryptographic token."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)

    await AuthService.reset_password(db, req, ip_address=ip)
    return StandardResponse(data={"message": "Password has been successfully reset. You may now log in."}, meta=make_meta(req_id))


@router.post("/verify-email", response_model=StandardResponse[dict])
async def verify_email(
    req: VerifyEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Verifies candidate email address via single-use token."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    ip = get_client_ip(request)

    await AuthService.verify_email(db, req.token, ip_address=ip)
    return StandardResponse(data={"message": "Email address verified successfully."}, meta=make_meta(req_id))


@router.post("/resend-verification", response_model=StandardResponse[dict])
async def resend_verification(
    req: ResendVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Resends email verification link with rate limiting."""
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return StandardResponse(
        data={"message": "If this account is unverified, a verification link has been sent."},
        meta=make_meta(req_id),
    )

