"""
RIGHT FIT — Core Career Engine API Entrypoint
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import init_db
from contracts.common.errors import APIErrorResponse, ErrorCode, ErrorDetail, ErrorPayload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initializes database tables on startup."""
    await init_db()
    yield


app = FastAPI(
    title="RIGHT FIT Core Career Engine",
    description="Central career intelligence orchestration, candidate identity, ATS aggregation, and contract gateway.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id_and_timing(request: Request, call_next):
    """Ensures every request has a correlation ID and attaches timing headers."""
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["x-request-id"] = request_id
    response.headers["x-response-time-ms"] = f"{process_time:.2f}"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats Pydantic validation errors into standard APIErrorResponse contract."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in err["loc"] if loc != "body"),
            issue=err["msg"],
            rejected_value=str(err.get("input", "")) if err.get("input") is not None else None,
        )
        for err in exc.errors()
    ]
    error_payload = ErrorPayload(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request payload failed schema validation",
        details=details,
        request_id=request_id,
        service="core_career_engine",
        retryable=False,
    )
    envelope = APIErrorResponse(success=False, error=error_payload)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=envelope.model_dump(mode="json"))


@app.exception_handler(StarletteHTTPException)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException | StarletteHTTPException) -> JSONResponse:
    """Formats HTTPExceptions into standard APIErrorResponse contract."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHENTICATED,
        403: ErrorCode.UNAUTHORIZED,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        409: ErrorCode.RESOURCE_CONFLICT,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        502: ErrorCode.UPSTREAM_SERVICE_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
        504: ErrorCode.UPSTREAM_TIMEOUT,
    }
    err_code = code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    error_payload = ErrorPayload(
        code=err_code,
        message=str(exc.detail),
        details=[],
        request_id=request_id,
        service="core_career_engine",
        retryable=exc.status_code in (429, 502, 503, 504),
    )
    envelope = APIErrorResponse(success=False, error=error_payload)
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump(mode="json"))


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled exceptions and returns standard 500 APIErrorResponse without leaking internals."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    error_payload = ErrorPayload(
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected server error occurred. Please try again later.",
        details=[],
        request_id=request_id,
        service="core_career_engine",
        retryable=True,
    )
    envelope = APIErrorResponse(success=False, error=error_payload)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=envelope.model_dump(mode="json"))


# Include Routers
app.include_router(health_router)  # /health/live and /health/ready
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root metadata discovery endpoint."""
    return {
        "service": "RIGHT FIT Core Career Engine",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "docs": "/docs",
        "api_v1": "/api/v1",
    }
