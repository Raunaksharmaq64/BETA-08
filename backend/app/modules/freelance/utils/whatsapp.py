"""
WhatsApp Messenger — Compliant wa.me click-to-chat URL generator.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Optional


class WhatsAppMessenger:
    """Generates pre-filled wa.me links for candidate-initiated outreach."""

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Strip non-digits and ensure country code format."""
        if not phone:
            return ""
        digits = re.sub(r"[^\d]", "", phone)
        if len(digits) == 10:
            return f"91{digits}"
        if digits.startswith("0") and len(digits) == 11:
            return f"91{digits[1:]}"
        return digits

    @staticmethod
    def generate_whatsapp_link(phone: str, message: str) -> str:
        """
        Builds a compliant https://wa.me/{phone}?text={encoded_message} URL.
        Never automatically transmits messages over the network.
        """
        clean_phone = WhatsAppMessenger.clean_phone_number(phone)
        if not clean_phone:
            return ""
        encoded = urllib.parse.quote(message.strip())
        return f"https://wa.me/{clean_phone}?text={encoded}"
