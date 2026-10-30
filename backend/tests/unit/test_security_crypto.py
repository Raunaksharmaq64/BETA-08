"""
Unit Tests: Cryptography & Security Utilities
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import time
from datetime import timedelta
import pytest
import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_random_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_argon2_password_hashing():
    """Verifies that passwords hashed with Argon2id verify correctly and resist tampering."""
    pwd = "CorrectHorseBatteryStaple123!"
    hashed = hash_password(pwd)

    assert hashed.startswith("$argon2id$")
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_access_token_creation_and_claims():
    """Verifies that access tokens contain required claims and expire as scheduled."""
    user_id = "usr-test-12345"
    email = "candidate@example.com"
    role = "CANDIDATE"

    token = create_access_token(user_id=user_id, email=email, role=role)
    payload = decode_token(token)

    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert payload["role"] == role
    assert payload["type"] == "access"
    assert payload["iss"] == "rightfit_core"
    assert "jti" in payload
    assert payload["exp"] > payload["iat"]


def test_expired_token_raises_exception():
    """Verifies that expired access tokens raise ExpiredSignatureError."""
    token = create_access_token(
        user_id="usr-expired",
        email="expired@example.com",
        role="CANDIDATE",
        expires_delta=timedelta(seconds=-10),  # already expired
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)


def test_refresh_token_family_assignment():
    """Verifies that refresh tokens are issued with a family ID."""
    token, family_id = create_refresh_token(user_id="usr-999")
    payload = decode_token(token)

    assert payload["sub"] == "usr-999"
    assert payload["family_id"] == family_id
    assert payload["type"] == "refresh"


def test_secure_random_token_and_hashing():
    """Verifies that random tokens are unique and SHA-256 token hashing is deterministic."""
    t1 = generate_secure_random_token(32)
    t2 = generate_secure_random_token(32)
    assert t1 != t2

    h1 = hash_token(t1)
    h2 = hash_token(t1)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest length
