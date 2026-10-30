"""
Unit tests for StorageService.
Verifies magic-byte validation, path traversal defense, file size limits, and isolation.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

import os
from pathlib import Path
import pytest

from app.services.storage_service import StorageSecurityError, StorageService

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_resumes"


def test_sanitize_filename():
    """Verifies filename sanitization prevents path traversal and special characters."""
    assert StorageService.sanitize_filename("../../../etc/passwd") == "passwd"
    assert StorageService.sanitize_filename("my resume (1).pdf") == "my_resume__1_.pdf"
    assert StorageService.sanitize_filename("..\\..\\windows\\system32.dll") == "system32.dll"


def test_magic_byte_validation_pdf():
    """Verifies that PDF magic bytes %PDF- are recognized."""
    pdf_bytes = b"%PDF-1.7\nSample content"
    file_type, mime = StorageService.detect_file_type_and_validate(pdf_bytes, "resume.pdf")
    assert file_type == "pdf"
    assert mime == "application/pdf"


def test_magic_byte_validation_docx():
    """Verifies that DOCX magic bytes PK\\x03\\x04 are recognized."""
    docx_bytes = b"PK\x03\x04\x14\x00\x06\x00Sample"
    file_type, mime = StorageService.detect_file_type_and_validate(docx_bytes, "resume.docx")
    assert file_type == "docx"
    assert "wordprocessingml" in mime


def test_rejection_of_unsupported_executables():
    """Verifies rejection of non-PDF/DOCX binary files."""
    exe_path = FIXTURES_DIR / "malicious.exe"
    with open(exe_path, "rb") as f:
        file_bytes = f.read()

    with pytest.raises(StorageSecurityError) as exc_info:
        StorageService.detect_file_type_and_validate(file_bytes, "malicious.exe")
    assert "Unsupported or malformed" in str(exc_info.value)


def test_file_size_limit_enforcement():
    """Verifies that files exceeding size limits are rejected."""
    # Create fake bytes exceeding 10MB
    oversized_bytes = b"%PDF-" + b"0" * (11 * 1024 * 1024)
    with pytest.raises(StorageSecurityError) as exc_info:
        StorageService.detect_file_type_and_validate(oversized_bytes, "large.pdf")
    assert "File size exceeds" in str(exc_info.value)


def test_path_traversal_on_resolution(tmp_path):
    """Verifies that resolve_secure_path prevents escaping the user's isolated directory."""
    svc = StorageService(base_dir=str(tmp_path))
    user_id = "user_123"

    # Attempt path traversal
    with pytest.raises(StorageSecurityError) as exc_info:
        svc.resolve_secure_path("../other_user/secret.pdf", user_id)
    assert "Access denied" in str(exc_info.value)
