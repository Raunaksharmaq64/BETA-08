"""
Data Cleaner — Normalization, phone standardization, line classification, and duplicate removal.
"""

from __future__ import annotations

import concurrent.futures
import logging
import re
from typing import Dict, List, Optional

import phonenumbers
from phonenumbers import PhoneNumberType
import requests

from app.modules.freelance.collectors.base_collector import DiscoveredLead
from app.modules.freelance.constants import (
    PRIORITY_ORDER,
    WEBSITE_CHECK_MAX_SITES,
    WEBSITE_CHECK_MAX_WORKERS,
    WEBSITE_CHECK_TIMEOUT,
)
from app.modules.freelance.utils.ssrf_guard import is_safe_url, safe_request

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans, normalizes, and classifies business leads."""

    @staticmethod
    def standardize_phone(phone: str) -> str:
        """Standardize phone numbers into consistent readable formatting."""
        if not phone:
            return ""
        digits = re.sub(r"[^\d]", "", phone)
        if digits.startswith("91") and len(digits) == 12:
            return f"+91 {digits[2:7]} {digits[7:]}"
        elif digits.startswith("0") and len(digits) == 11:
            digits = digits[1:]
            return f"+91 {digits[:5]} {digits[5:]}"
        elif len(digits) == 10:
            return f"+91 {digits[:5]} {digits[5:]}"
        else:
            if phone.startswith("+"):
                return phone
            return f"+{digits}" if digits else ""

    @staticmethod
    def extract_whatsapp_number(phone: str) -> str:
        """Extract clean digits-only number for WhatsApp links."""
        if not phone:
            return ""
        digits = re.sub(r"[^\d]", "", phone)
        if len(digits) == 10:
            return f"91{digits}"
        elif len(digits) == 12 and digits.startswith("91"):
            return digits
        elif len(digits) == 11 and digits.startswith("0"):
            return f"91{digits[1:]}"
        return digits if len(digits) >= 10 else ""

    @staticmethod
    def validate_and_classify_phone(phone: str, default_region: str = "IN") -> Dict[str, Any]:
        """Classify phone number as MOBILE, LANDLINE, VOIP using libphonenumber."""
        if not phone:
            return {"is_valid": False, "whatsapp_number": "", "line_type": "UNKNOWN"}

        try:
            raw = (phone or "").strip()
            if raw.startswith("+"):
                parsed = phonenumbers.parse(raw, None)
            else:
                parsed = phonenumbers.parse(raw, default_region)

            is_valid = phonenumbers.is_valid_number(parsed)
            if not is_valid:
                return {"is_valid": False, "whatsapp_number": "", "line_type": "UNKNOWN"}

            formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            whatsapp_number = formatted.replace("+", "")

            num_type = phonenumbers.number_type(parsed)
            line_type = "UNKNOWN"
            if num_type == PhoneNumberType.MOBILE:
                line_type = "MOBILE"
            elif num_type in (PhoneNumberType.FIXED_LINE, PhoneNumberType.FIXED_LINE_OR_MOBILE):
                line_type = "MOBILE" if num_type == PhoneNumberType.FIXED_LINE_OR_MOBILE else "LANDLINE"
            elif num_type == PhoneNumberType.VOIP:
                line_type = "VOIP"

            return {
                "is_valid": True,
                "whatsapp_number": whatsapp_number,
                "line_type": line_type,
            }
        except Exception as e:
            logger.debug(f"[DataCleaner] Phone parsing exception for {phone}: {e}")
            return {"is_valid": False, "whatsapp_number": "", "line_type": "UNKNOWN"}

    @staticmethod
    def check_website_health(url: str) -> bool:
        """Test if website is online using SSRF-guarded HEAD probe with GET fallback."""
        if not url:
            return False

        target = url.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            resp = safe_request(target, method="HEAD", headers=headers, timeout=3.0)
            if resp.status_code < 500:
                return True
        except requests.exceptions.SSLError:
            return True
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            pass

        try:
            resp = safe_request(target, method="GET", headers=headers, timeout=3.0, max_bytes=1024)
            resp.close()
            if resp.status_code < 500:
                return True
        except requests.exceptions.SSLError:
            return True
        except Exception:
            pass

        return False

    @staticmethod
    def assign_priority(lead: DiscoveredLead) -> str:
        """
        Assign priority:
        - HIGH: No website or broken website, has phone, < 50 reviews (great prospect)
        - MEDIUM: No website or broken website, has phone, 50-200 reviews
        - LOW: No website, no phone OR > 200 reviews
        - IGNORE: Working website
        """
        if lead.website and not lead.is_broken_website:
            return "IGNORE"

        has_phone = bool(lead.phone)
        reviews = lead.reviews or 0

        if lead.is_broken_website:
            if has_phone and reviews < 50:
                return "HIGH"
            elif has_phone and reviews <= 200:
                return "MEDIUM"
            return "MEDIUM" if not has_phone else "HIGH"

        if has_phone and reviews < 50:
            return "HIGH"
        elif has_phone and reviews <= 200:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def remove_duplicates(leads: List[DiscoveredLead]) -> List[DiscoveredLead]:
        """Multi-signal duplicate removal."""
        seen_ids = set()
        seen_phones = set()
        seen_names = set()
        unique: List[DiscoveredLead] = []

        for lead in leads:
            if lead.place_id and lead.place_id in seen_ids:
                continue

            phone_digits = re.sub(r"\D", "", lead.phone) if lead.phone else ""
            if phone_digits and phone_digits in seen_phones:
                continue

            name_key = f"{(lead.name or '').lower().strip()}_{(lead.city or '').lower().strip()}"
            if name_key in seen_names:
                continue

            if lead.place_id:
                seen_ids.add(lead.place_id)
            if phone_digits:
                seen_phones.add(phone_digits)
            seen_names.add(name_key)
            unique.append(lead)

        return unique

    @staticmethod
    def clean_leads(leads: List[DiscoveredLead]) -> List[DiscoveredLead]:
        """Clean fields, standardize phones, check website health, and assign priority."""
        # 1. Basic field cleaning & phone standardization
        for lead in leads:
            lead.name = (lead.name or "").strip()
            lead.address = (lead.address or "").strip()
            lead.city = (lead.city or "").strip().title()
            lead.category = (lead.category or "").strip().title() if lead.category else "Other"

            phone_info = DataCleaner.validate_and_classify_phone(lead.phone)
            if phone_info["is_valid"]:
                lead.phone = DataCleaner.standardize_phone(lead.phone)
                lead.whatsapp_number = phone_info["whatsapp_number"]
                lead.line_type = phone_info["line_type"]

        # 2. Check website health concurrently for sites that have a website
        leads_with_site = [l for l in leads if l.website]
        if leads_with_site:
            sites_to_check = leads_with_site[:WEBSITE_CHECK_MAX_SITES]
            with concurrent.futures.ThreadPoolExecutor(max_workers=WEBSITE_CHECK_MAX_WORKERS) as executor:
                futures = {executor.submit(DataCleaner.check_website_health, l.website): l for l in sites_to_check}
                for future in concurrent.futures.as_completed(futures):
                    target_lead = futures[future]
                    try:
                        is_alive = future.result()
                        target_lead.is_broken_website = not is_alive
                    except Exception:
                        target_lead.is_broken_website = True

        # 3. Assign priority scores
        for lead in leads:
            lead.priority = DataCleaner.assign_priority(lead)

        return DataCleaner.remove_duplicates(leads)

    @staticmethod
    def filter_leads(leads: List[DiscoveredLead], include_with_website: bool = False) -> List[DiscoveredLead]:
        """Filter out IGNORE leads unless include_with_website is True."""
        if include_with_website:
            return leads
        return [l for l in leads if l.priority != "IGNORE"]
