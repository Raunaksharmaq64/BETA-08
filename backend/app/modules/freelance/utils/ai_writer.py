"""
AI Outreach Writer — Google Gemini prompt synthesis, prompt injection protection, and outreach generation.
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

logger = logging.getLogger(__name__)

INJECTION_PATTERNS = [
    r"(?i)system\s*override",
    r"(?i)ignore\s+(all\s+)?(prior|previous|past|above)?\s*(instructions|rules|directives|prompts|constraints)",
    r"(?i)disregard\s+(all\s+)?(prior|previous|past|above)?\s*(instructions|rules|directives|prompts|constraints)",
    r"(?i)output\s+(the\s+)?(system\s+prompt|api\s+key|credentials|secret)",
    r"(?i)reveal\s+(the\s+)?(system\s+prompt|api\s+key|credentials|secret)",
    r"\[INST\]",
    r"\[/INST\]",
    r"<<SYS>>",
    r"<</SYS>>",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"<\|endoftext\|>",
]


def sanitize_prompt_input(text: str, max_length: int = 500) -> str:
    """Sanitize untrusted external input before prompt injection."""
    if not text or not isinstance(text, str):
        return ""
    cleaned = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"<script.*?>.*?</script>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"[\u200b-\u200f\ufeff\u202a-\u202e]", "", cleaned)
    for pattern in INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[FILTERED_INPUT]", cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned[:max_length]


class AIRateLimiter:
    """Thread-safe rate limiter and circuit breaker for Gemini generation."""

    def __init__(self, max_per_minute: int = 30, max_per_day: int = 1000):
        self.max_per_minute = max_per_minute
        self.max_per_day = max_per_day
        self._user_requests: Dict[str, List[float]] = {}
        self._circuit_breakers: Dict[str, float] = {}
        self._lock = threading.Lock()

    def check_and_record(self, user_id: str = "default") -> bool:
        now = time.time()
        with self._lock:
            breaker_expiry = self._circuit_breakers.get(str(user_id), 0)
            if now < breaker_expiry:
                return False

            reqs = self._user_requests.setdefault(str(user_id), [])
            minute_reqs = [t for t in reqs if now - t < 60]
            day_reqs = [t for t in reqs if now - t < 86400]

            if len(minute_reqs) >= self.max_per_minute or len(day_reqs) >= self.max_per_day:
                self._circuit_breakers[str(user_id)] = now + 30
                return False

            day_reqs.append(now)
            self._user_requests[str(user_id)] = day_reqs
            return True


ai_rate_limiter = AIRateLimiter()


class AIOutreachWriter:
    _prompts = None
    _prompts_mtime = 0
    _prompts_lock = threading.Lock()

    @staticmethod
    def _load_prompts() -> Dict[str, Any]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompts_path = os.path.join(base_dir, "prompts", "outreach_pitches.yaml")
        try:
            current_mtime = os.path.getmtime(prompts_path)
        except OSError:
            current_mtime = 0

        with AIOutreachWriter._prompts_lock:
            if AIOutreachWriter._prompts is None or current_mtime != AIOutreachWriter._prompts_mtime:
                try:
                    with open(prompts_path, "r", encoding="utf-8") as f:
                        AIOutreachWriter._prompts = yaml.safe_load(f)
                    AIOutreachWriter._prompts_mtime = current_mtime
                except Exception as e:
                    logger.error(f"[AIOutreachWriter] Error loading prompts YAML from {prompts_path}: {e}")
                    if AIOutreachWriter._prompts is None:
                        AIOutreachWriter._prompts = {}
        return AIOutreachWriter._prompts or {}

    @staticmethod
    def _call_gemini_api(prompt: str, api_key: str, override_temp: float = 0.7) -> str:
        """Call Google Gemini generateContent API with fallback model ladder."""
        if not api_key:
            raise ValueError("Gemini API key is required.")

        models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": override_temp,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            },
        }

        last_error = None
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=20.0)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                last_error = f"Model {model} returned HTTP {resp.status_code}: {resp.text[:200]}"
            except Exception as exc:
                last_error = f"Model {model} connection failure: {exc}"

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    @classmethod
    def generate_pitch(
        cls,
        lead_data: Dict[str, Any],
        project_sample: str = "",
        tone: str = "elite",
        service: str = "Web Design & Development",
        sender_info: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None,
        mockup_link: str = "",
        audit_link: str = "",
    ) -> str:
        """Generates a WhatsApp outreach pitch using PAS, BAB, or AIDA framework."""
        prompts = cls._load_prompts()
        business_name = sanitize_prompt_input(lead_data.get("name") or lead_data.get("business_name", "Business"))
        city = sanitize_prompt_input(lead_data.get("city", "City"))
        category = sanitize_prompt_input(lead_data.get("category", "Services"))
        rating = lead_data.get("rating", 4.5)
        reviews = lead_data.get("reviews") or lead_data.get("reviews_count", 0)
        website = lead_data.get("website", "")
        is_broken = lead_data.get("is_broken_website", False)

        sender = sender_info or {}
        sender_name = sender.get("name", "RightFit Growth Partner")
        sender_brand = sender.get("brand", "RightFit")

        if is_broken:
            template = prompts.get("whatsapp_pitch_broken", "")
        elif not website:
            template = prompts.get("whatsapp_pitch_no_website", "")
        else:
            template = prompts.get("whatsapp_pitch_working_website", "")

        if not template:
            return cls._generate_fallback_pitch(lead_data, service, sender, mockup_link, audit_link)

        formatted_prompt = template.format(
            business_name=business_name,
            city=city,
            category=category,
            rating=rating,
            reviews=reviews,
            website_url=website,
            mockup_link=mockup_link or audit_link or "https://rightfit.platform/diagnostics",
            project_sample=project_sample or "Recent local business digital presence optimization case study",
            service_directives=f"Pitching: {service}",
            category_directives=f"Industry: {category} in {city}",
            tone_directives=f"Tone: {tone}",
            length_directives="Keep response punchy and concise, max 3 paragraphs.",
            hook_type_directive="Compliment their stellar Maps rating before addressing digital gaps.",
            persona_directive=f"representing {sender_brand}",
            language_directives="Use natural English with a warm and conversational professional tone.",
            custom_rules_directive="",
            signoff_directive=f"Sign-off: Best regards, {sender_name}",
        )

        resolved_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if resolved_key:
            try:
                return cls._call_gemini_api(formatted_prompt, resolved_key)
            except Exception as e:
                logger.warning(f"[AIOutreachWriter] Gemini generation failed: {e}. Using deterministic fallback.")

        return cls._generate_fallback_pitch(lead_data, service, sender, mockup_link, audit_link)

    @classmethod
    def generate_email_pitch(
        cls,
        lead_data: Dict[str, Any],
        project_sample: str = "",
        tone: str = "professional",
        service: str = "Web Design & Development",
        sender_info: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None,
        mockup_link: str = "",
        audit_link: str = "",
        min_words: int = 150,
    ) -> Tuple[str, str]:
        """Generates cold email (subject, body) via Gemini with strict fallback."""
        prompts = cls._load_prompts()
        template = prompts.get("email_pitch", "")

        business_name = sanitize_prompt_input(lead_data.get("name") or lead_data.get("business_name", "Business"))
        city = sanitize_prompt_input(lead_data.get("city", "City"))
        category = sanitize_prompt_input(lead_data.get("category", "Services"))
        rating = lead_data.get("rating", 4.5)
        reviews = lead_data.get("reviews") or lead_data.get("reviews_count", 0)
        website = lead_data.get("website", "")
        is_broken = lead_data.get("is_broken_website", False)

        sender = sender_info or {}
        sender_name = sender.get("name", "Growth Consultant")
        sender_brand = sender.get("brand", "RightFit")

        website_state = "broken website" if is_broken else ("no website listed" if not website else "active website")

        resolved_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if template and resolved_key:
            formatted_prompt = template.format(
                business_name=business_name,
                city=city,
                category=category,
                rating=rating,
                reviews=reviews,
                website_state=website_state,
                mockup_link=mockup_link or audit_link or "https://rightfit.platform/audit",
                project_sample=project_sample or f"Optimized local {category} digital booking platform",
                service_directives=f"Service: {service}",
                category_directives=f"Category: {category} in {city}",
                tone_directives=f"Tone: {tone}",
                email_length_directives=f"Length: At least {min_words} words.",
                language_directives="Write clean, direct business English.",
                signoff_str=f"{sender_name}\n{sender_brand}",
                custom_rules_directive="",
                min_words=min_words,
            )
            try:
                raw_output = cls._call_gemini_api(formatted_prompt, resolved_key)
                if "SUBJECT:" in raw_output and "BODY:" in raw_output:
                    parts = raw_output.split("BODY:")
                    subject = parts[0].replace("SUBJECT:", "").strip()
                    body = parts[1].strip()
                    return subject, body
            except Exception as e:
                logger.warning(f"[AIOutreachWriter] Gemini email generation failed: {e}. Falling back.")

        # Fallback Deterministic Generation
        if is_broken:
            subject = f"Question about {business_name}'s website link"
            body = (
                f"Hi {business_name} team,\n\n"
                f"I noticed your Google Maps listing has an impressive {rating}/5 rating with {reviews} reviews in {city}. "
                f"However, when I clicked your website link, it appears to be currently returning an error.\n\n"
                f"Many local customers research on mobile before visiting, so a broken link often results in lost bookings. "
                f"I specialize in {service} and have helped similar local businesses restore and modernize their digital presence.\n\n"
                f"Would you be open to a quick 5-minute chat this week to share a free performance recovery blueprint?\n\n"
                f"Best regards,\n{sender_name}\n{sender_brand}"
            )
        elif not website:
            subject = f"Modern web presence for {business_name}"
            body = (
                f"Hi {business_name} team,\n\n"
                f"Congratulations on your outstanding reputation in {city} with a {rating}/5 Google rating across {reviews} customer reviews!\n\n"
                f"I noticed you don't currently have a dedicated website listed on your profile. "
                f"Having a fast, mobile-friendly landing page allows local customers to explore your offerings, view customer proof, and reach out immediately.\n\n"
                f"I specialize in {service} and would love to show you a quick layout concept tailored to your business.\n\n"
                f"Would you like me to send over a preview link?\n\n"
                f"Best regards,\n{sender_name}\n{sender_brand}"
            )
        else:
            subject = f"Digital growth & performance review for {business_name}"
            body = (
                f"Hi {business_name} team,\n\n"
                f"I was reviewing top-rated {category} businesses in {city} and came across {business_name}. "
                f"Your {rating}/5 rating from {reviews} reviews clearly demonstrates strong local customer satisfaction.\n\n"
                f"I took a look at your website and identified several high-impact optimization opportunities around mobile speed and local conversion funnels.\n\n"
                f"I've put together a brief technical audit scorecard highlighting how these updates can help drive more direct inquiries.\n\n"
                f"Would you be open to taking a look?\n\n"
                f"Best regards,\n{sender_name}\n{sender_brand}"
            )

        return subject, body

    @classmethod
    def _generate_fallback_pitch(
        cls,
        lead_data: Dict[str, Any],
        service: str,
        sender: Dict[str, str],
        mockup_link: str,
        audit_link: str,
    ) -> str:
        """Reliable deterministic pitch when LLM is unavailable."""
        name = lead_data.get("name") or lead_data.get("business_name", "Business")
        city = lead_data.get("city", "City")
        rating = lead_data.get("rating", 4.5)
        reviews = lead_data.get("reviews") or lead_data.get("reviews_count", 0)
        is_broken = lead_data.get("is_broken_website", False)
        sender_name = sender.get("name", "RightFit Growth Partner")

        if is_broken:
            return (
                f"Hey {name} team! 👋\n\n"
                f"Noticed your *{rating} rating* and *{reviews} reviews* on Google Maps in {city} — amazing reputation!\n\n"
                f"Quick heads up: your listed website link currently returns an error page. "
                f"Most local customers search on their phones, so a down link causes visitors to bounce.\n\n"
                f"I specialize in {service} and put together a free diagnostic recovery draft for you:\n"
                f"{mockup_link or audit_link or 'https://rightfit.platform'}\n\n"
                f"Happy to walk you through it if helpful!\nBest, {sender_name}"
            )

        return (
            f"Hey {name} team! 👋\n\n"
            f"Congrats on your strong *{rating} rating* and *{reviews} reviews* on Google Maps in {city}!\n\n"
            f"I noticed you don't have a website listed on Maps yet. A mobile landing page lets local clients view your services and book instantly.\n\n"
            f"I drafted a preliminary concept for your business. Would you like me to send over the link?\n\n"
            f"Best, {sender_name}"
        )
