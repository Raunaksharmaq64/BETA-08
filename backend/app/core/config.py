"""
RIGHT FIT Core — Application Configuration
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration settings for RIGHT FIT Core Career Engine."""

    APP_NAME: str = "RIGHT FIT Core Career Engine"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
    API_V1_STR: str = "/api/v1"

    # Cryptography & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "rightfit_dev_super_secret_signing_key_32bytes_min!")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "rightfit_jwt_signing_secret_key_minimum_32_bytes!")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # Rotating refresh tokens
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # Cookie Authentication
    AUTH_COOKIE_NAME: str = "rightfit_session"
    COOKIE_SECURE: bool = os.getenv("APP_ENV", "development") == "production"
    COOKIE_SAMESITE: str = "lax"
    COOKIE_HTTPONLY: bool = True

    # Database: Async SQLite for local/offline dev & testing, PostgreSQL in production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./rightfit_core.db"
    )

    # Redis: Task queues and rate limiting
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Rate Limiting (Requests per minute)
    RATE_LIMIT_LOGIN: int = 10
    RATE_LIMIT_REGISTER: int = 5
    RATE_LIMIT_PASSWORD_RESET: int = 3
    RATE_LIMIT_DATA_EXPORT: int = 2
    RATE_LIMIT_RESUME_UPLOAD: int = 10

    # Resume Storage & Intelligence
    RESUME_STORAGE_DIR: str = os.getenv(
        "RESUME_STORAGE_DIR",
        os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "resumes"))
    )
    MAX_RESUME_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_RESUME_EXTENSIONS: List[str] = ["pdf", "docx"]
    ALLOWED_RESUME_MIME_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    # Satellite Service Integrations
    LEADHUNTER_BASE_URL: str = os.getenv("LEADHUNTER_BASE_URL", "http://localhost:8001")
    STARTUP_INTELLIGENCE_BASE_URL: str = os.getenv("STARTUP_INTELLIGENCE_BASE_URL", "http://127.0.0.1:8002")
    INTERNAL_SERVICE_KEY: str = os.getenv("INTERNAL_SERVICE_KEY", "rightfit_internal_shared_secret_key_123")

    # AI & LLM Engine Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)

    # Search & Discovery Extraction Providers
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY", None)
    APIFY_TOKEN: Optional[str] = os.getenv("APIFY_TOKEN", None)
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY", None)
    HUNTER_API_KEY: Optional[str] = os.getenv("HUNTER_API_KEY", None)

    # External Commercial Job Aggregators
    ADZUNA_APP_ID: Optional[str] = os.getenv("ADZUNA_APP_ID", None)
    ADZUNA_APP_KEY: Optional[str] = os.getenv("ADZUNA_APP_KEY", None)
    JOOBLE_API_KEY: Optional[str] = os.getenv("JOOBLE_API_KEY", None)

    # Email & Notifications
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY", None)

    # AWS Cloud Infrastructure & S3 Object Storage
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_RESUMES: str = os.getenv("S3_BUCKET_RESUMES", "rightfit-resumes-prod")
    S3_BUCKET_REPORTS: str = os.getenv("S3_BUCKET_REPORTS", "rightfit-reports-prod")
    S3_BUCKET_BACKUPS: str = os.getenv("S3_BUCKET_BACKUPS", "rightfit-backups-prod")
    USE_S3_STORAGE: bool = os.getenv("USE_S3_STORAGE", "false").lower() in ("true", "1")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            ".env",
        ),
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
