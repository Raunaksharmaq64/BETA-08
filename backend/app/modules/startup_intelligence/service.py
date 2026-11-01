"""
RIGHT FIT Core — Startup Discovery Service
Native in-process orchestrator for mining startup pain points, technical bottlenecks,
and talent shortages across live feeds (Reddit, Hacker News, Dev.to, Google News, GitHub).
Enables single-instance AWS deployments with zero external microservice dependency.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.startup_service import StartupService

from . import scraper
from . import ai_agent

logger = logging.getLogger(__name__)


def _classify_signal_intent(title: str, text: str) -> tuple[str, int]:
    """Assigns category and urgency score based on high-intent technical signal keywords."""
    combined = (title + " " + text).lower()
    if any(k in combined for k in ["hire", "hiring", "looking for", "freelancer", "developer", "contractor", "engineer"]):
        return "Development", 8
    if any(k in combined for k in ["slow", "page load", "performance", "speed", "latency", "bottleneck", "optimization", "lcp"]):
        return "Performance", 8
    if any(k in combined for k in ["ai", "gpt", "llm", "chatbot", "agent", "rag", "embeddings"]):
        return "AI", 8
    if any(k in combined for k in ["seo", "google rank", "meta", "organic", "search ranking"]):
        return "SEO", 7
    if any(k in combined for k in ["onboarding", "ux", "ui", "redesign", "conversion", "churn"]):
        return "UI/UX", 7
    if any(k in combined for k in ["marketing", "growth", "acquisition", "traffic", "funnel"]):
        return "Marketing", 6
    return "Development", 6


def _extract_startup_name(signal: Dict[str, Any]) -> str:
    """Extracts a clean startup or founder name from signal metadata."""
    source = signal.get("source", "").lower()
    title = signal.get("title", "")
    author = signal.get("author", "")

    if "reddit" in source and author:
        return f"u/{author}"
    if "hacker news" in source:
        clean = title.replace("Show HN:", "").replace("Ask HN:", "").strip()
        clean = clean.split(" - ")[0].split(" | ")[0].split(":")[0].strip()
        return clean[:32] if clean else "Hacker News Startup"
    
    clean = title.split(" - ")[0].split(" | ")[0].split(":")[0].strip()
    return clean[:32] if clean else "Innovative Startup"


class StartupDiscoveryService:
    """Native in-process startup intelligence discovery engine."""

    @classmethod
    async def discover_raw_signals(
        cls,
        enabled_sources: Optional[List[str]] = None,
        subreddits: Optional[List[str]] = None,
        limit_per_source: int = 15,
    ) -> List[Dict[str, Any]]:
        """Asynchronously scrapes live startup feeds across multiple public platforms."""
        sources = enabled_sources or ["reddit", "hackernews", "devto", "google_news", "github"]
        sub_list = subreddits or ["saas", "startups", "SideProject"]

        tasks = []
        if "reddit" in sources:
            tasks.append(scraper.fetch_reddit_signals(sub_list))
        if "hackernews" in sources:
            tasks.append(scraper.fetch_hackernews_signals())
        if "devto" in sources:
            tasks.append(scraper.fetch_devto_signals())
        if "google_news" in sources:
            tasks.append(scraper.fetch_google_news_signals())
        if "github" in sources:
            tasks.append(scraper.fetch_github_signals())
        if "rss" in sources:
            tasks.append(scraper.fetch_rss_signals())

        all_signals: List[Dict[str, Any]] = []
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, list):
                    all_signals.extend(res)
                elif isinstance(res, Exception):
                    logger.warning(f"[StartupDiscovery] Sub-scraper exception: {res}")

        logger.info(f"[StartupDiscovery] Collected {len(all_signals)} raw signals across {len(sources)} platforms.")
        return all_signals

    @classmethod
    async def discover_leads(
        cls,
        category: Optional[str] = None,
        min_score: Optional[int] = None,
        source: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Fetches raw signals, analyzes them, and converts them to canonical lead schemas."""
        raw_signals = await cls.discover_raw_signals()

        # Deduplicate signals by URL
        seen_urls = set()
        unique_signals = []
        for s in raw_signals:
            url = s.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_signals.append(s)
            elif not url:
                unique_signals.append(s)

        leads: List[Dict[str, Any]] = []
        for sig in unique_signals:
            title = sig.get("title", "Discovered Technical Signal")
            text = sig.get("text", "")
            cat, score = _classify_signal_intent(title, text)

            if category and category.lower() != "all" and cat.lower() != category.lower():
                continue
            if min_score is not None and score < min_score:
                continue
            if source and source.lower() != "all" and source.lower() not in sig.get("source", "").lower():
                continue

            name = _extract_startup_name(sig)
            lead_id = str(uuid.uuid4())

            leads.append({
                "id": lead_id,
                "startup_name": name,
                "category": cat,
                "detected_signal": title,
                "pain_point_description": text[:800] if text else title,
                "insight": f"Observed via {sig.get('source', 'Community Feed')}: {title}. Indicates active engineering demand or architectural friction.",
                "opportunity": f"Technical consulting and engineering implementation for {name}.",
                "pitch_idea": f"Hi {name} team,\n\nI noticed your recent update regarding {title}. I specialize in {cat} architecture and can help you resolve this bottleneck quickly without long hiring cycles.\n\nBest,\n[Your Name]",
                "score": score,
                "score_explanation": f"Classified as {cat} signal with score {score}/10 based on keyword intent.",
                "source": sig.get("source", "Community Feed"),
                "url": sig.get("url"),
                "status": "New",
                "published_at": datetime.now(timezone.utc).isoformat(),
            })

            if len(leads) >= limit:
                break

        return leads

    @classmethod
    async def discover_and_import(
        cls,
        session: AsyncSession,
        category: Optional[str] = None,
        min_score: Optional[int] = None,
        source: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Discovers leads and immediately ingests them into the Core database via StartupService."""
        leads = await cls.discover_leads(category=category, min_score=min_score, source=source, limit=limit)
        return await StartupService.import_startup_leads(leads, session)

