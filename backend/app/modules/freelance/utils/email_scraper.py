"""
Email Scraper — Public business email extraction with SSRF security and contact page crawling.
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional
import urllib.parse

from app.modules.freelance.utils.ssrf_guard import is_safe_url, safe_request

logger = logging.getLogger(__name__)


class EmailScraper:
    """Robust extractor of public business emails from websites."""

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    EXCLUDE_PATTERNS = [
        r"\.png$", r"\.jpg$", r"\.jpeg$", r"\.gif$", r"\.svg$", r"\.webp$",
        r"\.css$", r"\.js$", r"\.mp4$", r"\.woff$", r"\.woff2$", r"\.ttf$",
        r"^sentry@", r"^bootstrap@", r"^jquery@", r"^example@", r"^yourname@",
        r"^email@", r"^user@", r"^domain@", r"^test@",
    ]

    CONTACT_PAGE_KEYWORDS = ["contact", "about", "connect", "reach-us", "get-in-touch"]

    @classmethod
    def clean_email(cls, email: str) -> str:
        cleaned = email.strip().lower()
        if cleaned.endswith((".", ",", ";", ":")):
            cleaned = cleaned[:-1]
        return cleaned

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        cleaned = cls.clean_email(email)
        for pattern in cls.EXCLUDE_PATTERNS:
            if re.search(pattern, cleaned):
                return False
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", cleaned):
            return False
        return True

    @classmethod
    def scrape_emails_from_html(cls, html_content: str) -> List[str]:
        if not html_content:
            return []
        # Decode common email obfuscations
        decoded = re.sub(r"\s*[\(\[]\s*at\s*[\)\]]\s*", "@", html_content, flags=re.IGNORECASE)
        decoded = re.sub(r"\s*[\(\[]\s*dot\s*[\)\]]\s*", ".", decoded, flags=re.IGNORECASE)

        found = re.findall(cls.EMAIL_REGEX, decoded)
        valid: List[str] = []
        for e in found:
            cleaned = cls.clean_email(e)
            if cls.is_valid_email(cleaned) and cleaned not in valid:
                valid.append(cleaned)
        return valid

    @classmethod
    def scrape_url(cls, url: str) -> List[str]:
        if not url:
            return []
        target = url.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        try:
            resp = safe_request(target, method="GET", headers=headers, timeout=5.0, max_bytes=2 * 1024 * 1024)
            return cls.scrape_emails_from_html(resp.text)
        except Exception as e:
            logger.debug(f"[EmailScraper] Failed to scrape {target}: {e}")
            return []

    @classmethod
    def find_contact_links(cls, base_url: str, html: str) -> List[str]:
        """Discover contact or about page links from homepage HTML."""
        links: List[str] = []
        parsed_base = urllib.parse.urlparse(base_url)
        base_domain = parsed_base.netloc.lower()

        href_matches = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html, flags=re.IGNORECASE)
        for href in href_matches:
            href_lower = href.lower()
            if any(k in href_lower for k in cls.CONTACT_PAGE_KEYWORDS):
                full_url = urllib.parse.urljoin(base_url, href)
                parsed = urllib.parse.urlparse(full_url)
                if parsed.netloc.lower() == base_domain and full_url not in links:
                    links.append(full_url)
            if len(links) >= 3:
                break
        return links

    @classmethod
    def deep_scrape_business_emails(cls, main_url: str) -> str:
        """Crawls home page and contact links, returning best discovered public email."""
        if not main_url:
            return ""

        target = main_url.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        try:
            resp = safe_request(target, method="GET", headers=headers, timeout=5.0, max_bytes=2 * 1024 * 1024)
            html = resp.text
            emails = cls.scrape_emails_from_html(html)
            if emails:
                return emails[0]

            contact_links = cls.find_contact_links(target, html)
            for c_url in contact_links:
                c_emails = cls.scrape_url(c_url)
                if c_emails:
                    return c_emails[0]
        except Exception as e:
            logger.debug(f"[EmailScraper] Deep scrape error for {main_url}: {e}")

        return ""
