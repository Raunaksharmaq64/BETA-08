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
        r"^email@", r"^user@", r"^domain@", r"^test@", r"^you@",
        r"@domain\.com$", r"@example\.com$", r"wixpress\.com$", r"wordpress\.org$",
        r"sentry\.io$", r"cloudflare\.com$",
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
            resp = safe_request(target, method="GET", headers=headers, timeout=5.0, max_bytes=2 * 1024 * 1024, verify_ssl=False)
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
    def scrape_socials_from_html(cls, html_content: str) -> Dict[str, str]:
        """
        Extract public social media links (Instagram, Facebook, LinkedIn, Twitter/X) from webpage HTML.
        Filters out sharing widgets, legal policies, and generic intent links.
        """
        socials: Dict[str, str] = {
            "instagram": "",
            "facebook": "",
            "linkedin": "",
            "twitter": "",
        }
        if not html_content:
            return socials

        # Instagram
        insta_matches = re.findall(
            r'href=["\'](https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_\-\.]+/?)[^"\']*["\']',
            html_content,
            re.IGNORECASE,
        )
        for link in insta_matches:
            lower = link.lower()
            if not any(x in lower for x in ["/p/", "/tags/", "/explore/", "/reel/", "/directory/", "/accounts/"]):
                socials["instagram"] = link
                break

        # Facebook
        fb_matches = re.findall(
            r'href=["\'](https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_\-\./]+)[^"\']*["\']',
            html_content,
            re.IGNORECASE,
        )
        for link in fb_matches:
            lower = link.lower()
            if not any(x in lower for x in ["/sharer/", "/policies/", "/groups/", "/events/", "/post/", "/dialog/"]):
                socials["facebook"] = link
                break

        # LinkedIn
        li_matches = re.findall(
            r'href=["\'](https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_\-\./]+)[^"\']*["\']',
            html_content,
            re.IGNORECASE,
        )
        for link in li_matches:
            lower = link.lower()
            if not any(x in lower for x in ["/shareArticle", "/sharing/", "/pulse/"]):
                socials["linkedin"] = link
                break

        # Twitter / X
        tw_matches = re.findall(
            r'href=["\'](https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_\-\.]+/?)[^"\']*["\']',
            html_content,
            re.IGNORECASE,
        )
        for link in tw_matches:
            lower = link.lower()
            if not any(x in lower for x in ["/intent/", "/share", "/hashtag/", "/search"]):
                socials["twitter"] = link
                break

        return socials

    @classmethod
    def deep_scrape_socials(cls, main_url: str) -> Dict[str, str]:
        """Crawl homepage and contact pages to locate verified official social profiles."""
        enrichment = cls.deep_enrich_contacts(main_url)
        return enrichment.get("socials", {"instagram": "", "facebook": "", "linkedin": "", "twitter": ""})

    @classmethod
    def deep_enrich_contacts(cls, main_url: str) -> Dict[str, Any]:
        """
        Unified multi-signal contact extraction:
        Crawls homepage and top contact links in a single pass to discover:
        - Primary public business email
        - List of candidate emails
        - Official social profiles (Instagram, Facebook, LinkedIn, Twitter/X)
        """
        result: Dict[str, Any] = {
            "email": "",
            "emails": [],
            "socials": {
                "instagram": "",
                "facebook": "",
                "linkedin": "",
                "twitter": "",
            },
        }
        if not main_url:
            return result

        target = main_url.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        try:
            resp = safe_request(target, method="GET", headers=headers, timeout=5.0, max_bytes=2 * 1024 * 1024, verify_ssl=False)
            html = resp.text

            # 1. Extract from homepage
            emails = cls.scrape_emails_from_html(html)
            socials = cls.scrape_socials_from_html(html)

            result["emails"] = emails
            if emails:
                result["email"] = emails[0]
            result["socials"] = socials

            # 2. Check contact pages if email or socials are incomplete
            missing_socials = not all(result["socials"].values())
            if not result["email"] or missing_socials:
                contact_links = cls.find_contact_links(target, html)
                for c_url in contact_links:
                    try:
                        c_resp = safe_request(c_url, method="GET", headers=headers, timeout=5.0, max_bytes=2 * 1024 * 1024, verify_ssl=False)
                        c_html = c_resp.text

                        # If email was missing, extract
                        if not result["email"]:
                            c_emails = cls.scrape_emails_from_html(c_html)
                            if c_emails:
                                result["email"] = c_emails[0]
                                for em in c_emails:
                                    if em not in result["emails"]:
                                        result["emails"].append(em)

                        # If any social was missing, extract
                        c_socials = cls.scrape_socials_from_html(c_html)
                        for key, val in c_socials.items():
                            if not result["socials"].get(key) and val:
                                result["socials"][key] = val
                    except Exception:
                        continue

        except Exception as e:
            logger.debug(f"[EmailScraper] Deep contact enrichment error for {main_url}: {e}")

        return result

    @classmethod
    def deep_scrape_business_emails(cls, main_url: str) -> str:
        """Crawls home page and contact links, returning best discovered public email."""
        enrichment = cls.deep_enrich_contacts(main_url)
        return enrichment.get("email", "")
