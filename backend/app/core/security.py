"""
RIGHT FIT Core — Cryptography & Security Utilities
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation

Implements OWASP-recommended Argon2id password hashing, PyJWT access & refresh
token issuance, cryptographic token hashing (SHA-256), and rotation validation.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import argon2
import jwt
from argon2.exceptions import VerificationError, VerifyMismatchError

from app.core.config import settings

# Initialize Argon2id password hasher with secure parameters
_ph = argon2.PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hashes a plain-text password using Argon2id."""
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against an Argon2id hash using constant-time comparison."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerificationError, VerifyMismatchError):
        return False
    except Exception:
        return False


def generate_secure_random_token(n_bytes: int = 32) -> str:
    """Generates a cryptographically strong, URL-safe random token."""
    return secrets.token_urlsafe(n_bytes)


def hash_token(raw_token: str) -> str:
    """Computes SHA-256 hash of a token.
    Ensures raw refresh, verification, or reset tokens are never persisted in the database.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + delta

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iss": "rightfit_core",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: str,
    family_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, str]:
    """Creates a rotating JWT refresh token and returns (token_string, family_id)."""
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = now + delta
    assigned_family_id = family_id or str(uuid.uuid4())

    payload = {
        "sub": user_id,
        "family_id": assigned_family_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iss": "rightfit_core",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, assigned_family_id


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token signature and expiration.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        issuer="rightfit_core",
    )
