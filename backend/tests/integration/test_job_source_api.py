"""
Integration Tests: Job Source Framework & Ingestion Lifecycle API
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Tests:
- Source Registration & Validation
- Policy Gate Rejection (DRAFT/BLOCKED sources cannot ingest)
- Policy Gate Approval & Audit History
- Ingestion Run Execution (Observation, Normalization, Deduplication)
- Ingestion Idempotency & Duplicate Suppression
- Source Run Logs & Resilience Updates
- Canonical Opportunities Search & Grounded Salary Integrity
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def get_auth_headers(client: AsyncClient, email: str = "source.admin@example.com") -> dict:
    """Helper to register and login an admin/manager user."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Job Source Admin",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_job_source_lifecycle_and_policy_gate():
    """Validates the complete lifecycle: registration, policy gate check, approval, ingestion, and search."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_auth_headers(client, email="sources.lead@example.com")

        # ----------------------------------------------------------------------
        # 1. Register Source (Initial status should be DRAFT)
        # ----------------------------------------------------------------------
        create_payload = {
            "source_key": "synth-tech-board",
            "display_name": "Tech Corp Board",
            "source_type": "ATS_JOB_BOARD",
            "provider": "synthetic",
            "base_url": "synthetic://tech-corp",
            "rate_limit_per_minute": 60,
            "timeout_seconds": 15.0,
            "retry_max_attempts": 3,
            "notes": "Internal verified synthetic feed for testing",
        }

        reg_res = await client.post("/api/v1/sources", headers=headers, json=create_payload)
        assert reg_res.status_code == 201, reg_res.text
        source_data = reg_res.json()["data"]
        source_id = source_data["id"]

        assert source_data["source_key"] == "synth-tech-board"
        assert source_data["policy_status"] == "DRAFT"
        assert source_data["circuit_breaker_state"] == "CLOSED"

        # ----------------------------------------------------------------------
        # 2. Policy Gate Block: Ingestion Attempt while DRAFT must fail (403)
        # ----------------------------------------------------------------------
        ingest_attempt_1 = await client.post(
            f"/api/v1/sources/{source_id}/ingest",
            headers=headers,
            json={"max_records": 10},
        )
        assert ingest_attempt_1.status_code == 403
        err_msg = ingest_attempt_1.json()["error"]["message"]
        assert "Policy gate rejection" in err_msg

        # ----------------------------------------------------------------------
        # 3. Policy Gate Transition: DRAFT -> ACTIVE with audit rationale
        # ----------------------------------------------------------------------
        policy_update_payload = {
            "policy_status": "ACTIVE",
            "review_notes": "Security, legal compliance, and robots.txt review passed.",
        }
        policy_res = await client.patch(
            f"/api/v1/sources/{source_id}/policy",
            headers=headers,
            json=policy_update_payload,
        )
        assert policy_res.status_code == 200
        updated_source = policy_res.json()["data"]
        assert updated_source["policy_status"] == "ACTIVE"
        assert len(updated_source["policy_decision_json"]["history"]) >= 1

        # ----------------------------------------------------------------------
        # 4. Ingestion Run 1: Permitted and Normalizes Opportunities
        # ----------------------------------------------------------------------
        ingest_res_1 = await client.post(
            f"/api/v1/sources/{source_id}/ingest",
            headers=headers,
            json={"max_records": 10},
        )
        assert ingest_res_1.status_code == 200, ingest_res_1.text
        run_1_data = ingest_res_1.json()["data"]
        assert run_1_data["status"] == "SUCCESS"
        assert run_1_data["records_fetched"] >= 2
        assert run_1_data["records_inserted"] >= 2
        assert run_1_data["circuit_state"] == "CLOSED"

        # ----------------------------------------------------------------------
        # 5. Ingestion Run 2: Idempotency (Updating existing, 0 duplicates inserted)
        # ----------------------------------------------------------------------
        ingest_res_2 = await client.post(
            f"/api/v1/sources/{source_id}/ingest",
            headers=headers,
            json={"max_records": 10},
        )
        assert ingest_res_2.status_code == 200
        run_2_data = ingest_res_2.json()["data"]
        assert run_2_data["status"] == "SUCCESS"
        # Since the exact same items were re-fetched, they should be updated, not duplicated
        assert run_2_data["records_inserted"] == 0
        assert run_2_data["records_updated"] == run_1_data["records_inserted"]

        # ----------------------------------------------------------------------
        # 6. Verify Source Observations & Run Logs
        # ----------------------------------------------------------------------
        runs_res = await client.get(f"/api/v1/sources/{source_id}/runs", headers=headers)
        assert runs_res.status_code == 200
        runs_list = runs_res.json()["data"]
        # Includes the initial rejected run and the 2 successful runs
        assert len(runs_list) >= 3

        obs_res = await client.get(f"/api/v1/sources/{source_id}/observations", headers=headers)
        assert obs_res.status_code == 200
        obs_list = obs_res.json()["data"]
        assert len(obs_list) >= 2
        assert obs_list[0]["normalization_status"] == "NORMALIZED"
        assert len(obs_list[0]["payload_hash_sha256"]) == 64

        # ----------------------------------------------------------------------
        # 7. Query Canonical Opportunities
        # ----------------------------------------------------------------------
        opps_res = await client.get("/api/v1/opportunities?search=Python", headers=headers)
        assert opps_res.status_code == 200
        opps_list = opps_res.json()["data"]
        assert len(opps_list) >= 1
        python_job = opps_list[0]
        assert "Python" in python_job["title"]
        assert python_job["is_remote"] is True
        assert python_job["min_salary"] == 160000.0
        assert python_job["max_salary"] == 210000.0
        assert python_job["is_salary_estimated"] is False
        assert "FastAPI" in python_job["required_skills"]
        assert python_job["provenance"]["provider"] == "synthetic"
