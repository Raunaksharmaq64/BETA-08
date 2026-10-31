"""
Mockup Service — Dynamic SVG landing page preview generator for client outreach.
"""

from __future__ import annotations

import html as html_lib
from typing import Optional


class MockupService:
    @staticmethod
    def generate_svg_markup(business_name: str, category: str) -> str:
        """Dynamically generate a sanitized SVG mock landing page layout based on business category."""
        safe_name = html_lib.escape(business_name or "Your Business")
        cat_lower = (category or "").lower()

        if any(w in cat_lower for w in ["restaurant", "food", "cafe", "bakery", "dining"]):
            theme_color = "#f97316"
            bg_start = "#1e1b4b"
            bg_end = "#311005"
            headline = "Fresh Gourmet Delights Delivered To Your Table"
            sub_headline = "Taste the premium crafted recipes made by top local culinary experts."
            f1, f2, f3 = "🍕 Handcrafted Menu", "📅 Online Reservations", "🛵 Swift Door Delivery"
        elif any(w in cat_lower for w in ["gym", "fitness", "sport", "yoga", "crossfit"]):
            theme_color = "#a855f7"
            bg_start = "#09090b"
            bg_end = "#1e1b4b"
            headline = "Unleash Your Limits. Build Your Ultimate Physique."
            sub_headline = "Join the state-of-the-art gym with world class expert coaches."
            f1, f2, f3 = "🏋️ Elite Equipment", "💪 Personal Coaching", "🥗 Nutrition Programs"
        elif any(w in cat_lower for w in ["tech", "software", "agency", "app", "digital"]):
            theme_color = "#3b82f6"
            bg_start = "#020617"
            bg_end = "#172554"
            headline = "Scale Your Operations with Intelligent Automation"
            sub_headline = "Custom enterprise grade digital architectures engineered to convert."
            f1, f2, f3 = "⚡ Lightning Fast Performance", "🔒 Military-Grade Encryption", "📊 AI-Powered Analytics"
        else:
            theme_color = "#06b6d4"
            bg_start = "#0f172a"
            bg_end = "#083344"
            headline = "Elevate Your Local Brand Into A Digital Authority"
            sub_headline = "We build premium customer generation websites that grow your sales."
            f1, f2, f3 = "🎨 Modern Premium Design", "📈 Local SEO Authority", "💬 Instant Web Lead Capture"

        words = headline.split(" ")
        line1 = " ".join(words[:3]) if len(words) >= 3 else " ".join(words)
        line2 = " ".join(words[3:]) if len(words) > 3 else ""

        return f"""<svg width="800" height="500" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_start}" />
      <stop offset="100%" stop-color="{bg_end}" />
    </linearGradient>
    <linearGradient id="btnGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{theme_color}" />
      <stop offset="100%" stop-color="#ec4899" />
    </linearGradient>
  </defs>
  <rect width="800" height="500" fill="url(#bgGrad)" rx="20" />
  <rect x="5" y="5" width="790" height="490" fill="none" stroke="rgba(255, 255, 255, 0.05)" stroke-width="2" rx="15" />
  <text x="50" y="55" font-family="system-ui, sans-serif" font-size="20" font-weight="900" fill="#ffffff" letter-spacing="1">⚡ {safe_name.upper()}</text>
  <text x="470" y="50" font-family="system-ui, sans-serif" font-size="12" font-weight="bold" fill="rgba(255,255,255,0.6)">Services</text>
  <text x="540" y="50" font-family="system-ui, sans-serif" font-size="12" font-weight="bold" fill="rgba(255,255,255,0.6)">Portfolio</text>
  <text x="610" y="50" font-family="system-ui, sans-serif" font-size="12" font-weight="bold" fill="rgba(255,255,255,0.6)">About</text>
  <rect x="670" y="32" width="80" height="28" rx="8" fill="none" stroke="{theme_color}" stroke-width="1.5" />
  <text x="710" y="50" font-family="system-ui, sans-serif" font-size="11" font-weight="bold" fill="{theme_color}" text-anchor="middle">Let's Talk</text>
  <text x="50" y="140" font-family="system-ui, sans-serif" font-size="30" font-weight="900" fill="#ffffff">
    <tspan x="50" dy="0">{line1}</tspan>
    <tspan x="50" dy="38" fill="{theme_color}">{line2}</tspan>
  </text>
  <text x="50" y="220" font-family="system-ui, sans-serif" font-size="14" fill="rgba(255,255,255,0.7)">{sub_headline}</text>
  <rect x="50" y="250" width="160" height="42" rx="10" fill="url(#btnGrad)" />
  <text x="130" y="276" font-family="system-ui, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Book A Consultation</text>
  <g transform="translate(50, 340)">
    <rect width="210" height="80" rx="12" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
    <text x="20" y="46" font-family="system-ui, sans-serif" font-size="13" font-weight="bold" fill="#ffffff">{f1}</text>
  </g>
  <g transform="translate(280, 340)">
    <rect width="210" height="80" rx="12" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
    <text x="20" y="46" font-family="system-ui, sans-serif" font-size="13" font-weight="bold" fill="#ffffff">{f2}</text>
  </g>
  <g transform="translate(510, 340)">
    <rect width="210" height="80" rx="12" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
    <text x="20" y="46" font-family="system-ui, sans-serif" font-size="13" font-weight="bold" fill="#ffffff">{f3}</text>
  </g>
</svg>"""
