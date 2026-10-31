"""
Unit tests for Phase 4: Actionable AI Resume Suggestions.
Verifies grounded rewrites, strict anti-hallucination guardrails,
Gemini reliability/fallbacks, and the candidate approval workflow.
Phase: 4
"""

import pytest
from unittest.mock import AsyncMock, patch
from contracts.resume.schemas import AISuggestionDTO
from app.services.resume_ai_service import (
    ResumeAIService,
    resume_ai_service,
    GeminiRawSuggestionItem,
)


@pytest.mark.asyncio
async def test_grounded_rewrites_across_sections():
    """
    Verifies that suggestions are generated for summary, weak bullets, and project descriptions
    with clear 'Before vs After' and candidate verification requirements.
    """
    extractions = {
        "summary": None,  # Missing summary
        "experience": [
            {
                "company": "Alpha Corp",
                "responsibilities": [
                    "Responsible for database optimization and helped with queries.",
                    "Built microservices handling requests without metrics."
                ]
            }
        ],
        "projects": [
            {
                "name": "Cache Service",
                "description": "Simple cache."  # Under 12 words -> weak project description
            }
        ]
    }

    report = await resume_ai_service.generate_suggestions("res-101", "ver-101", extractions)

    assert len(report.suggestions) >= 3

    # 1. Summary suggestion
    summary_sug = next((s for s in report.suggestions if s.category == "SUMMARY_POLISH"), None)
    assert summary_sug is not None
    assert summary_sug.target_section == "SUMMARY"
    assert "[Target Role Title]" in summary_sug.recommended_text
    assert summary_sug.evidence_required_from_candidate != ""

    # 2. Bullet rewrite suggestion
    bullet_sug = next((s for s in report.suggestions if s.category == "BULLET_REWRITE"), None)
    assert bullet_sug is not None
    assert "Spearheaded" in bullet_sug.recommended_text
    assert "[X]%" in bullet_sug.recommended_text
    assert bullet_sug.evidence_required_from_candidate != ""

    # 3. Project description suggestion
    proj_sug = next((s for s in report.suggestions if s.category == "PROJECT_DESCRIPTION"), None)
    assert proj_sug is not None
    assert "Architected" in proj_sug.recommended_text
    assert proj_sug.evidence_required_from_candidate != ""


def test_anti_hallucination_metric_sanitization():
    """
    Strict guardrail: If Gemini attempts to inject unprompted bare metrics (e.g. 'reduced latency by 42%')
    when the original bullet had no metrics, the engine sanitizes the bare metric into '[X]%' placeholder.
    """
    original_text = "Responsible for backend optimization."
    raw_item = GeminiRawSuggestionItem(
        category="BULLET_REWRITE",
        target_section="EXPERIENCE",
        current_issue="Passive verb and lacks metrics",
        why_it_matters="Active verbs highlight ownership",
        current_text=original_text,
        recommended_text="Architected backend caching layers, cutting latency by 45% and saving $50k.",
        evidence_required_from_candidate="Provide verified latency and cost figures.",
        confidence_level="HIGH"
    )

    sanitized = resume_ai_service._validate_and_sanitize_suggestion(raw_item, original_text)

    assert sanitized is not None
    # 45% must be replaced with [X]% and $50k with [$X]
    assert "45%" not in sanitized.recommended_text
    assert "[X]%" in sanitized.recommended_text
    assert "$50k" not in sanitized.recommended_text
    assert "[$X]" in sanitized.recommended_text
    assert sanitized.original_preserved is True


def test_candidate_approval_workflow_accept():
    """Verifies that accepting a suggestion marks status ACCEPTED and preserves original text."""
    sug = AISuggestionDTO(
        id="sug-1",
        category="BULLET_REWRITE",
        target_section="EXPERIENCE",
        current_issue="Passive phrase",
        why_it_matters="Agency",
        current_text="Responsible for internal tools.",
        recommended_text="Spearheaded internal tools development, saving [X] hours/week.",
        evidence_required_from_candidate="Verify hours saved.",
        status="PENDING",
        original_content="Responsible for internal tools.",
        original_preserved=True
    )

    success, updated, msg = resume_ai_service.apply_candidate_action(sug, "ACCEPT")

    assert success is True
    assert updated.status == "ACCEPTED"
    assert updated.original_content == "Responsible for internal tools."
    assert updated.original_preserved is True
    assert "Original resume content preserved" in msg


def test_candidate_approval_workflow_reject():
    """Verifies that rejecting a suggestion marks status REJECTED and leaves original text unchanged."""
    sug = AISuggestionDTO(
        id="sug-2",
        category="BULLET_REWRITE",
        target_section="EXPERIENCE",
        current_issue="Passive phrase",
        why_it_matters="Agency",
        current_text="Assisted in database maintenance.",
        recommended_text="Automated database maintenance tasks.",
        evidence_required_from_candidate="Confirm automation scope.",
        status="PENDING",
        original_content="Assisted in database maintenance.",
        original_preserved=True
    )

    success, updated, msg = resume_ai_service.apply_candidate_action(sug, "REJECT")

    assert success is True
    assert updated.status == "REJECTED"
    assert updated.original_preserved is True
    assert "dismissed" in msg


def test_candidate_approval_workflow_edit():
    """Verifies that candidate can edit the suggestion text and track custom modifications."""
    sug = AISuggestionDTO(
        id="sug-3",
        category="BULLET_REWRITE",
        target_section="EXPERIENCE",
        current_issue="Passive phrase",
        why_it_matters="Agency",
        current_text="Worked on API endpoints.",
        recommended_text="Architected high-throughput API endpoints.",
        evidence_required_from_candidate="Verify scale.",
        status="PENDING",
        original_content="Worked on API endpoints.",
        original_preserved=True
    )

    custom_text = "Architected 12 core REST API endpoints serving 500k monthly active users."
    success, updated, msg = resume_ai_service.apply_candidate_action(sug, "EDIT", edited_text=custom_text)

    assert success is True
    assert updated.status == "EDITED"
    assert updated.edited_content == custom_text
    assert updated.recommended_text == custom_text
    assert updated.original_content == "Worked on API endpoints."
    assert updated.original_preserved is True


def test_candidate_approval_workflow_empty_edit_fails():
    """Verifies that submitting an empty candidate edit is rejected with informative message."""
    sug = AISuggestionDTO(
        id="sug-4",
        category="BULLET_REWRITE",
        target_section="EXPERIENCE",
        current_issue="Issue",
        why_it_matters="Why",
        recommended_text="Rec",
        evidence_required_from_candidate="Evidence",
        status="PENDING"
    )

    success, _, msg = resume_ai_service.apply_candidate_action(sug, "EDIT", edited_text="   ")
    assert success is False
    assert "cannot be empty" in msg


@pytest.mark.asyncio
async def test_gemini_unavailable_fallback():
    """Verifies safe fallback to deterministic heuristics when Gemini is unavailable or times out."""
    extractions = {
        "summary": None,
        "experience": [
            {
                "company": "BetaTech",
                "responsibilities": ["Responsible for bug fixing."]
            }
        ],
        "projects": []
    }

    # Simulate network timeout / error during Gemini invocation
    with patch("httpx.AsyncClient.post", side_effect=Exception("API connection timeout")):
        report = await resume_ai_service.generate_suggestions("res-999", "ver-999", extractions)

    assert report.provider_used == "DETERMINISTIC_HEURISTIC"
    assert len(report.suggestions) > 0
    assert report.suggestions[0].evidence_required_from_candidate != ""
