"""
Integration tests for Resume Intelligence API lifecycle.
Covers upload, versioning, parsing, review workbench, profile sync, ATS analysis, download, and deletion.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_resumes"


@pytest.fixture
def auth_headers():
    return {}


async def register_and_login(client: AsyncClient, email: str = "candidate.resume@example.com") -> dict:
    """Helper to register and login a test candidate."""
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Test Resume Candidate"
        }
    )
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_resume_upload_and_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await register_and_login(client)

        # 1. Upload initial resume (PDF)
        pdf_path = FIXTURES_DIR / "standard_one_page.pdf"
        with open(pdf_path, "rb") as f:
            files = {"file": ("standard_one_page.pdf", f.read(), "application/pdf")}
            data = {"title": "Software Engineer Resume"}
            upload_res = await client.post("/api/v1/resumes", headers=headers, data=data, files=files)

        assert upload_res.status_code == 201
        upload_data = upload_res.json()
        resume_id = upload_data["resume_id"]
        v1_id = upload_data["version_id"]
        assert upload_data["version_number"] == 1
        assert upload_data["file_type"] == "pdf"
        assert upload_data["parsing_status"] == "UPLOADED"

        # 2. List candidate resumes
        list_res = await client.get("/api/v1/resumes", headers=headers)
        assert list_res.status_code == 200
        resumes = list_res.json()
        assert len(resumes) >= 1
        assert resumes[0]["id"] == resume_id
        assert resumes[0]["version_count"] == 1

        # 3. Upload version 2 (DOCX)
        docx_path = FIXTURES_DIR / "standard_resume.docx"
        with open(docx_path, "rb") as f:
            v2_files = {"file": ("standard_resume.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            v2_data = {"version_label": "v2 - Updated with DOCX"}
            v2_res = await client.post(f"/api/v1/resumes/{resume_id}/versions", headers=headers, data=v2_data, files=v2_files)

        assert v2_res.status_code == 201
        v2_data_json = v2_res.json()
        v2_id = v2_data_json["version_id"]
        assert v2_data_json["version_number"] == 2

        # 4. List versions
        vers_res = await client.get(f"/api/v1/resumes/{resume_id}/versions", headers=headers)
        assert vers_res.status_code == 200
        vers_list = vers_res.json()
        assert len(vers_list) == 2

        # 5. Set active version to v1
        act_res = await client.patch(f"/api/v1/resumes/{resume_id}/active-version?version_id={v1_id}", headers=headers)
        assert act_res.status_code == 200
        assert act_res.json()["active_version_id"] == v1_id

        # 6. Parse active version (v1 PDF)
        parse_res = await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)
        assert parse_res.status_code == 200
        ext_data = parse_res.json()
        assert ext_data["parsing_status"] == "REVIEW_REQUIRED"
        assert ext_data["personal_info"]["email"] == "jane.doe@example.com"
        assert len(ext_data["evidence_items"]) > 0

        # 7. Get Review Workbench
        review_res = await client.get(f"/api/v1/resumes/{resume_id}/review", headers=headers)
        assert review_res.status_code == 200
        review_data = review_res.json()
        assert review_data["pending_fields_count"] > 0
        first_ev = review_data["evidence_items"][0]
        field_id_to_confirm = first_ev["field_id"]

        # 8. Candidate confirms field
        patch_res = await client.patch(
            f"/api/v1/resumes/{resume_id}/review",
            headers=headers,
            json={
                "field_id": field_id_to_confirm,
                "action": "CONFIRM"
            }
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["confirmed_fields_count"] >= 1

        # 9. Candidate confirms and synchronizes profile
        sync_res = await client.post(
            f"/api/v1/resumes/{resume_id}/confirm",
            headers=headers,
            json={"overwrite_conflicts": False}
        )
        assert sync_res.status_code == 200
        sync_data = sync_res.json()
        assert sync_data["synced"] is True
        assert sync_data["fields_synced_count"] > 0

        # Verify candidate profile received synchronized skills and info
        prof_res = await client.get("/api/v1/candidate/profile", headers=headers)
        assert prof_res.status_code == 200
        raw_prof = prof_res.json()
        prof_json = raw_prof.get("data", raw_prof)
        assert prof_json["phone"] == "(555) 123-4567" or prof_json["email"] == "candidate.resume@example.com"
        assert len(prof_json["skills"]) > 0

        # 10. Run ATS Analysis against target job description
        ats_res = await client.post(
            f"/api/v1/resumes/{resume_id}/ats-analysis",
            headers=headers,
            json={
                "target_job_title": "Senior Python Backend Engineer",
                "target_job_description": (
                    "We need an experienced Senior Python Engineer skilled in FastAPI, PostgreSQL, "
                    "Redis, Docker, and Kubernetes to lead high-performance cloud services."
                )
            }
        )
        assert ats_res.status_code == 200
        ats_json = ats_res.json()
        assert ats_json["coverage_score"] > 0.0
        assert "python" in ats_json["matched_keywords"]
        assert ats_json["bullet_impact_score"] > 0.0
        assert len(ats_json["actionable_suggestions"]) > 0

        # 10b. Test Resume Quality Analysis Endpoint
        quality_res = await client.get(f"/api/v1/resumes/{resume_id}/quality", headers=headers)
        assert quality_res.status_code == 200
        quality_json = quality_res.json()
        assert quality_json["overall_quality_score"] > 0.0
        assert quality_json["quality_band"] in ("STRONG", "MODERATE", "NEEDS_IMPROVEMENT")
        assert len(quality_json["section_scores"]) >= 1

        # 10c. Test Job-Specific Matcher Endpoint
        match_res = await client.post(
            f"/api/v1/resumes/{resume_id}/job-match",
            headers=headers,
            json={
                "target_job_title": "Senior Python Backend Engineer",
                "target_job_description": "Requires 5+ years experience in Python, FastAPI, Docker, and PostgreSQL."
            }
        )
        assert match_res.status_code == 200
        match_json = match_res.json()
        assert match_json["overall_match_score"] > 0.0
        assert match_json["keyword_coverage_score"] > 0.0
        assert match_json["required_skills_match"]["match_percentage"] > 0.0

        # 10d. Test AI Suggestions Endpoint
        sug_res = await client.get(f"/api/v1/resumes/{resume_id}/ai-suggestions", headers=headers)
        assert sug_res.status_code == 200
        sug_json = sug_res.json()
        assert len(sug_json["suggestions"]) > 0
        assert sug_json["suggestions"][0]["evidence_required_from_candidate"] != ""

        # 11. Authenticated File Download
        download_res = await client.get(f"/api/v1/resumes/{resume_id}/download", headers=headers)
        assert download_res.status_code == 200
        assert download_res.headers["content-type"] == "application/pdf"
        assert len(download_res.content) > 0

        # 12. Delete Resume
        del_res = await client.delete(f"/api/v1/resumes/{resume_id}", headers=headers)
        assert del_res.status_code == 200

        # Verify resume is deleted
        check_res = await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
        assert check_res.status_code == 404
