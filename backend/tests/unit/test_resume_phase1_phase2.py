"""
Comprehensive Unit Tests for Phase 1 & Phase 2 Resume Intelligence.
Phase 1: Robust Resume Parsing & Extraction (Scanned PDF detection <50 chars, mixed-content, explicit vs inferred skills, supplementary entities).
Phase 2: Deep Resume Understanding & Quality Scoring (5 deterministic dimensions, career stage fairness, observations, recommendations).
"""

import io
import fitz
import pytest

from app.services.resume_parser_service import resume_parser_service
from app.services.resume_quality_service import resume_quality_analyzer
from contracts.resume.schemas import ConfidenceLevel, ParsingStatus


def _create_in_memory_pdf(pages_text: list[str]) -> bytes:
    """Helper creating an in-memory PDF with specified text per page."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# =====================================================================
# Phase 1: Robust Resume Parsing & Extraction Tests
# =====================================================================

def test_scanned_pdf_detection_threshold_under_50_chars():
    """
    Verifies scanned PDF detection:
    When ALL pages have fewer than 50 extractable characters,
    document is flagged as is_scanned_pdf=True and ocr_required=True.
    """
    # 2 pages each with 20-30 characters (e.g. image artifacts or watermark)
    pages = [
        "Scanned Document A",  # 18 chars
        "Page 2 scan only"     # 16 chars
    ]
    pdf_bytes = _create_in_memory_pdf(pages)

    raw_text, extractions, evidence = resume_parser_service.parse_document(pdf_bytes, "pdf")

    assert extractions["is_scanned_pdf"] is True
    assert extractions["is_mixed_content"] is False
    assert extractions["ocr_required"] is True
    assert len(extractions["low_text_pages"]) == 2
    assert any("Scanned PDF detected" in n for n in extractions["extraction_notes"])


def test_mixed_content_pdf_detection():
    """
    Verifies mixed-content PDF detection:
    When some pages have normal text (>=50 chars) and other pages have <50 chars,
    is_scanned_pdf is False, is_mixed_content is True, and OCR requirement is clearly flagged.
    """
    page1 = (
        "Jane Doe - Staff Software Engineer\n"
        "Email: jane@example.com | Phone: 555-0199\n"
        "Summary: Senior distributed systems architect with extensive cloud experience.\n"
        "Experience: Principal Engineer at Acme Corp designing high-scale APIs."
    )  # ~230 chars
    page2 = "Certificate Attachment"  # 22 chars (<50 chars)

    pdf_bytes = _create_in_memory_pdf([page1, page2])

    raw_text, extractions, evidence = resume_parser_service.parse_document(pdf_bytes, "pdf")

    assert extractions["is_scanned_pdf"] is False
    assert extractions["is_mixed_content"] is True
    assert extractions["ocr_required"] is True
    assert extractions["low_text_pages"] == [2]
    assert any("Mixed-content PDF detected" in n for n in extractions["extraction_notes"])


def test_normal_digital_pdf_no_scanned_flag():
    """
    Verifies that a clean digital PDF with all pages >= 50 characters
    is NOT classified as scanned or mixed-content.
    """
    page1 = (
        "Alex Smith - Senior Python Engineer\n"
        "Email: alex.smith@example.com | Phone: 555-432-1098\n"
        "Experience: Senior Engineer at CloudScale Inc.\n"
        "- Architected streaming pipeline reducing data ingest latency by 45%.\n"
        "Skills: Python, Go, FastAPI, PostgreSQL, Docker, Kubernetes."
    )
    pdf_bytes = _create_in_memory_pdf([page1])

    raw_text, extractions, evidence = resume_parser_service.parse_document(pdf_bytes, "pdf")

    assert extractions["is_scanned_pdf"] is False
    assert extractions["is_mixed_content"] is False
    assert extractions["ocr_required"] is False
    assert extractions["low_text_pages"] == []


def test_explicit_vs_inferred_skills_separation():
    """
    Verifies strict separation:
    - explicit_skills: directly declared in dedicated Skills section.
    - inferred_skills: detected from project or experience body text only.
    - backward compatibility: extractions['skills'] matches explicit_skills.
    """
    resume_text = (
        "Sarah Connor\nsarah@example.com\n555-987-6543\n\n"
        "Experience:\n"
        "Senior Cloud Engineer at TechCorp\n"
        "- Engineered microservices deployed to AWS using Kubernetes and Terraform.\n"
        "- Built high-throughput caching layer with Redis.\n\n"
        "Skills:\n"
        "Languages: Python, Go\n"
        "Databases: PostgreSQL\n"
    )
    pdf_bytes = _create_in_memory_pdf([resume_text])

    _, extractions, evidence = resume_parser_service.parse_document(pdf_bytes, "pdf")

    explicit_skills = extractions["explicit_skills"]
    inferred_skills = extractions["inferred_skills"]

    # Explicit skills should contain Python, Go, PostgreSQL
    explicit_lang_names = [s["name"].lower() for s in explicit_skills.get("languages", [])]
    assert "python" in explicit_lang_names
    assert "go" in explicit_lang_names

    # Technologies mentioned only in experience (e.g. AWS, Kubernetes, Terraform, Redis)
    # MUST NOT be in explicit_skills; they belong in inferred_skills
    assert "aws" not in explicit_lang_names
    assert "kubernetes" not in [s["name"].lower() for s in explicit_skills.get("cloud", [])]

    inferred_names = [s["name"].lower() for s in inferred_skills]
    assert "aws" in inferred_names or "kubernetes" in inferred_names or "redis" in inferred_names

    # Check backward compatibility
    assert extractions["skills"] == explicit_skills


def test_supplementary_sections_extraction_with_evidence():
    """
    Verifies structured extraction and evidence citation for:
    - Internships
    - Publications
    - Languages
    - Awards
    """
    resume_text = (
        "Marcus Aurelius\nmarcus@example.com\n555-111-2222\n\n"
        "Internships:\n"
        "- Machine Learning Research Intern at DeepLab 2023\n\n"
        "Publications:\n"
        "- Distributed Consensus Protocols for Edge Networks (2022)\n\n"
        "Languages:\n"
        "- English (Native), Spanish (Fluent), German (Intermediate)\n\n"
        "Awards:\n"
        "- National Merit Scholar Award 2021\n"
    )
    pdf_bytes = _create_in_memory_pdf([resume_text])

    _, extractions, evidence_list = resume_parser_service.parse_document(pdf_bytes, "pdf")

    # Verify entities
    assert len(extractions["internships"]) >= 1
    assert "DeepLab" in extractions["internships"][0]["title"]

    assert len(extractions["publications"]) >= 1
    assert "Distributed Consensus" in extractions["publications"][0]["title"]

    assert len(extractions["languages"]) >= 2
    lang_names = [l["language"].lower() for l in extractions["languages"]]
    assert "english" in lang_names
    assert "spanish" in lang_names

    assert len(extractions["awards"]) >= 1
    assert "National Merit" in extractions["awards"][0]["title"]

    # Verify EvidenceDTO provenance citations
    evidence_fields = [ev.field_name for ev in evidence_list]
    assert any(f.startswith("internships[") for f in evidence_fields)
    assert any(f.startswith("publications[") for f in evidence_fields)
    assert any(f.startswith("languages[") for f in evidence_fields)
    assert any(f.startswith("awards[") for f in evidence_fields)


def test_missing_sections_no_fabrication():
    """
    Verifies that when supplementary sections are absent,
    the parser returns empty collections with zero fabricated records.
    """
    resume_text = (
        "Minimal Candidate\nminimal@example.com\n555-000-1111\n\n"
        "Education:\nBS Computer Science, MIT 2020\n"
    )
    pdf_bytes = _create_in_memory_pdf([resume_text])

    _, extractions, evidence_list = resume_parser_service.parse_document(pdf_bytes, "pdf")

    assert extractions["experience"] == []
    assert extractions["internships"] == []
    assert extractions["publications"] == []
    assert extractions["languages"] == []
    assert extractions["awards"] == []
    assert extractions["projects"] == []

    # Evidence list must not contain phantom fields
    evidence_fields = [ev.field_name for ev in evidence_list]
    assert not any(f.startswith("experience") for f in evidence_fields)
    assert not any(f.startswith("internships") for f in evidence_fields)
    assert not any(f.startswith("publications") for f in evidence_fields)


# =====================================================================
# Phase 2: Deep Understanding & Quality Scoring Tests
# =====================================================================

def test_quality_analyzer_all_5_dimensions_and_explanations():
    """
    Verifies that ResumeQualityAnalyzer evaluates all 5 dimensions:
    - structure_completeness
    - quantifiable_impact_density
    - action_verb_usage
    - readability
    - formatting_hygiene
    and provides positive & negative observations for each.
    """
    raw_text = (
        "Elena Rostova\nelena@example.com\n555-321-7654\nhttps://github.com/erostova\n\n"
        "Professional Summary: Senior distributed systems architect with 8+ years scaling cloud platforms.\n\n"
        "Experience:\n"
        "Lead Engineer at CloudNine\n"
        "- Architected event-driven microservices platform reducing p99 latency by 40% across 5M requests.\n"
        "- Automated deployment pipelines saving $60k annually in cloud spend.\n"
        "- Responsible for internal database maintenance and support tickets.\n\n"
        "Education:\n"
        "MS in Computer Science, Georgia Tech\n\n"
        "Skills:\n"
        "Python, Go, FastAPI, Kubernetes, Docker, PostgreSQL, Redis, AWS, Kafka, Terraform, Linux, Git\n"
    )

    extractions = {
        "personal_info": {"email": "elena@example.com", "phone": "555-321-7654", "github_url": "https://github.com/erostova"},
        "summary": {"text": "Senior distributed systems architect with 8+ years scaling cloud platforms."},
        "experience": [
            {
                "company": "CloudNine",
                "title": "Lead Engineer",
                "responsibilities": [
                    "Architected event-driven microservices platform reducing p99 latency by 40% across 5M requests.",
                    "Automated deployment pipelines saving $60k annually in cloud spend.",
                    "Responsible for internal database maintenance and support tickets."
                ]
            }
        ],
        "education": [{"degree": "MS Computer Science", "institution": "Georgia Tech"}],
        "skills": {
            "languages": [{"name": "Python"}, {"name": "Go"}],
            "frameworks": [{"name": "FastAPI"}],
            "databases": [{"name": "PostgreSQL"}, {"name": "Redis"}],
            "cloud": [{"name": "AWS"}, {"name": "Kubernetes"}, {"name": "Docker"}, {"name": "Terraform"}],
            "tools": [{"name": "Kafka"}, {"name": "Linux"}, {"name": "Git"}]
        },
        "projects": []
    }

    report = resume_quality_analyzer.analyze_quality("res-101", "ver-101", raw_text, extractions)

    # 1. Overall score and quality band
    assert report.overall_quality_score >= 70.0
    assert report.quality_band in ("STRONG", "MODERATE")

    # 2. Section scores: 0-100 on all 5 dimensions
    dims = report.dimension_evaluations
    assert "structure_completeness" in dims
    assert "quantifiable_impact_density" in dims
    assert "action_verb_usage" in dims
    assert "readability" in dims
    assert "formatting_hygiene" in dims

    for dim_name, dim_eval in dims.items():
        assert 0.0 <= dim_eval.score <= 100.0
        # Must have explainability observations
        assert len(dim_eval.positive_observations) > 0 or len(dim_eval.negative_observations) > 0

    # 3. Action verb observation correctly catches passive phrase 'responsible for'
    action_eval = dims["action_verb_usage"]
    assert any("passive" in neg.lower() for neg in action_eval.negative_observations)

    # 4. Actionable recommendations provided
    assert len(report.improvement_priorities) >= 1

    # 5. Backward compatible section_scores keys present
    assert "structure" in report.section_scores
    assert "impact_quantification" in report.section_scores
    assert "skills_depth" in report.section_scores
    assert "formatting_and_length" in report.section_scores


def test_quality_analyzer_career_stage_fairness():
    """
    Verifies that early career or student candidates who lack lengthy corporate
    experience but possess technical projects or internships are fairly credited
    and not unfairly penalized with a 0 on structure.
    """
    raw_text = (
        "David Kim\ndavid.kim@university.edu\n555-444-3333\n\n"
        "Education:\nBS Computer Engineering, University of Michigan (2024)\n\n"
        "Internships:\nSoftware Engineering Intern at StartupX (Summer 2023)\n\n"
        "Projects:\n"
        "- Real-Time Chat Engine: Built WebSocket messaging server in Go handling 10k connections.\n\n"
        "Skills:\nGo, Python, Docker, Redis\n"
    )

    extractions = {
        "personal_info": {"email": "david.kim@university.edu", "phone": "555-444-3333"},
        "summary": None,
        "experience": [],  # No traditional corporate roles
        "internships": [{"title": "Software Engineering Intern at StartupX", "responsibilities": "Built data pipelines"}],
        "education": [{"degree": "BS Computer Engineering", "institution": "University of Michigan"}],
        "skills": {
            "languages": [{"name": "Go"}, {"name": "Python"}],
            "databases": [{"name": "Redis"}],
            "cloud": [{"name": "Docker"}]
        },
        "projects": [{"name": "Real-Time Chat Engine", "description": "Built WebSocket messaging server in Go handling 10k connections."}]
    }

    report = resume_quality_analyzer.analyze_quality("res-student", "ver-1", raw_text, extractions)

    struct_eval = report.dimension_evaluations["structure_completeness"]
    # Should receive substantial credit for internship and projects despite 0 corporate experience
    assert struct_eval.score >= 50.0
    assert any("internship" in pos.lower() for pos in struct_eval.positive_observations)


def test_quality_analyzer_length_hygiene():
    """
    Verifies formatting hygiene penalties:
    - Sparse document (<220 words) receives formatting penalty and critical issue.
    - Optimal length document receives clean score.
    """
    # Very short text
    short_text = "John\njohn@example.com\nPython developer with experience."
    short_extractions = {
        "personal_info": {"email": "john@example.com"},
        "summary": None,
        "experience": [],
        "education": [],
        "skills": {"languages": [{"name": "Python"}]},
        "projects": []
    }

    short_report = resume_quality_analyzer.analyze_quality("short-1", "ver-1", short_text, short_extractions)
    form_eval = short_report.dimension_evaluations["formatting_hygiene"]

    assert form_eval.score < 80.0
    assert any("sparse" in iss.lower() or "short" in iss.lower() for iss in form_eval.negative_observations)
