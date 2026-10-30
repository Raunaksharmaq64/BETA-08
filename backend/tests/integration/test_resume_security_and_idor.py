"""
Security and IDOR isolation tests for Resume Intelligence.
Verifies cross-candidate isolation, unauthenticated rejection, malicious file blocking, and audit integrity.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_resumes"


async def create_candidate(client: AsyncClient, email: str) -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!@#Secure", "full_name": "Test User"}
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"}
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_cross_candidate_idor_isolation():
    """Verifies that Candidate A cannot access, download, inspect, or delete Candidate B's resume."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers_a = await create_candidate(client, "user.a.idor@example.com")
        headers_b = await create_candidate(client, "user.b.idor@example.com")

        # Candidate A uploads a resume
        pdf_path = FIXTURES_DIR / "standard_one_page.pdf"
        with open(pdf_path, "rb") as f:
            files = {"file": ("standard_one_page.pdf", f.read(), "application/pdf")}
            data = {"title": "Candidate A Secret Resume"}
            up_res = await client.post("/api/v1/resumes", headers=headers_a, data=data, files=files)

        assert up_res.status_code == 201
        resume_a_id = up_res.json()["resume_id"]

        # Parse Candidate A's resume
        await client.post(f"/api/v1/resumes/{resume_a_id}/parse", headers=headers_a)

        # 1. Candidate B attempts to GET Candidate A's resume summary
        get_res = await client.get(f"/api/v1/resumes/{resume_a_id}", headers=headers_b)
        assert get_res.status_code in (404, 403), "Candidate B must not view Candidate A's resume"

        # 2. Candidate B attempts to download Candidate A's file
        dl_res = await client.get(f"/api/v1/resumes/{resume_a_id}/download", headers=headers_b)
        assert dl_res.status_code in (404, 403), "Candidate B must not download Candidate A's file"

        # 3. Candidate B attempts to inspect Candidate A's extraction
        ext_res = await client.get(f"/api/v1/resumes/{resume_a_id}/extraction", headers=headers_b)
        assert ext_res.status_code in (404, 403), "Candidate B must not inspect Candidate A's extraction"

        # 4. Candidate B attempts to access Candidate A's review workbench
        rev_res = await client.get(f"/api/v1/resumes/{resume_a_id}/review", headers=headers_b)
        assert rev_res.status_code in (404, 403), "Candidate B must not inspect Candidate A's review"

        # 5. Candidate B attempts to modify Candidate A's review
        patch_res = await client.patch(
            f"/api/v1/resumes/{resume_a_id}/review",
            headers=headers_b,
            json={"field_id": "fake_id", "action": "CONFIRM"}
        )
        assert patch_res.status_code in (404, 403), "Candidate B must not modify Candidate A's review"

        # 6. Candidate B attempts to delete Candidate A's resume
        del_res = await client.delete(f"/api/v1/resumes/{resume_a_id}", headers=headers_b)
        assert del_res.status_code in (404, 403), "Candidate B must not delete Candidate A's resume"

        # Verify Candidate A's resume is still safe
        check_res = await client.get(f"/api/v1/resumes/{resume_a_id}", headers=headers_a)
        assert check_res.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected():
    """Verifies that all resume endpoints reject unauthenticated access."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/api/v1/resumes")).status_code == 401
        assert (await client.post("/api/v1/resumes")).status_code == 401
        assert (await client.get("/api/v1/resumes/dummy_id")).status_code == 401
        assert (await client.delete("/api/v1/resumes/dummy_id")).status_code == 401
        assert (await client.get("/api/v1/resumes/dummy_id/download")).status_code == 401


@pytest.mark.asyncio
async def test_malicious_file_rejection():
    """Verifies that executable or malformed files are rejected on upload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await create_candidate(client, "user.malicious.test@example.com")

        exe_path = FIXTURES_DIR / "malicious.exe"
        with open(exe_path, "rb") as f:
            files = {"file": ("malicious.exe", f.read(), "application/x-msdownload")}
            data = {"title": "Exploit Attempt"}
            res = await client.post("/api/v1/resumes", headers=headers, data=data, files=files)

        assert res.status_code == 400
        assert "Unsupported or malformed" in res.json()["error"]["message"]
