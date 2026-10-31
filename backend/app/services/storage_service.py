"""
RIGHT FIT Core — Resume Storage Service
Secure file management, magic-byte validation, and path traversal defense.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Optional, Tuple

from app.core.config import settings

# Regex to strip non-alphanumeric chars from original filenames
_SAFE_FILENAME_RE = re.compile(r"[^a-zA-Z0-9._-]")


class StorageSecurityError(Exception):
    """Raised when file upload violates security, size, or path traversal rules."""
    pass


class StorageService:
    """Manages private disk storage for candidate resume documents."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = Path(base_dir or settings.RESUME_STORAGE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizes user-provided filename preventing path traversal or shell exploits."""
        clean = os.path.basename(filename or "resume.pdf")
        clean = clean.replace("\x00", "").replace("..", "")
        clean = _SAFE_FILENAME_RE.sub("_", clean)
        return clean.strip("._") or "uploaded_resume.pdf"

    @staticmethod
    def detect_file_type_and_validate(file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Validates magic bytes signature and MIME type.
        Returns: (file_type, mime_type) -> e.g. ('pdf', 'application/pdf')
        """
        if not file_bytes:
            raise StorageSecurityError("Uploaded file is empty.")

        if len(file_bytes) > settings.MAX_RESUME_FILE_SIZE_BYTES:
            raise StorageSecurityError(
                f"File size exceeds maximum allowed limit of {settings.MAX_RESUME_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )

        # 1. PDF Magic Bytes: %PDF-
        if file_bytes.startswith(b"%PDF-"):
            return "pdf", "application/pdf"

        # 2. DOCX Magic Bytes: PK\x03\x04 (ZIP format used by OpenXML)
        if file_bytes.startswith(b"PK\x03\x04"):
            # Check if filename ends with docx
            lower_name = filename.lower()
            if lower_name.endswith(".docx"):
                return "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            # It's a zip but not labelled as docx
            raise StorageSecurityError("ZIP archives must be valid .docx documents.")

        raise StorageSecurityError("Unsupported or malformed file type. Only PDF and DOCX documents are accepted.")

    def compute_sha256(self, file_bytes: bytes) -> str:
        """Computes SHA-256 digest for integrity and deduplication."""
        return hashlib.sha256(file_bytes).hexdigest()

    def get_user_dir(self, user_id: str) -> Path:
        """Returns the isolated private directory for a candidate."""
        clean_user_id = os.path.basename(user_id)
        user_dir = (self.base_dir / clean_user_id).resolve()
        # Verify path traversal boundary
        if not str(user_dir).startswith(str(self.base_dir)):
            raise StorageSecurityError("Invalid user directory path.")
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def save_resume_file(
        self,
        user_id: str,
        version_id: str,
        file_bytes: bytes,
        original_filename: str
    ) -> Tuple[str, str, str, int, str]:
        """
        Validates and saves candidate resume to private storage.
        Returns: (storage_path_relative, file_type, mime_type, file_size, file_hash)
        """
        file_type, mime_type = self.detect_file_type_and_validate(file_bytes, original_filename)
        file_hash = self.compute_sha256(file_bytes)
        file_size = len(file_bytes)

        user_dir = self.get_user_dir(user_id)
        stored_filename = f"{version_id}.{file_type}"
        target_path = (user_dir / stored_filename).resolve()

        # Enforce target path is within user directory
        if not str(target_path).startswith(str(user_dir)):
            raise StorageSecurityError("Path traversal attempt detected.")

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        # Store relative storage reference: {user_id}/{version_id}.{ext}
        relative_storage_path = f"{os.path.basename(user_id)}/{stored_filename}"
        return relative_storage_path, file_type, mime_type, file_size, file_hash

    def resolve_secure_path(self, storage_path: str, user_id: str) -> Path:
        """
        Resolves private path with strict ownership and traversal verification.
        """
        clean_user_id = os.path.basename(user_id)
        user_dir = (self.base_dir / clean_user_id).resolve()
        target_path = (self.base_dir / storage_path).resolve()

        if not target_path.exists() or not target_path.is_file():
            # Check fallback locations (e.g. if running from a different working directory)
            potential_bases = [
                Path(__file__).resolve().parent.parent.parent.parent / "storage" / "resumes",
                Path.cwd() / "storage" / "resumes",
                Path.cwd() / "rightFIT" / "storage" / "resumes"
            ]
            for alt_base in potential_bases:
                alt_target = (alt_base / storage_path).resolve()
                if alt_target.exists() and alt_target.is_file():
                    target_path = alt_target
                    user_dir = (alt_base / clean_user_id).resolve()
                    break

        if not str(target_path).startswith(str(user_dir)):
            raise StorageSecurityError("Access denied: File does not belong to candidate.")

        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError("Resume file not found.")

        return target_path

    def read_resume_file(self, storage_path: str, user_id: str) -> bytes:
        """Reads resume file bytes with ownership and traversal protection."""
        target_path = self.resolve_secure_path(storage_path, user_id)
        with open(target_path, "rb") as f:
            return f.read()

    def delete_resume_file(self, storage_path: str, user_id: str) -> bool:
        """Deletes private resume file from disk."""
        try:
            target_path = self.resolve_secure_path(storage_path, user_id)
            if target_path.exists():
                target_path.unlink()
                return True
        except (FileNotFoundError, StorageSecurityError):
            pass
        return False

    def purge_user_storage(self, user_id: str) -> bool:
        """Purges candidate's entire private storage directory upon account deletion."""
        try:
            user_dir = self.get_user_dir(user_id)
            if user_dir.exists() and user_dir.is_dir():
                import shutil
                shutil.rmtree(user_dir, ignore_errors=True)
                return True
        except Exception:
            pass
        return False


# Singleton instance
storage_service = StorageService()
