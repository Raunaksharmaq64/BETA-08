"""
Unit tests for Phase 6 — Database & Backend Integration.
Verifies ResumeJobMatchRecord, ResumeAISuggestionActionRecord, and Version Diffing logic.
"""

import pytest
from app.db.models import (
    ResumeJobMatchRecord,
    ResumeAISuggestionActionRecord,
    ResumeExtractionRecord,
    ResumeVersionRecord,
)
from contracts.resume.schemas import ResumeVersionDiffResponse


def test_resume_job_match_record_schema():
    """Verifies ResumeJobMatchRecord columns, types, and instantiation."""
    rec = ResumeJobMatchRecord(
        resume_version_id="ver-123",
        user_id="user-456",
        target_job_title="Staff Backend Engineer",
        target_job_description="Seeking Python and Distributed Systems expert",
        overall_match_score=85.5,
        keyword_coverage_score=0.82,
        required_skills_match_json={"matched": ["python"], "missing": []},
        preferred_skills_match_json={"matched": ["redis"], "missing": []},
        experience_level_match_json={"required_years": 5.0, "detected_years": 6.0},
        project_theme_alignments_json=[{"jd_theme": "python", "score": 1.0}],
        unverified_matches_json=[],
        job_specific_suggestions_json=[]
    )
    assert rec.target_job_title == "Staff Backend Engineer"
    assert rec.overall_match_score == 85.5
    assert rec.keyword_coverage_score == 0.82
    assert rec.required_skills_match_json["matched"] == ["python"]


def test_resume_ai_suggestion_action_record_schema():
    """Verifies ResumeAISuggestionActionRecord columns and candidate action tracking."""
    rec = ResumeAISuggestionActionRecord(
        resume_version_id="ver-123",
        user_id="user-456",
        suggestion_id="sug-789",
        action="EDIT",
        original_text="Worked on APIs",
        suggested_text="Architected FastAPI endpoints processing [X] req/sec",
        edited_text="Architected FastAPI endpoints processing 15,000 req/sec",
        status="APPLIED"
    )
    assert rec.suggestion_id == "sug-789"
    assert rec.action == "EDIT"
    assert "15,000 req/sec" in rec.edited_text
    assert rec.status == "APPLIED"


def test_resume_version_diff_schema():
    """Verifies ResumeVersionDiffResponse contract serialization."""
    diff = ResumeVersionDiffResponse(
        resume_id="res-1",
        version_id_1="v-1",
        version_id_2="v-2",
        version_label_1="v1 - General",
        version_label_2="v2 - Cloud Native",
        character_count_diff=250,
        word_count_diff=45,
        added_skills=["Kubernetes", "Terraform", "Go"],
        removed_skills=["PHP"],
        shared_skills=["Python", "PostgreSQL", "Docker"],
        section_changes={"PUBLICATIONS": "ADDED", "OBJECTIVE": "REMOVED"},
        quality_score_diff={
            "v1_score": 72.0,
            "v2_score": 88.5,
            "score_delta": 16.5,
            "v1_band": "MODERATE",
            "v2_band": "STRONG"
        }
    )
    assert diff.character_count_diff == 250
    assert "Kubernetes" in diff.added_skills
    assert "PHP" in diff.removed_skills
    assert diff.quality_score_diff["score_delta"] == 16.5
    assert diff.quality_score_diff["v2_band"] == "STRONG"

