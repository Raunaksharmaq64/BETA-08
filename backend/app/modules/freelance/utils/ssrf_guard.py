"""
SSRF Guard — Centralized Server-Side Request Forgery Protection Module.

Protects against:
  1. Private / loopback / link-local / reserved IP access
  2. Cloud instance metadata endpoint probing (e.g. 169.254.169.254)
  3. DNS rebinding attacks via resolved-IP pinning
  4. Redirect loops, decompression bombs & payload flooding
"""

from __future__ import annotations

import ipaddress
import logging
import socket
import urllib.parse
from typing import Optional, Tuple

import requests
import requests.adapters

logger = logging.getLogger(__name__)

ALLOWED_SCHEMES = frozenset({"http", "https"})
MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB
DEFAULT_TIMEOUT = 10.0

BLOCKED_HOSTNAMES = frozenset({
    "localhost",
    "metadata.google.internal",
    "metadata.internal",
})

BLOCKED_METADATA_IPS = frozenset({
    "169.254.169.254",
})


class SSRFBlockedError(Exception):
    """Raised when a request is blocked by SSRF protection policies."""
    pass


class PayloadTooLargeError(Exception):
    """Raised when a response body exceeds the configured size limit."""
    pass


def _is_ip_safe(ip_str: str) -> bool:
    """Return True if IP is public and safe. Blocks private, loopback, link-local, reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if any([
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_reserved,
            ip.is_multicast,
            ip.is_unspecified,
        ]):
            return False
        if str(ip) in BLOCKED_METADATA_IPS:
            return False
        return True
    except ValueError:
        return False


def resolve_and_validate(hostname: str) -> str:
    """Resolve hostname to IP and verify safety, returning pinned IP string."""
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if not _is_ip_safe(str(ip_obj)):
            raise SSRFBlockedError(f"Blocked: target IP {hostname} resolves to a restricted address.")
        return str(ip_obj)
    except ValueError:
        pass

    try:
        resolved_ip = socket.gethostbyname(hostname)
    except socket.gaierror as exc:
        raise SSRFBlockedError(f"DNS resolution failed for hostname '{hostname}': {exc}") from exc

    if not _is_ip_safe(resolved_ip):
        raise SSRFBlockedError(f"Blocked: hostname '{hostname}' resolved to restricted IP {resolved_ip}.")

    return resolved_ip


def is_safe_url(url: str) -> bool:
    """Convenience boolean check for safe URL."""
    try:
        validate_url(url)
        return True
    except (SSRFBlockedError, Exception):
        return False


def validate_url(url: str) -> Tuple[str, str, int]:
    """Fully validate a URL and return (scheme, resolved_ip, port)."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as exc:
        raise SSRFBlockedError(f"Malformed URL: {url}") from exc

    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        raise SSRFBlockedError(f"Blocked: scheme '{scheme}' is not allowed. Only {ALLOWED_SCHEMES} are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFBlockedError(f"Blocked: URL has no hostname: {url}")

    hostname_lower = hostname.lower()
    if hostname_lower in BLOCKED_HOSTNAMES:
        raise SSRFBlockedError(f"Blocked: hostname '{hostname}' is on the blocklist.")

    resolved_ip = resolve_and_validate(hostname)
    port = parsed.port or (443 if scheme == "https" else 80)
    return scheme, resolved_ip, port


class _PinnedIPAdapter(requests.adapters.HTTPAdapter):
    """Requests adapter connecting to pre-resolved IP, mitigating DNS rebinding."""

    def __init__(self, pinned_ip: str, **kwargs):
        self._pinned_ip = pinned_ip
        super().__init__(**kwargs)

    def send(self, request, **kwargs):
        parsed = urllib.parse.urlparse(request.url)
        hostname = parsed.hostname or ""
        port_suffix = f":{parsed.port}" if parsed.port else ""

        if "Host" not in request.headers:
            request.headers["Host"] = hostname

        pinned_url = request.url.replace(
            f"{parsed.scheme}://{hostname}{port_suffix}",
            f"{parsed.scheme}://{self._pinned_ip}{port_suffix}",
            1,
        )
        request.url = pinned_url
        return super().send(request, **kwargs)


def safe_request(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = MAX_REDIRECTS,
    max_bytes: int = MAX_RESPONSE_BYTES,
    verify_ssl: bool = True,
    **kwargs,
) -> requests.Response:
    """Perform HTTP request with full SSRF, size cap, and redirect validation."""
    if headers is None:
        headers = {}

    current_url = url
    for hop in range(max_redirects + 1):
        scheme, resolved_ip, _port = validate_url(current_url)

        session = requests.Session()
        prefix = f"{scheme}://{resolved_ip}"
        session.mount(prefix, _PinnedIPAdapter(pinned_ip=resolved_ip))

        resp = session.request(
            method=method.upper(),
            url=current_url,
            headers=headers,
            timeout=timeout,
            allow_redirects=False,
            stream=True,
            verify=verify_ssl,
            **kwargs,
        )

        if resp.is_redirect or (300 <= resp.status_code < 400):
            next_url = resp.headers.get("Location")
            if not next_url:
                break
            current_url = urllib.parse.urljoin(current_url, next_url)
            resp.close()
            session.close()
            continue

        if method.upper() != "HEAD" and max_bytes > 0:
            content_length = resp.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                resp.close()
                session.close()
                raise PayloadTooLargeError(
                    f"Response Content-Length ({content_length} bytes) exceeds limit ({max_bytes} bytes)."
                )

            chunks = []
            bytes_read = 0
            for chunk in resp.iter_content(chunk_size=8192):
                bytes_read += len(chunk)
                if bytes_read > max_bytes:
                    resp.close()
                    session.close()
                    raise PayloadTooLargeError(f"Response body exceeded limit ({max_bytes} bytes).")
                chunks.append(chunk)

            resp._content = b"".join(chunks)

        session.close()
        return resp

    raise SSRFBlockedError("Too many redirects or redirection loop detected.")
