"""
RIGHT FIT — OpenAPI & JSON Schema Generator
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import json
import sys
from pathlib import Path
import yaml

# Ensure imports resolve
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from contracts.common.errors import APIErrorResponse
from contracts.common.envelope import StandardResponse
from contracts.common.tasks import TaskEnvelope
from contracts.auth.service_identity import ServiceIdentity
from contracts.auth.schemas import UserResponse, RegisterRequest, LoginRequest
from contracts.profile.schemas import CandidateProfileResponse, CandidatePreferencesResponse
from contracts.privacy.schemas import PrivacySettingsResponse, DataExportDownloadResponse, AccountDeletionResponse
from contracts.opportunities.models import OpportunityEnvelope
from contracts.leads.models import (
    LeadDiscoveryRequest,
    LeadDiscoveryStatus,
    LeadDiscoveryResult,
    LeadDetailResponse,
)
from contracts.pain_points.models import (
    StartupDiscoveryRequest,
    StartupDiscoveryStatus,
    StartupDiscoveryResult,
    StartupProblemDetailResponse,
)
from app.main import app


def export_json_schemas():
    schemas_dir = ROOT_DIR / "docs" / "api" / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    models_to_export = {
        "opportunity-envelope.schema.json": OpportunityEnvelope,
        "api-error-response.schema.json": APIErrorResponse,
        "service-identity.schema.json": ServiceIdentity,
        "task-envelope.schema.json": TaskEnvelope,
        "user-response.schema.json": UserResponse,
        "candidate-profile.schema.json": CandidateProfileResponse,
        "candidate-preferences.schema.json": CandidatePreferencesResponse,
        "privacy-settings.schema.json": PrivacySettingsResponse,
        "data-export.schema.json": DataExportDownloadResponse,
        "account-deletion.schema.json": AccountDeletionResponse,
    }

    for filename, model in models_to_export.items():
        out_path = schemas_dir / filename
        schema = model.model_json_schema()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated schema: {out_path.name}")


def export_openapi_specs():
    openapi_dir = ROOT_DIR / "docs" / "api" / "openapi"
    openapi_dir.mkdir(parents=True, exist_ok=True)

    # 1. Core Career Engine OpenAPI (Full Phase 3 specification with all 39 endpoints)
    core_openapi = app.openapi()
    core_json_path = openapi_dir / "core-career-engine.json"
    core_yaml_path = openapi_dir / "core-career-engine.yaml"

    with open(core_json_path, "w", encoding="utf-8") as f:
        json.dump(core_openapi, f, indent=2)
    with open(core_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(core_openapi, f, sort_keys=False)
    print(f"Generated Core OpenAPI: {core_yaml_path.name}")


if __name__ == "__main__":
    export_json_schemas()
    export_openapi_specs()
