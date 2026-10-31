"""
SerpApi Collector — Google Maps scraper via SerpApi.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
import urllib.parse
from typing import List, Optional, Set

from serpapi import GoogleSearch

from app.modules.freelance.collectors.base_collector import BaseCollector, DiscoveredLead

logger = logging.getLogger(__name__)


class SerpApiCollector(BaseCollector):
    """Collector querying Google Maps via official SerpApi engine."""

    def __init__(self, default_api_key: Optional[str] = None):
        self.default_api_key = default_api_key

    @property
    def platform_name(self) -> str:
        return "SerpApi Google Maps"

    def search(
        self,
        query: str,
        city: str,
        max_results: int = 20,
        exclude_place_ids: Optional[Set[str]] = None,
        start_offset: int = 0,
        api_key: Optional[str] = None,
    ) -> List[DiscoveredLead]:
        key = api_key or self.default_api_key or os.getenv("SERPAPI_KEY", "")
        is_placeholder = not key or "placeholder" in key.lower() or key in ("your_serpapi_key_here", "your_serpapi_key_placeholder")
        if is_placeholder:
            logger.info("[SerpApiCollector] No valid SerpApi key configured. Using DirectLocalDiscoveryCollector.")
            from app.modules.freelance.collectors.direct_collector import DirectLocalDiscoveryCollector
            return DirectLocalDiscoveryCollector().search(
                query=query,
                city=city,
                max_results=max_results,
                exclude_place_ids=exclude_place_ids,
                start_offset=start_offset,
            )

        search_query = f"{query} in {city}"
        leads: List[DiscoveredLead] = []
        start = start_offset
        ll_param: Optional[str] = None

        while len(leads) < max_results and start < 100:
            params = {
                "engine": "google_maps",
                "q": search_query,
                "type": "search",
                "api_key": key,
                "start": start,
            }
            if ll_param:
                params["ll"] = ll_param

            try:
                search = GoogleSearch(params)
                results = search.get_dict()

                if "error" in results:
                    raise RuntimeError(f"SerpApi Error: {results['error']}")

                # Coordinate pagination extraction
                if not ll_param:
                    ll_param = results.get("search_parameters", {}).get("ll")
                    if not ll_param:
                        next_url = results.get("serpapi_pagination", {}).get("next")
                        if next_url:
                            parsed_url = urllib.parse.urlparse(next_url)
                            query_params = urllib.parse.parse_qs(parsed_url.query)
                            ll_vals = query_params.get("ll")
                            if ll_vals:
                                ll_param = ll_vals[0]
                    if not ll_param and results.get("local_results"):
                        first_place = results["local_results"][0]
                        gps = first_place.get("gps_coordinates")
                        if gps:
                            lat = gps.get("latitude")
                            lng = gps.get("longitude")
                            if lat is not None and lng is not None:
                                ll_param = f"@{lat},{lng},14z"

                local_results = results.get("local_results", [])
                if not local_results:
                    break

                for place in local_results:
                    place_id = place.get("data_id") or place.get("place_id")
                    if not place_id:
                        fallback = f"{place.get('title', '')}_{place.get('address', '')}_{city}"
                        place_id = f"serpapi_{hashlib.sha256(fallback.encode()).hexdigest()[:16]}"

                    if exclude_place_ids and place_id in exclude_place_ids:
                        continue

                    website = ""
                    links = place.get("links", {})
                    if links:
                        website = links.get("website", "")
                    if not website:
                        website = place.get("website", "")

                    lead = DiscoveredLead(
                        place_id=place_id,
                        name=place.get("title", ""),
                        phone=place.get("phone", ""),
                        address=place.get("address", ""),
                        website=website,
                        rating=float(place.get("rating") or 0.0),
                        reviews=int(place.get("reviews") or 0),
                        category=place.get("type", "Business"),
                        city=city,
                        source=self.platform_name,
                    )

                    if lead.name:
                        leads.append(lead)

                    if len(leads) >= max_results:
                        break

                start += 20
                if len(leads) < max_results and start <= 100:
                    time.sleep(1)

            except Exception as e:
                logger.warning(f"[SerpApiCollector] Search notice ({e}). Falling back to DirectLocalDiscoveryCollector.")
                from app.modules.freelance.collectors.direct_collector import DirectLocalDiscoveryCollector
                fallback_leads = DirectLocalDiscoveryCollector().search(
                    query=query,
                    city=city,
                    max_results=max_results - len(leads),
                    exclude_place_ids=exclude_place_ids,
                    start_offset=start_offset,
                )
                leads.extend(fallback_leads)
                break

        if not leads:
            logger.info("[SerpApiCollector] 0 leads from SerpApi. Invoking DirectLocalDiscoveryCollector fallback.")
            from app.modules.freelance.collectors.direct_collector import DirectLocalDiscoveryCollector
            return DirectLocalDiscoveryCollector().search(
                query=query,
                city=city,
                max_results=max_results,
                exclude_place_ids=exclude_place_ids,
                start_offset=start_offset,
            )

        return leads[:max_results]

    def get_details(self, place_id: str) -> Optional[DiscoveredLead]:
        return None
