"""
RIGHT FIT Core — Authentication & Authorization Dependencies
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.db.models import User
from contracts.auth.schemas import AccountStatus

bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Extracts client IP address considering proxy headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"


def get_client_ua(request: Request) -> str:
    """Extracts client User-Agent string."""
    return request.headers.get("user-agent", "unknown")


async def get_current_user(
    request: Request,
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extracts, decodes, and validates Bearer access token or HttpOnly session cookie."""
    token: Optional[str] = None
    if bearer_creds and bearer_creds.credentials:
        token = bearer_creds.credentials
    else:
        # Fallback to session cookie
        token = request.cookies.get(settings.AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
            )
        user_id: str = payload["sub"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = select(User).where(User.id == user_id)
    res = await db.execute(query)
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
        )

    if user.status == AccountStatus.SUSPENDED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been suspended. Please contact platform support.",
        )

    if user.status == AccountStatus.DELETED.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deleted.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures the authenticated user is not pending deletion or restricted."""
    if current_user.status == AccountStatus.DELETION_PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is pending deletion. Normal authenticated actions are restricted.",
        )
    return current_user
