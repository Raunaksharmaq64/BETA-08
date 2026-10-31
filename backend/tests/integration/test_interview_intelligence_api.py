"""
Integration Tests: Interview Intelligence API, STAR Builder, Mock Rubric & Debriefs
Phase: 8 — CRM and Interview Intelligence
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient

from app.main import app


async def get_test_auth_headers(client: AsyncClient, email: str = "intel.cand@example.com") -> dict:
    """Registers and authenticates a test candidate."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!@#Secure",
            "full_name": "Interview Intel Candidate",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!@#Secure"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_interview_plans_and_48h_sprint_lifecycle():
    """Verify plan creation, round addition, and 48-Hour sprint generation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="intel.plan.cand@example.com")

        # 0. Create linked application first
        app_res = await client.post(
            "/api/v1/applications",
            headers=headers,
            json={
                "company_name": "Stripe",
                "job_title": "Senior Distributed Systems Engineer",
                "status": "INTERVIEW",
            },
        )
        assert app_res.status_code == 201
        app_id = app_res.json()["data"]["id"]

        # 1. Create interview plan
        plan_res = await client.post(
            "/api/v1/interview-plans",
            headers=headers,
            json={
                "application_id": app_id,
                "title": "Stripe Senior Infra Plan",
                "company_name": "Stripe",
                "role_title": "Senior Distributed Systems Engineer",
            },
        )
        assert plan_res.status_code == 201, plan_res.text
        plan_data = plan_res.json()["data"]
        plan_id = plan_data["id"]

        # 2. Add round
        round_res = await client.post(
            f"/api/v1/interview-plans/{plan_id}/rounds",
            headers=headers,
            json={
                "round_number": 1,
                "round_name": "Distributed Transactions & Architecture",
                "interview_format": "VIDEO",
            },
        )
        assert round_res.status_code == 201
        round_data = round_res.json()["data"]
        assert round_data["round_name"] == "Distributed Transactions & Architecture"

        # 3. Get 48-Hour sprint plan
        sprint_res = await client.get(
            f"/api/v1/interview-plans/{plan_id}/48-hour-prep",
            headers=headers,
        )
        assert sprint_res.status_code == 200
        sprint = sprint_res.json()["data"]
        assert sprint["company_name"] == "Stripe"
        assert len(sprint["prioritized_milestones"]) >= 3


@pytest.mark.asyncio
async def test_star_answers_and_mock_session_evaluation():
    """Verify grounded STAR stories, mock questions, and 6-factor rubric."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_test_auth_headers(client, email="intel.star.cand@example.com")

        # 0. Create linked application
        app_res = await client.post(
            "/api/v1/applications",
            headers=headers,
            json={
                "company_name": "Netflix",
                "job_title": "Senior Backend Architect",
                "status": "INTERVIEW",
            },
        )
        assert app_res.status_code == 201
        app_id = app_res.json()["data"]["id"]

        # 1. Create STAR story
        star_res = await client.post(
            "/api/v1/star-answers",
            headers=headers,
            json={
                "question": "Tell me about optimizing an API gateway",
                "category": "PERFORMANCE_OPTIMIZATION",
                "situation": "Gateway was throttling 15% of mobile client requests.",
                "task": "Redesign rate limiter with sliding window counter.",
                "action": "Implemented Redis Lua scripts and local memory caching.",
                "result": "Zero throttling on legitimate traffic and throughput increased by 300%.",
                "supporting_evidence_reference": "Resume Project: API Gateway Overhaul",
            },
        )
        assert star_res.status_code == 201
        star_data = star_res.json()["data"]
        assert star_data["missing_information_notes"] is None

        # 2. Start mock session
        mock_start_res = await client.post(
            "/api/v1/mock-interviews",
            headers=headers,
            json={
                "role_title": "Backend Engineer",
                "session_type": "BEHAVIORAL",
            },
        )
        assert mock_start_res.status_code == 201
        session_data = mock_start_res.json()["data"]
        session_id = session_data["id"]
        assert len(session_data["questions"]) >= 3
        q_id = session_data["questions"][0]["id"]

        # 3. Submit response for rubric evaluation
        answer_res = await client.post(
            f"/api/v1/mock-interviews/{session_id}/questions/{q_id}/answer",
            headers=headers,
            json={
                "question_id": q_id,
                "candidate_answer": (
                    "Situation: Our microservices communication caused cascading failures. "
                    "Task: I led the design of circuit breakers and exponential backoff retry policies. "
                    "Action: I used Resilience4j in Java, instrumented Prometheus metrics, and set fallback degraded responses. "
                    "Result: Successfully prevented 100% of cascading outages and reduced downtime to 0 hours over 6 months."
                ),
            },
        )
        assert answer_res.status_code == 200
        evaluated_q = answer_res.json()["data"]
        rubric = evaluated_q["rubric_evaluation"]
        assert rubric is not None
        assert rubric["overall_score"] >= 7.0
        assert len(rubric["strengths"]) > 0

        # 4. Create and retrieve debrief
        now_iso = datetime.now(timezone.utc).isoformat()
        debrief_res = await client.post(
            "/api/v1/interview-debriefs",
            headers=headers,
            json={
                "application_id": app_id,
                "round_name": "Distributed Transactions",
                "interview_date": now_iso,
                "questions_asked": ["Tell me about a difficult bug you found in production"],
                "topics_discussed": "Distributed transactions and idempotency",
                "candidate_reflections": "Gave concrete metrics and root cause explanation.",
                "recruiter_commitments": "Next steps within 3 business days.",
                "next_step": "Send follow-up email",
            },
        )
        assert debrief_res.status_code == 201
        debrief_list_res = await client.get("/api/v1/interview-debriefs", headers=headers)
        assert debrief_list_res.status_code == 200
        assert len(debrief_list_res.json()["data"]) >= 1
