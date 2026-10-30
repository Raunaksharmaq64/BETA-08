"""
Integration Tests: Candidate Profile, Experience, Skills & Preferences APIs
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import init_db
from app.main import app
from app.services.rate_limiter import rate_limiter





async def register_and_get_token(client: AsyncClient, email: str = "profile_user@example.com") -> str:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Gina Linetti",
    })
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_profile_update_and_retrieval():
    """Verifies updating and retrieving candidate personal information."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "profile_edit@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Update Profile
        update_payload = {
            "headline": "Lead Systems Architect & AI Engineer",
            "summary": "Specializing in microservices, distributed systems, and LLM orchestration.",
            "phone": "+1-555-019-2834",
            "city": "Seattle",
            "state": "WA",
            "country": "United States",
            "timezone": "America/Los_Angeles",
        }
        put_resp = await client.put("/api/v1/candidate/profile", json=update_payload, headers=headers)
        assert put_resp.status_code == 200
        data = put_resp.json()["data"]
        assert data["headline"] == "Lead Systems Architect & AI Engineer"
        assert data["city"] == "Seattle"

        # 2. Get Profile
        get_resp = await client.get("/api/v1/candidate/profile", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["summary"] == update_payload["summary"]


@pytest.mark.asyncio
async def test_education_crud_and_provenance():
    """Verifies adding and deleting education credentials with provenance tracking."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "edu_user@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # Add Education
        edu_payload = {
            "institution": "University of Washington",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "start_date": "2018-09",
            "end_date": "2022-06",
            "is_current": False,
            "achievements": "Summa Cum Laude, Dean's List",
            "provenance": "USER_PROVIDED",
        }
        add_resp = await client.post("/api/v1/candidate/education", json=edu_payload, headers=headers)
        assert add_resp.status_code == 201
        edu_id = add_resp.json()["data"]["id"]
        assert add_resp.json()["data"]["provenance"] == "USER_PROVIDED"

        # Delete Education
        del_resp = await client.delete(f"/api/v1/candidate/education/{edu_id}", headers=headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_experience_and_skills_crud():
    """Verifies adding and deleting experience and skills."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "exp_user@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # Add Experience
        exp_payload = {
            "company": "Stripe",
            "role": "Staff Software Engineer",
            "employment_type": "Full-time",
            "start_date": "2022-07",
            "is_current": True,
            "description": "Designing high-reliability payment routing services.",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Kafka"],
            "provenance": "USER_PROVIDED",
        }
        exp_resp = await client.post("/api/v1/candidate/experience", json=exp_payload, headers=headers)
        assert exp_resp.status_code == 201
        exp_id = exp_resp.json()["data"]["id"]
        assert len(exp_resp.json()["data"]["skills"]) == 4

        # Add Skill
        skill_payload = {
            "skill_name": "FastAPI",
            "category": "Backend Framework",
            "proficiency": "Expert",
            "years_experience": 5.0,
            "provenance": "USER_PROVIDED",
        }
        skill_resp = await client.post("/api/v1/candidate/skills", json=skill_payload, headers=headers)
        assert skill_resp.status_code == 201
        skill_id = skill_resp.json()["data"]["id"]

        # Delete Skill
        del_skill = await client.delete(f"/api/v1/candidate/skills/{skill_id}", headers=headers)
        assert del_skill.status_code == 200


@pytest.mark.asyncio
async def test_preferences_and_completeness():
    """Verifies career preferences persistence and profile completeness calculation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_get_token(client, "prefs_user@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Update Preferences
        pref_payload = {
            "preferred_roles": ["Principal Backend Engineer", "Distributed Systems Architect"],
            "preferred_skills": ["Python", "PostgreSQL", "Redis", "Docker"],
            "preferred_industries": ["Fintech", "Developer Tools", "AI Platforms"],
            "preferred_locations": ["Remote", "San Francisco, CA"],
            "remote_preference": "REMOTE",
            "min_salary": 180000,
            "max_salary": 240000,
            "currency": "USD",
            "employment_types": ["Full-time"],
            "job_notification_frequency": "IMMEDIATE",
        }
        pref_resp = await client.put("/api/v1/candidate/preferences", json=pref_payload, headers=headers)
        assert pref_resp.status_code == 200
        assert pref_resp.json()["data"]["remote_preference"] == "REMOTE"

        # 2. Check Completeness Calculation
        comp_resp = await client.get("/api/v1/candidate/profile/completeness", headers=headers)
        assert comp_resp.status_code == 200
        comp_data = comp_resp.json()["data"]
        assert comp_data["has_preferences"] is True
        assert comp_data["score_percentage"] >= 20
