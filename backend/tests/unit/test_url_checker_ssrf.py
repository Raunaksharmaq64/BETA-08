"""
Unit Tests: Bounded Permitted URL Checker & SSRF Protection
Phase 6: Verification, Deduplication, Freshness & Data Quality Intelligence
"""

import pytest
from app.services.url_checker import SafeURLChecker, SSRFSecurityException


def test_ssrf_blocks_private_and_loopback_ips():
    """Verify is_ip_forbidden identifies loopback, internal, and metadata addresses."""
    # Loopback
    assert SafeURLChecker.is_ip_forbidden("127.0.0.1") is True
    assert SafeURLChecker.is_ip_forbidden("127.0.0.2") is True
    assert SafeURLChecker.is_ip_forbidden("::1") is True

    # RFC 1918 Private Ranges
    assert SafeURLChecker.is_ip_forbidden("10.0.0.1") is True
    assert SafeURLChecker.is_ip_forbidden("172.16.0.5") is True
    assert SafeURLChecker.is_ip_forbidden("192.168.1.1") is True

    # Cloud Metadata (AWS / GCP / Azure)
    assert SafeURLChecker.is_ip_forbidden("169.254.169.254") is True

    # Valid Public IP
    assert SafeURLChecker.is_ip_forbidden("8.8.8.8") is False
    assert SafeURLChecker.is_ip_forbidden("93.184.216.34") is False


def test_ssrf_blocks_forbidden_schemes():
    """Verify validate_url_safety rejects non-http/https schemes."""
    with pytest.raises(ValueError, match="Unsupported protocol scheme"):
        SafeURLChecker.validate_url_safety("file:///etc/passwd")

    with pytest.raises(ValueError, match="Unsupported protocol scheme"):
        SafeURLChecker.validate_url_safety("ftp://example.com/job")

    with pytest.raises(ValueError, match="Unsupported protocol scheme"):
        SafeURLChecker.validate_url_safety("javascript:alert(1)")


def test_ssrf_blocks_local_hostnames():
    """Verify validate_url_safety rejects localhost, loopback, and cloud metadata hostnames."""
    with pytest.raises(SSRFSecurityException, match="Prohibited host target"):
        SafeURLChecker.validate_url_safety("http://localhost/api")

    with pytest.raises(SSRFSecurityException, match="Prohibited host target"):
        SafeURLChecker.validate_url_safety("http://127.0.0.1/admin")

    with pytest.raises(SSRFSecurityException, match="Prohibited host target"):
        SafeURLChecker.validate_url_safety("http://metadata.google.internal/computeMetadata")


def test_ssrf_allows_valid_public_https_url():
    """Verify validate_url_safety accepts standard HTTPS public job board URLs without raising exceptions."""
    # Should not raise any exception
    SafeURLChecker.validate_url_safety("https://boards.greenhouse.io/acme/jobs/12345")
