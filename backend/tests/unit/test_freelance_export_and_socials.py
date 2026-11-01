"""
Unit tests for Freelance Intelligence Socials Scraping & Excel/CSV Export
"""

import io
import pytest
from app.modules.freelance.utils.email_scraper import EmailScraper
from app.modules.freelance.services.export_service import FreelanceExportService


def test_sanitize_spreadsheet_cell_formula_injection_defense():
    """Formulas with =, @, +, -, \\t must be escaped with a leading single quote."""
    malicious = [
        "=cmd|'/C calc'!A1",
        "@SUM(1+1)",
        "+123456789",
        "-5+2",
        "\t=1+1",
    ]
    for cell in malicious:
        sanitized = FreelanceExportService.sanitize_spreadsheet_cell(cell)
        assert sanitized.startswith("'"), f"Failed on {cell}: {sanitized}"
        assert sanitized[1:] == cell

    # Safe strings must not be modified
    assert FreelanceExportService.sanitize_spreadsheet_cell("Dental Clinic") == "Dental Clinic"
    assert FreelanceExportService.sanitize_spreadsheet_cell(4.8) == 4.8
    assert FreelanceExportService.sanitize_spreadsheet_cell(None) == ""


def test_scrape_socials_from_html():
    """HTML with Instagram, Facebook, LinkedIn, Twitter links should be accurately extracted."""
    html = """
    <div>
      <a href="https://instagram.com/local_business/">IG</a>
      <a href="https://facebook.com/localbusinesspage">FB</a>
      <a href="https://linkedin.com/company/localbiz">LI</a>
      <a href="https://x.com/localbiz">X</a>
      <!-- Excluded junk links -->
      <a href="https://facebook.com/sharer/sharer.php?u=abc">Share</a>
      <a href="https://instagram.com/explore/tags/food/">Tag</a>
    </div>
    """
    socials = EmailScraper.scrape_socials_from_html(html)
    assert socials["instagram"] == "https://instagram.com/local_business/"
    assert socials["facebook"] == "https://facebook.com/localbusinesspage"
    assert socials["linkedin"] == "https://linkedin.com/company/localbiz"
    assert socials["twitter"] == "https://x.com/localbiz"


def test_generate_excel_and_csv_from_mock_opportunities():
    """Export service should produce valid Excel (.xlsx) and CSV binary buffers."""
    mock_opps = [
        {
            "business_name": "Metro Healthcare",
            "service_category": "Dentists",
            "city": "Austin, TX",
            "website": "https://metrohealth.com",
            "is_broken_website": False,
            "priority": "HIGH",
            "relevance_score": 95.0,
            "email": "info@metrohealth.com",
            "phone": "+1 512 555 0199",
            "rating": 4.9,
            "reviews_count": 42,
            "instagram": "https://instagram.com/metrohealth",
            "facebook": "https://facebook.com/metrohealth",
            "linkedin": "",
            "twitter": "",
            "suggested_service": "SEO & Performance Rebuild",
            "discovered_at": "2026-10-31 12:00:00",
        }
    ]

    excel_bytes = FreelanceExportService.generate_excel(mock_opps)
    assert len(excel_bytes) > 2000
    assert excel_bytes.startswith(b"PK")  # Standard ZIP/XLSX header signature

    csv_bytes = FreelanceExportService.generate_csv(mock_opps)
    assert len(csv_bytes) > 100
    assert csv_bytes.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM
    decoded = csv_bytes.decode("utf-8-sig")
    assert "Metro Healthcare" in decoded
    assert "info@metrohealth.com" in decoded

