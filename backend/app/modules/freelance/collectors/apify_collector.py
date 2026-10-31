"""
Apify Collector — Google Maps scraper via Apify Google Places Actor.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import List, Optional, Set

from apify_client import ApifyClient

from app.modules.freelance.collectors.base_collector import BaseCollector, DiscoveredLead

logger = logging.getLogger(__name__)


class ApifyCollector(BaseCollector):
    """Alternative Google Maps collector powered by Apify actors."""

    def __init__(self, default_token: Optional[str] = None):
        self.default_token = default_token

    @property
    def platform_name(self) -> str:
        return "Apify Google Maps"

    def search(
        self,
        query: str,
        city: str,
        max_results: int = 20,
        exclude_place_ids: Optional[Set[str]] = None,
        start_offset: int = 0,
        api_key: Optional[str] = None,
    ) -> List[DiscoveredLead]:
        token = api_key or self.default_token or os.getenv("APIFY_API_TOKEN", "")
        if not token:
            logger.warning("[ApifyCollector] No Apify API token provided.")
            return []

        leads: List[DiscoveredLead] = []
        try:
            client = ApifyClient(token)
            total_to_crawl = max_results + (start_offset or 0)
            run_input = {
                "searchStringsArray": [query],
                "locationQuery": city,
                "maxCrawledPlacesPerSearch": total_to_crawl,
                "scrapeWebsites": False,
                "language": "en",
            }

            logger.info(f"[ApifyCollector] Starting Apify Places scraper for '{query}' in '{city}'")
            run = client.actor("compass/crawler-google-places").call(run_input=run_input)
            if not run:
                raise RuntimeError("Apify actor run failed to start.")

            dataset_id = None
            if isinstance(run, dict):
                dataset_id = run.get("default_dataset_id") or run.get("defaultDatasetId")
            else:
                dataset_id = getattr(run, "default_dataset_id", None) or getattr(run, "defaultDatasetId", None)

            if not dataset_id:
                raise RuntimeError("Apify actor run did not return a default_dataset_id.")

            dataset_items = client.dataset(dataset_id).list_items().items
            if start_offset and start_offset > 0:
                dataset_items = dataset_items[start_offset:]

            for item in dataset_items:
                place_id = item.get("placeId") or item.get("cid") or item.get("id")
                if not place_id:
                    fallback = f"{item.get('title', '')}_{item.get('address', '')}_{city}"
                    place_id = f"apify_{hashlib.sha256(fallback.encode()).hexdigest()[:16]}"

                if exclude_place_ids and place_id in exclude_place_ids:
                    continue

                lead = DiscoveredLead(
                    place_id=place_id,
                    name=item.get("title", ""),
                    phone=item.get("phone", ""),
                    address=item.get("address", ""),
                    website=item.get("website", ""),
                    rating=float(item.get("totalScore") or item.get("stars") or 0.0),
                    reviews=int(item.get("reviewsCount") or item.get("reviews") or 0),
                    category=item.get("categoryName") or item.get("type") or "Business",
                    city=city,
                    source=self.platform_name,
                )

                if lead.name:
                    leads.append(lead)

                if len(leads) >= max_results:
                    break

        except Exception as e:
            logger.error(f"[ApifyCollector] Error fetching from Apify: {e}", exc_info=True)
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["unauthorized", "invalid token", "401", "quota", "limit", "credit", "usage"]):
                raise e

        return leads[:max_results]

    def get_details(self, place_id: str) -> Optional[DiscoveredLead]:
        return None
