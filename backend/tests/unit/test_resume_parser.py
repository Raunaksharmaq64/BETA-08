"""
Unit tests for ResumeParserService.
Verifies PDF, DOCX parsing, section classification, evidenced entity extraction, and error handling.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from pathlib import Path
import pytest

from app.services.resume_parser_service import (
    ParsingError,
    ResumeParserService,
    resume_parser_service,
)
from contracts.resume.schemas import ConfidenceLevel, ReviewStatus

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_resumes"


def test_standard_one_page_pdf_parsing():
    """Verifies complete parsing pipeline on a standard 1-page PDF."""
    pdf_path = FIXTURES_DIR / "standard_one_page.pdf"
    assert pdf_path.exists(), "Standard PDF fixture must exist"

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    raw_text, extractions, evidence_list = resume_parser_service.parse_document(file_bytes, "pdf")

    # 1. Text & Sections
    assert "JANE DOE" in raw_text
    assert "TechCorp Solutions" in raw_text
    assert len(extractions["sections"]) >= 4

    # 2. Contact Information
    contact = extractions["personal_info"]
    assert contact["email"] == "jane.doe@example.com"
    assert "123-4567" in contact["phone"]
    assert "linkedin.com/in/janedoe" in contact["linkedin_url"]
    assert "github.com/janedoe" in contact["github_url"]

    # 3. Education
    edu = extractions["education"]
    assert len(edu) >= 1
    assert "Stanford" in edu[0]["institution"]
    assert "2014" in edu[0]["start_date"] or "2018" in edu[0]["end_date"]

    # 4. Experience
    exp = extractions["experience"]
    assert len(exp) >= 1
    assert any("TechCorp" in e["company"] for e in exp)

    # 5. Skills
    skills = extractions["skills"]
    assert "languages" in skills
    languages_names = [s["name"].lower() for s in skills["languages"]]
    assert "python" in languages_names
    assert "go" in languages_names

    frameworks_names = [s["name"].lower() for s in skills["frameworks"]]
    assert "fastapi" in frameworks_names
    assert "react" in frameworks_names

    # 6. Evidence Items
    assert len(evidence_list) >= 8
    for ev in evidence_list:
        assert ev.field_id is not None
        assert ev.field_name
        assert ev.excerpt
        assert ev.confidence_score >= 0.70
        assert ev.review_status == ReviewStatus.PENDING
        assert ev.confidence_level in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM)


def test_multi_page_pdf_page_partitioning():
    """Verifies that multi-page documents track page numbers correctly in evidence."""
    pdf_path = FIXTURES_DIR / "multi_page.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    raw_text, extractions, evidence_list = resume_parser_service.parse_document(file_bytes, "pdf")

    assert "--- Page 1 ---" in raw_text
    assert "--- Page 2 ---" in raw_text

    # Check that evidence has page numbers
    page_numbers = {ev.page_number for ev in evidence_list if ev.page_number is not None}
    assert 1 in page_numbers
    assert 2 in page_numbers


def test_docx_document_parsing():
    """Verifies extraction from DOCX paragraphs and tables."""
    docx_path = FIXTURES_DIR / "standard_resume.docx"
    with open(docx_path, "rb") as f:
        file_bytes = f.read()

    raw_text, extractions, evidence_list = resume_parser_service.parse_document(file_bytes, "docx")

    assert "EMILY DAVIS" in raw_text
    assert "emily.davis@example.org" in extractions["personal_info"]["email"]
    assert "github.com/emilydavis" in extractions["personal_info"]["github_url"]
    assert len(extractions["education"]) >= 1
    assert "Michigan" in extractions["education"][0]["institution"]

    # Check skills extracted from table
    skills = extractions["skills"]
    all_skill_names = [
        item["name"].lower()
        for cat in skills.values()
        for item in cat
    ]
    assert "python" in all_skill_names
    assert "fastapi" in all_skill_names


def test_no_fabrication_when_sections_missing():
    """Verifies that missing resume sections produce empty lists and never invent data."""
    pdf_path = FIXTURES_DIR / "missing_sections.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    _, extractions, evidence_list = resume_parser_service.parse_document(file_bytes, "pdf")

    # Missing summary, projects, certifications
    assert extractions["summary"] is None
    assert extractions["projects"] == []
    assert extractions["certifications"] == []

    # Evidence list should NOT have any project or certification items
    evidence_fields = [ev.field_name for ev in evidence_list]
    assert not any(f.startswith("projects") for f in evidence_fields)
    assert not any(f.startswith("certifications") for f in evidence_fields)


def test_password_protected_pdf_rejection():
    """Verifies that password-encrypted PDFs raise informative ParsingError."""
    pdf_path = FIXTURES_DIR / "password_protected.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    with pytest.raises(ParsingError) as exc_info:
        resume_parser_service.parse_document(file_bytes, "pdf")

    assert "Password-protected" in str(exc_info.value)


def test_corrupted_pdf_rejection():
    """Verifies that malformed PDF bytes raise ParsingError."""
    pdf_path = FIXTURES_DIR / "corrupted.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    with pytest.raises(ParsingError):
        resume_parser_service.parse_document(file_bytes, "pdf")


def test_empty_pdf_rejection():
    """Verifies that PDFs with no text raise ParsingError."""
    pdf_path = FIXTURES_DIR / "empty.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    with pytest.raises(ParsingError) as exc_info:
        resume_parser_service.parse_document(file_bytes, "pdf")

    assert "No extractable text" in str(exc_info.value)


def test_corrupted_docx_rejection():
    """Verifies that malformed DOCX bytes raise ParsingError."""
    docx_path = FIXTURES_DIR / "corrupted_resume.docx"
    with open(docx_path, "rb") as f:
        file_bytes = f.read()

    with pytest.raises(ParsingError):
        resume_parser_service.parse_document(file_bytes, "docx")

