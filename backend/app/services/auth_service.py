"""
RIGHT FIT Core — Authentication & Identity Service
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_random_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.db.models import (
    AccountDeletionRequestRecord,
    CandidatePreferenceRecord,
    CandidateProfile,
    EmailVerificationTokenRecord,
    PasswordResetTokenRecord,
    PrivacySettingsRecord,
    RefreshTokenRecord,
    User,
    is_expired,
    utc_now,
)
from app.services.audit_service import AuditService
from app.services.rate_limiter import rate_limiter
from contracts.auth.schemas import (
    AccountStatus,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserRole,
)
from contracts.security.audit import AuditEventType


class AuthService:
    @staticmethod
    async def register_user(
        db: AsyncSession,
        req: RegisterRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[UserResponse, str]:
        """Registers a new user and provisions default profile, preferences, and privacy settings.
        Returns (UserResponse, raw_verification_token).
        """
        # 1. Rate limiting
        allowed, retry_after = rate_limiter.is_allowed(
            f"register:{ip_address or 'anon'}",
            max_requests=settings.RATE_LIMIT_REGISTER,
            window_seconds=60,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Registration rate limit exceeded. Retry after {retry_after}s.",
            )

        # 2. Check duplicate email
        normalized_email = req.email.strip().lower()
        query = select(User).where(User.email == normalized_email)
        res = await db.execute(query)
        if res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )

        # 3. Create User with Argon2id hash
        pwd_hash = hash_password(req.password)
        user = User(
            email=normalized_email,
            password_hash=pwd_hash,
            full_name=req.full_name.strip(),
            role=req.role.value if hasattr(req.role, "value") else str(req.role),
            status=AccountStatus.ACTIVE.value,
            is_email_verified=False,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(user)
        await db.flush()

        # 4. Provision default CandidateProfile & Preferences
        profile = CandidateProfile(
            user_id=user.id,
            headline="Candidate",
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(profile)
        await db.flush()

        preferences = CandidatePreferenceRecord(
            profile_id=profile.id,
            preferred_roles_json=[],
            preferred_skills_json=[],
            preferred_industries_json=[],
            preferred_locations_json=[],
            remote_preference="ANY",
            employment_types_json=["Full-time"],
            job_notification_frequency="DAILY",
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(preferences)

        # 5. Provision default PrivacySettings
        privacy = PrivacySettingsRecord(
            user_id=user.id,
            profile_visibility="PUBLIC",
            opportunity_alerts=True,
            email_notifications=True,
            ai_processing_enabled=True,
            data_usage_research=False,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(privacy)

        # 6. Generate single-use Email Verification Token
        raw_verify_token = generate_secure_random_token(32)
        verify_record = EmailVerificationTokenRecord(
            user_id=user.id,
            token_hash=hash_token(raw_verify_token),
            expires_at=utc_now() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS),
            is_used=False,
            created_at=utc_now(),
        )
        db.add(verify_record)
        await db.commit()
        await db.refresh(user)

        user_resp = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=UserRole(user.role),
            status=AccountStatus(user.status),
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
        )
        return user_resp, raw_verify_token

    @staticmethod
    async def login_user(
        db: AsyncSession,
        req: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticates user, validates account status, and issues rotating tokens."""
        normalized_email = req.email.strip().lower()

        # 1. Rate limiting by IP and by account email
        for key in [f"login_ip:{ip_address or 'anon'}", f"login_email:{normalized_email}"]:
            allowed, retry_after = rate_limiter.is_allowed(
                key, max_requests=settings.RATE_LIMIT_LOGIN, window_seconds=60
            )
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Retry after {retry_after} seconds.",
                )

        # 2. Lookup User
        query = select(User).where(User.email == normalized_email)
        res = await db.execute(query)
        user = res.scalar_one_or_none()

        if not user or not verify_password(req.password, user.password_hash):
            await AuditService.record_event(
                db,
                event_type=AuditEventType.LOGIN_FAILURE,
                status="FAILURE",
                actor_email=normalized_email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "invalid_credentials"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # 3. Account status validation
        if user.status == AccountStatus.SUSPENDED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended. Please contact support.",
            )
        if user.status == AccountStatus.DELETED.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account has been deleted.",
            )

        # 4. Issue access token & rotating refresh token
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        raw_refresh, family_id = create_refresh_token(user_id=user.id)

        # 5. Persist refresh token hash
        session_record = RefreshTokenRecord(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            family_id=family_id,
            is_revoked=False,
            expires_at=utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            created_at=utc_now(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(session_record)

        await AuditService.record_event(
            db,
            event_type=AuditEventType.LOGIN_SUCCESS,
            status="SUCCESS",
            user_id=user.id,
            actor_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=raw_refresh,
        )

    @staticmethod
    async def refresh_session(
        db: AsyncSession,
        req: RefreshTokenRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Rotates refresh token and detects reuse/replay attacks."""
        raw_token = req.refresh_token
        try:
            payload = decode_token(raw_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type.")
            user_id = payload["sub"]
            family_id = payload["family_id"]
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")

        token_hash = hash_token(raw_token)
        query = select(RefreshTokenRecord).where(RefreshTokenRecord.token_hash == token_hash)
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        # REUSE DETECTION: If token record not found or already revoked, revoke ALL tokens in family!
        if not record or record.is_revoked:
            revoke_stmt = (
                update(RefreshTokenRecord)
                .where(RefreshTokenRecord.family_id == family_id)
                .values(is_revoked=True)
            )
            await db.execute(revoke_stmt)
            await AuditService.record_event(
                db,
                event_type=AuditEventType.SESSION_REVOKED,
                status="WARNING",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "refresh_token_reuse_detected", "family_id": family_id},
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Security alert: Token reuse detected. All sessions in this chain have been terminated.",
            )

        # Check expiration
        if is_expired(record.expires_at):
            record.is_revoked = True
            await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired.")

        # Invalidate current token and issue new pair in same family
        record.is_revoked = True

        user_query = select(User).where(User.id == user_id)
        u_res = await db.execute(user_query)
        user = u_res.scalar_one_or_none()
        if not user or user.status != AccountStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive.")

        new_access = create_access_token(user_id=user.id, email=user.email, role=user.role)
        new_refresh, _ = create_refresh_token(user_id=user.id, family_id=family_id)

        new_record = RefreshTokenRecord(
            user_id=user.id,
            token_hash=hash_token(new_refresh),
            family_id=family_id,
            is_revoked=False,
            expires_at=utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            created_at=utc_now(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(new_record)
        await db.commit()

        return TokenResponse(
            access_token=new_access,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh,
        )

    @staticmethod
    async def logout_user(
        db: AsyncSession,
        user_id: str,
        raw_refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Revokes the current refresh session and logs security event."""
        if raw_refresh_token:
            token_hash = hash_token(raw_refresh_token)
            stmt = (
                update(RefreshTokenRecord)
                .where(RefreshTokenRecord.token_hash == token_hash)
                .values(is_revoked=True)
            )
            await db.execute(stmt)

        await AuditService.record_event(
            db,
            event_type=AuditEventType.LOGOUT,
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
        )
        await db.commit()

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: str,
        req: ChangePasswordRequest,
        ip_address: Optional[str] = None,
    ) -> None:
        """Changes password and invalidates all existing sessions."""
        query = select(User).where(User.id == user_id)
        res = await db.execute(query)
        user = res.scalar_one_or_none()
        if not user or not verify_password(req.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        user.password_hash = hash_password(req.new_password)
        user.updated_at = utc_now()

        # Invalidate all active sessions for security
        revoke_all = (
            update(RefreshTokenRecord)
            .where(RefreshTokenRecord.user_id == user_id)
            .values(is_revoked=True)
        )
        await db.execute(revoke_all)

        await AuditService.record_event(
            db,
            event_type=AuditEventType.PASSWORD_CHANGE,
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
        )
        await db.commit()

    @staticmethod
    async def forgot_password(
        db: AsyncSession,
        req: ForgotPasswordRequest,
        ip_address: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """Initiates password reset without leaking account existence.
        Returns (generic_message, Optional[raw_reset_token_for_dev_tests]).
        """
        normalized_email = req.email.strip().lower()
        allowed, retry_after = rate_limiter.is_allowed(
            f"forgot_pwd:{normalized_email}",
            max_requests=settings.RATE_LIMIT_PASSWORD_RESET,
            window_seconds=60,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Password recovery rate limit reached. Retry after {retry_after}s.",
            )

        query = select(User).where(User.email == normalized_email)
        res = await db.execute(query)
        user = res.scalar_one_or_none()

        dev_token = None
        if user and user.status == AccountStatus.ACTIVE.value:
            raw_token = generate_secure_random_token(32)
            dev_token = raw_token
            record = PasswordResetTokenRecord(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=utc_now() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
                is_used=False,
                created_at=utc_now(),
            )
            db.add(record)
            await AuditService.record_event(
                db,
                event_type=AuditEventType.PASSWORD_RESET_REQUEST,
                status="SUCCESS",
                user_id=user.id,
                actor_email=normalized_email,
                ip_address=ip_address,
            )
            await db.commit()

        # Safe response to prevent enumeration
        msg = "If an account exists with this email address, a password recovery link has been dispatched."
        return msg, dev_token

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        req: ResetPasswordRequest,
        ip_address: Optional[str] = None,
    ) -> None:
        """Completes password reset using single-use cryptographically verified token."""
        token_hash = hash_token(req.token)
        query = select(PasswordResetTokenRecord).where(
            PasswordResetTokenRecord.token_hash == token_hash,
            PasswordResetTokenRecord.is_used == False,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        if not record or is_expired(record.expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token is invalid, expired, or has already been used.",
            )

        # Mark token used
        record.is_used = True

        # Update user password
        u_query = select(User).where(User.id == record.user_id)
        u_res = await db.execute(u_query)
        user = u_res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Associated user not found.")

        user.password_hash = hash_password(req.new_password)
        user.updated_at = utc_now()

        # Revoke all active sessions
        revoke_stmt = (
            update(RefreshTokenRecord)
            .where(RefreshTokenRecord.user_id == user.id)
            .values(is_revoked=True)
        )
        await db.execute(revoke_stmt)

        await AuditService.record_event(
            db,
            event_type=AuditEventType.PASSWORD_RESET_COMPLETE,
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
        )
        await db.commit()

    @staticmethod
    async def verify_email(
        db: AsyncSession,
        token: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Marks candidate email verified via single-use token."""
        token_hash = hash_token(token)
        query = select(EmailVerificationTokenRecord).where(
            EmailVerificationTokenRecord.token_hash == token_hash,
            EmailVerificationTokenRecord.is_used == False,
        )
        res = await db.execute(query)
        record = res.scalar_one_or_none()

        if not record or is_expired(record.expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token is invalid, expired, or already used.",
            )

        record.is_used = True

        u_query = select(User).where(User.id == record.user_id)
        u_res = await db.execute(u_query)
        user = u_res.scalar_one_or_none()
        if user:
            user.is_email_verified = True
            user.updated_at = utc_now()

        await AuditService.record_event(
            db,
            event_type=AuditEventType.EMAIL_VERIFIED,
            status="SUCCESS",
            user_id=record.user_id,
            ip_address=ip_address,
        )
        await db.commit()
