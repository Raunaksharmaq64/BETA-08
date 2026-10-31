"""
Website Auditor — SEO, performance, mobile responsiveness, and SSL technical health analyzer.
"""

from __future__ import annotations

from html.parser import HTMLParser
import logging
import time
from typing import Any, Dict, List
import urllib.parse

from app.modules.freelance.utils.ssrf_guard import is_safe_url, safe_request

logger = logging.getLogger(__name__)


class AuditHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.has_viewport = False
        self.h1_count = 0
        self.total_images = 0
        self.images_with_alt = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = {name.lower(): value for name, value in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif name == "viewport":
                self.has_viewport = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "img":
            self.total_images += 1
            if "alt" in attrs_dict and attrs_dict["alt"] and attrs_dict["alt"].strip():
                self.images_with_alt += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def audit_website(url: str) -> Dict[str, Any]:
    """
    Perform a comprehensive technical audit of a business website.
    Returns 100-point category scorecards and actionable recommendations.
    """
    if not url:
        return {
            "overall_score": 0,
            "status": "UNREACHABLE",
            "scores": {"speed": 0, "seo": 0, "mobile": 0, "ssl": 0, "alt": 0},
            "recommendations": [{"category": "General", "title": "No Website Listed", "description": "Business lacks a digital presence.", "severity": "HIGH"}],
        }

    target_url = url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    start_time = time.time()
    try:
        resp = safe_request(target_url, method="GET", headers=headers, timeout=6.0, max_bytes=2 * 1024 * 1024)
        response_time = time.time() - start_time
        html_content = resp.text
        is_ssl = resp.url.startswith("https://")
    except Exception as e:
        logger.warning(f"[WebsiteAuditor] Failed to fetch {target_url}: {e}")
        return {
            "overall_score": 15,
            "status": "BROKEN",
            "scores": {"speed": 10, "seo": 10, "mobile": 20, "ssl": 0, "alt": 0},
            "recommendations": [
                {
                    "category": "DNS & Uptime",
                    "title": "Website Down / Broken Host",
                    "description": f"Domain failed connection or health checks: {str(e)[:100]}",
                    "severity": "CRITICAL",
                }
            ],
            "response_time": 9.99,
        }

    # Speed Score (0-100)
    # < 1.0s: 100, 1.0-2.5s: 80, 2.5-4.0s: 60, > 4.0s: 30
    if response_time < 1.0:
        speed_score = 100
    elif response_time < 2.5:
        speed_score = 80
    elif response_time < 4.0:
        speed_score = 60
    else:
        speed_score = 30

    parser = AuditHTMLParser()
    try:
        parser.feed(html_content)
    except Exception:
        pass

    # SEO Score (Title, Meta Description, H1)
    seo_points = 0
    recommendations: List[Dict[str, str]] = []

    if parser.title and len(parser.title.strip()) > 10:
        seo_points += 40
    else:
        recommendations.append({
            "category": "SEO",
            "title": "Missing or Short Title Tag",
            "description": "Page title should clearly define business services and target location.",
            "severity": "HIGH",
        })

    if parser.meta_description and len(parser.meta_description.strip()) > 30:
        seo_points += 35
    else:
        recommendations.append({
            "category": "SEO",
            "title": "Missing Meta Description",
            "description": "Meta description helps searchers understand your offering before clicking.",
            "severity": "MEDIUM",
        })

    if parser.h1_count == 1:
        seo_points += 25
    elif parser.h1_count > 1:
        seo_points += 15
        recommendations.append({
            "category": "SEO",
            "title": "Multiple H1 Headings Found",
            "description": "Page should have exactly one clear H1 heading.",
            "severity": "LOW",
        })
    else:
        recommendations.append({
            "category": "SEO",
            "title": "Missing Primary H1 Heading",
            "description": "Add a prominent H1 tag containing core business keywords.",
            "severity": "HIGH",
        })

    # Mobile Responsiveness Score
    mobile_score = 100 if parser.has_viewport else 20
    if not parser.has_viewport:
        recommendations.append({
            "category": "Mobile",
            "title": "Missing Viewport Meta Tag",
            "description": "Site does not scale for mobile devices; customers will see tiny desktop text.",
            "severity": "CRITICAL",
        })

    # SSL Score
    ssl_score = 100 if is_ssl else 0
    if not is_ssl:
        recommendations.append({
            "category": "Security",
            "title": "Missing SSL Certificate (HTTP)",
            "description": "Browsers flag site as 'Not Secure', turning away customers.",
            "severity": "HIGH",
        })

    # Image Alt Score
    if parser.total_images == 0:
        alt_score = 100
    else:
        ratio = parser.images_with_alt / parser.total_images
        alt_score = int(ratio * 100)
        if ratio < 0.6:
            recommendations.append({
                "category": "Accessibility & SEO",
                "title": f"Missing Alt Tags ({parser.total_images - parser.images_with_alt} images)",
                "description": "Add descriptive alt attributes to product and showcase images.",
                "severity": "LOW",
            })

    # Overall Score (Weighted)
    overall_score = int(
        (speed_score * 0.25)
        + (seo_points * 0.25)
        + (mobile_score * 0.25)
        + (ssl_score * 0.15)
        + (alt_score * 0.10)
    )

    return {
        "overall_score": overall_score,
        "status": "ANALYZED",
        "response_time": round(response_time, 2),
        "scores": {
            "speed": speed_score,
            "seo": seo_points,
            "mobile": mobile_score,
            "ssl": ssl_score,
            "alt": alt_score,
        },
        "details": {
            "title": parser.title.strip(),
            "meta_description": parser.meta_description.strip(),
            "h1_count": parser.h1_count,
            "total_images": parser.total_images,
            "images_with_alt": parser.images_with_alt,
            "has_viewport": parser.has_viewport,
            "is_ssl": is_ssl,
        },
        "recommendations": recommendations,
    }
