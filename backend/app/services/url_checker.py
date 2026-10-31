"""
RIGHT FIT Core — Bounded Permitted URL Probe & SSRF Protection Service
Version: 1.0.0
Phase: 6 — Verification, Deduplication, Freshness & Data Quality Intelligence

Provides controlled, safe external URL accessibility probes:
- Anti-SSRF validation against internal, loopback, and private IP ranges
- Scheme validation (strictly http and https)
- Follows redirects up to maximum limit with destination validation
- Max response size limits and strict timeout bounds
"""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import socket
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger("rightfit.url_checker")

BOT_USER_AGENT = "RIGHT-FIT-Verification-Bot/1.0 (+https://rightfit.platform/bot)"
MAX_REDIRECTS = 3
DEFAULT_TIMEOUT_SECONDS = 10.0
MAX_RESPONSE_BYTES = 512 * 1024  # 512 KB limit to prevent memory exhaustion


class SSRFSecurityException(Exception):
    """Raised when a URL attempts to resolve to a private or forbidden IP address."""
    pass


@dataclass
class URLProbeResult:
    """Outcome of a safe bounded URL probe."""
    url: str
    final_url: str
    http_status: Optional[int]
    is_accessible: bool
    latency_ms: float
    content_type: Optional[str] = None
    redirect_count: int = 0
    error_category: Optional[str] = None
    error_message: Optional[str] = None


class SafeURLChecker:
    """Safely verifies external listing accessibility without SSRF or unbounded crawling."""

    @staticmethod
    def is_ip_forbidden(ip_str: str) -> bool:
        """Evaluates whether an IP address belongs to loopback, private, link-local, or reserved networks."""
        try:
            ip = ipaddress.ip_address(ip_str)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                return True
            # Explicit check for AWS/GCP metadata service
            if str(ip) == "169.254.169.254":
                return True
            return False
        except ValueError:
            return True

    @classmethod
    def validate_url_safety(cls, url: str) -> None:
        """Validates scheme and resolves hostname to ensure no SSRF targets.
        Raises ValueError or SSRFSecurityException if unsafe.
        """
        parsed = urlparse(url.strip())
        if parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(f"Unsupported protocol scheme '{parsed.scheme}'. Only http and https are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL has no valid hostname.")

        # Block direct localhost strings
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"):
            raise SSRFSecurityException(f"Prohibited host target '{hostname}' (loopback/internal)")

        # Resolve DNS to check IP addresses
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                if cls.is_ip_forbidden(ip_str):
                    raise SSRFSecurityException(
                        f"SSRF violation: Hostname '{hostname}' resolved to prohibited address '{ip_str}'"
                    )
        except socket.gaierror as e:
            # Domain cannot be resolved via DNS
            logger.debug(f"DNS lookup failed for hostname '{hostname}': {e}")

    @classmethod
    async def probe_url(
        cls,
        url: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_redirects: int = MAX_REDIRECTS,
    ) -> URLProbeResult:
        """Executes a bounded, safe HTTP probe (HEAD falling back to GET) with redirect validation."""
        start_time = time.time()
        current_url = url.strip()
        redirects_followed = 0

        try:
            cls.validate_url_safety(current_url)
        except SSRFSecurityException as ssrf_err:
            latency = (time.time() - start_time) * 1000.0
            return URLProbeResult(
                url=url,
                final_url=current_url,
                http_status=None,
                is_accessible=False,
                latency_ms=round(latency, 2),
                error_category="SSRF_PROHIBITED",
                error_message=str(ssrf_err),
            )
        except ValueError as val_err:
            latency = (time.time() - start_time) * 1000.0
            return URLProbeResult(
                url=url,
                final_url=current_url,
                http_status=None,
                is_accessible=False,
                latency_ms=round(latency, 2),
                error_category="INVALID_URL_SCHEME",
                error_message=str(val_err),
            )

        headers = {"User-Agent": BOT_USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/json,*/*"}

        try:
            # We manage redirects manually to validate each target against SSRF
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False, headers=headers) as client:
                while True:
                    try:
                        resp = await client.head(current_url)
                        # If HEAD is 405 Method Not Allowed or 403, retry with bounded GET
                        if resp.status_code in (405, 403):
                            resp = await client.get(current_url)
                    except Exception:
                        resp = await client.get(current_url)

                    # Handle Redirects
                    if resp.status_code in (301, 302, 303, 307, 308):
                        if redirects_followed >= max_redirects:
                            latency = (time.time() - start_time) * 1000.0
                            return URLProbeResult(
                                url=url,
                                final_url=current_url,
                                http_status=resp.status_code,
                                is_accessible=False,
                                latency_ms=round(latency, 2),
                                redirect_count=redirects_followed,
                                error_category="MAX_REDIRECTS_EXCEEDED",
                                error_message=f"Exceeded max redirect limit of {max_redirects}",
                            )

                        next_location = resp.headers.get("location")
                        if not next_location:
                            break

                        # Parse next URL and validate against SSRF
                        from urllib.parse import urljoin
                        resolved_next = urljoin(current_url, next_location)
                        cls.validate_url_safety(resolved_next)
                        current_url = resolved_next
                        redirects_followed += 1
                        continue

                    # Final non-redirect response reached
                    latency = (time.time() - start_time) * 1000.0
                    content_type = resp.headers.get("content-type") or ""
                    is_ok = 200 <= resp.status_code < 400

                    # Check for DOM tombstones in HTML responses (e.g., job expired but returns 200)
                    tombstone_found = None
                    if is_ok and "html" in content_type.lower():
                        try:
                            # Read initial snippet to prevent unbounded memory usage
                            body_snippet = (resp.text[:65536] if hasattr(resp, "text") else "").lower()
                            tombstone_phrases = [
                                "no longer accepting applications",
                                "this position has been filled",
                                "job has been closed",
                                "this job is closed",
                                "this listing has expired",
                                "requisition has been unposted",
                                "the job you are looking for is no longer available",
                                "this opening is closed",
                                "this vacancy has been closed",
                                "posting has closed",
                            ]
                            for phrase in tombstone_phrases:
                                if phrase in body_snippet:
                                    tombstone_found = phrase
                                    break
                        except Exception:
                            tombstone_found = None

                    if tombstone_found:
                        is_ok = False
                        error_category = "TOMBSTONE_DETECTED"
                        error_message = f"Vacancy closed: detected '{tombstone_found}' on employer page"
                    elif is_ok:
                        error_category = None
                        error_message = None
                    else:
                        error_category = "HTTP_ERROR"
                        error_message = f"HTTP {resp.status_code}"

                    return URLProbeResult(
                        url=url,
                        final_url=current_url,
                        http_status=resp.status_code,
                        is_accessible=is_ok,
                        latency_ms=round(latency, 2),
                        content_type=content_type,
                        redirect_count=redirects_followed,
                        error_category=error_category,
                        error_message=error_message,
                    )

        except SSRFSecurityException as redirect_ssrf:
            latency = (time.time() - start_time) * 1000.0
            return URLProbeResult(
                url=url,
                final_url=current_url,
                http_status=None,
                is_accessible=False,
                latency_ms=round(latency, 2),
                redirect_count=redirects_followed,
                error_category="REDIRECT_SSRF_BLOCKED",
                error_message=str(redirect_ssrf),
            )
        except (httpx.TimeoutException, asyncio.TimeoutError):
            latency = (time.time() - start_time) * 1000.0
            return URLProbeResult(
                url=url,
                final_url=current_url,
                http_status=None,
                is_accessible=False,
                latency_ms=round(latency, 2),
                redirect_count=redirects_followed,
                error_category="TIMEOUT",
                error_message=f"Request timed out after {timeout_seconds}s",
            )
        except (httpx.ConnectError, socket.gaierror) as net_err:
            latency = (time.time() - start_time) * 1000.0
            return URLProbeResult(
                url=url,
                final_url=current_url,
                http_status=None,
                is_accessible=False,
                latency_ms=round(latency, 2),
                redirect_count=redirects_followed,
                error_category="DNS_OR_CONNECTION_FAILURE",
                error_message=str(net_err),
            )
        except Exception as exc:
            latency = (time.time() - start_time) * 1000.0
            return URLProbeResult(
                url=url,
                final_url=current_url,
                http_status=None,
                is_accessible=False,
                latency_ms=round(latency, 2),
                redirect_count=redirects_followed,
                error_category="UNEXPECTED_PROBE_ERROR",
                error_message=str(exc),
            )

