# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timezone
import logging
import re
import asyncio
import warnings

# Suppress package rename warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

# pyrefly: ignore [missing-import]
from duckduckgo_search import DDGS
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

REDDIT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OpportunityFinderAgent/1.0 (prospecting bot for personal use)"
}

async def search_query(query: str) -> list[str]:
    """
    Searches using duckduckgo-search package first. If failed, falls back to
    DuckDuckGo HTML / Yahoo Search BeautifulSoup parsing.
    Returns a list of clean URLs.
    """
    serper_api_key = os.getenv("SERPER_API_KEY", "")
    if serper_api_key:
        logger.info(f"Searching for '{query}' using Serper.dev...")
        try:
            async with httpx.AsyncClient(headers={"X-API-KEY": serper_api_key, "Content-Type": "application/json"}, timeout=10.0) as client:
                resp = await client.post("https://google.serper.dev/search", json={"q": query, "num": 15})
                if resp.status_code == 200:
                    data = resp.json()
                    organic = data.get("organic", [])
                    urls = [res.get("link") for res in organic if res.get("link")]
                    if urls:
                        return urls
        except Exception as e:
            logger.error(f"Serper.dev search failed: {str(e)}. Falling back to default search...")

    urls = []
    logger.info(f"Searching for '{query}' using duckduckgo-search library...")
    try:
        loop = asyncio.get_event_loop()
        def _ddg_search():
            with DDGS() as ddgs:
                return [r["href"] for r in ddgs.text(query, max_results=15)]
        results = await loop.run_in_executor(None, _ddg_search)
        for url in results:
            if url.startswith("http"):
                urls.append(url)
        if urls:
            return urls
    except Exception as e:
        logger.warning(f"duckduckgo-search package failed: {str(e)}. Falling back to HTML scraping...")

    encoded_query = urllib.parse.quote_plus(query)
    ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    urls = []
    
    logger.info(f"Searching for '{query}'...")
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
            response = await client.get(ddg_url)
            if response.status_code == 200 and "anomaly-modal" not in response.text:
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", class_="result__url"):
                    href = link.get("href", "").strip()
                    if "uddg=" in href:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                        actual_url = parsed.get("uddg", [None])[0]
                        if actual_url:
                            href = actual_url
                    if href.startswith("http"):
                        urls.append(href)
            else:
                logger.warning("DuckDuckGo returned captcha or non-200. Falling back to Yahoo Search...")
                yahoo_url = f"https://search.yahoo.com/search?p={encoded_query}"
                for attempt in range(2):
                    try:
                        response = await client.get(yahoo_url)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, "html.parser")
                            for a in soup.find_all("a", href=True):
                                href = a["href"]
                                if "RU=" in href:
                                    try:
                                        parts = href.split("RU=")
                                        if len(parts) > 1:
                                            target = parts[1].split("/")[0]
                                            target_decoded = urllib.parse.unquote(target)
                                            if target_decoded.startswith("http") and not any(dom in target_decoded.lower() for dom in ["yahoo.com", "yimg.com"]):
                                                urls.append(target_decoded)
                                    except Exception:
                                        continue
                            break
                        else:
                            logger.warning(f"Yahoo Search failed with status {response.status_code} (attempt {attempt+1}/2). Retrying in 1s...")
                            await asyncio.sleep(1.0)
                    except Exception as ex:
                        logger.warning(f"Yahoo Search error (attempt {attempt+1}/2): {str(ex)}. Retrying in 1s...")
                        await asyncio.sleep(1.0)
    except Exception as e:
        logger.error(f"Search query error for '{query}': {str(e)}")
        
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    return unique_urls

async def search_query_with_details(query: str) -> list[dict]:
    """
    Searches using duckduckgo-search package first. If failed, falls back to
    DuckDuckGo HTML / Yahoo Search BeautifulSoup parsing.
    Returns a list of dicts with title, snippet, and url.
    """
    serper_api_key = os.getenv("SERPER_API_KEY", "")
    if serper_api_key:
        logger.info(f"Searching details for '{query}' using Serper.dev...")
        try:
            async with httpx.AsyncClient(headers={"X-API-KEY": serper_api_key, "Content-Type": "application/json"}, timeout=10.0) as client:
                resp = await client.post("https://google.serper.dev/search", json={"q": query, "num": 15})
                if resp.status_code == 200:
                    data = resp.json()
                    organic = data.get("organic", [])
                    results = [{
                        "title": res.get("title", ""),
                        "snippet": res.get("snippet", ""),
                        "url": res.get("link", "")
                    } for res in organic if res.get("link")]
                    if results:
                        return results
        except Exception as e:
            logger.error(f"Serper.dev details search failed: {str(e)}. Falling back to default search...")
    logger.info(f"Searching details for '{query}' using duckduckgo-search library...")
    try:
        loop = asyncio.get_event_loop()
        def _ddg_search_details():
            with DDGS() as ddgs:
                return [{
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                } for r in ddgs.text(query, max_results=15)]
        results = await loop.run_in_executor(None, _ddg_search_details)
        if results:
            return results
    except Exception as e:
        logger.warning(f"duckduckgo-search package failed for details: {str(e)}. Falling back to HTML scraping...")

    encoded_query = urllib.parse.quote_plus(query)
    ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    results = []
    
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
            response = await client.get(ddg_url)
            if response.status_code == 200 and "anomaly-modal" not in response.text:
                soup = BeautifulSoup(response.text, "html.parser")
                divs = soup.find_all("div", class_="result")
                for div in divs:
                    a_title = div.find("a", class_="result__a")
                    a_snippet = div.find("a", class_="result__snippet")
                    a_url = div.find("a", class_="result__url")
                    
                    title = a_title.text.strip() if a_title else ""
                    snippet = a_snippet.text.strip() if a_snippet else ""
                    href = a_url.get("href", "").strip() if a_url else (a_title.get("href", "").strip() if a_title else "")
                    
                    if "uddg=" in href:
                           parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                           actual_url = parsed.get("uddg", [None])[0]
                           if actual_url:
                                href = actual_url
                                
                    if href.startswith("http"):
                        results.append({
                            "title": title,
                            "snippet": snippet,
                            "url": href
                        })
            else:
                logger.warning("DuckDuckGo returned captcha or non-200 for details. Falling back to Yahoo...")
                yahoo_url = f"https://search.yahoo.com/search?p={encoded_query}"
                for attempt in range(2):
                    try:
                        response = await client.get(yahoo_url)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, "html.parser")
                            for div in soup.find_all("div", class_="algo"):
                                a = div.find("a", href=True)
                                h3 = div.find("h3")
                                snippet_div = div.find("div", class_="compText")
                                
                                title = h3.text.strip() if h3 else (a.text.strip() if a else "No Title")
                                snippet = snippet_div.text.strip() if snippet_div else ""
                                href = a["href"] if a else ""
                                
                                url = ""
                                if "RU=" in href:
                                    try:
                                        parts = href.split("RU=")
                                        if len(parts) > 1:
                                            target = parts[1].split("/")[0]
                                            url = urllib.parse.unquote(target)
                                    except Exception:
                                        pass
                                        
                                if url and url.startswith("http") and not any(dom in url.lower() for dom in ["yahoo.com", "yimg.com"]):
                                    results.append({
                                        "title": title,
                                        "snippet": snippet,
                                        "url": url
                                    })
                            break
                        else:
                            logger.warning(f"Yahoo Search detail failed with status {response.status_code} (attempt {attempt+1}/2). Retrying in 1s...")
                            await asyncio.sleep(1.0)
                    except Exception as ex:
                        logger.warning(f"Yahoo Search detail error (attempt {attempt+1}/2): {str(ex)}. Retrying in 1s...")
                        await asyncio.sleep(1.0)
    except Exception as e:
        logger.error(f"Error in search_query_with_details for '{query}': {str(e)}")
        
    return results
def extract_url_from_text(text: str) -> str:
    """
    Scans a text block for external web URLs or domains, filtering out standard social/aggregator sites.
    Returns the first matching URL, or an empty string.
    """
    if not text:
        return ""
    
    # 1. Look for http/https URLs
    urls = re.findall(r'https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]+', text)
    cleaned_urls = []
    for u in urls:
        # Strip trailing punctuation that might be part of sentence structure rather than the URL
        u = re.sub(r'[.,;:?!)\]"\'\s]+$', '', u)
        cleaned_urls.append(u)
        
    # 2. Look for standalone domains if no full URLs found
    if not cleaned_urls:
        words = text.split()
        for w in words:
            w_clean = w.strip('.,;:?!)[]"\'')
            if '@' not in w_clean and re.match(r'^[a-zA-Z0-9\-]+\.(?:com|org|net|co|io|sh|dev|app|ai|me|so|biz|info|us|in|to|ca|uk)$', w_clean, re.IGNORECASE):
                cleaned_urls.append(f"https://{w_clean}")
            
    skip_domains = [
        "reddit.com", "twitter.com", "x.com", "ycombinator.com", "producthunt.com", 
        "betalist.com", "facebook.com", "youtube.com", "github.com", "medium.com", 
        "crunchbase.com", "instagram.com", "pinterest.com", "glassdoor.com", 
        "indeed.com", "yimg.com", "google.com", "bing.com", "duckduckgo.com"
    ]
    
    for url in cleaned_urls:
        url_lower = url.lower()
        if not any(dom in url_lower for dom in skip_domains):
            return url
            
    return ""


def extract_emails_from_html(html: str) -> list[str]:
    """
    Extracts regular and obfuscated emails from HTML content.
    """
    if not html:
        return []
        
    found_emails = []
    
    # 1. Standard emails
    standard = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html)
    for e in standard:
        cleaned = e.strip().lower()
        if not cleaned.endswith(('.png', '.jpg', '.jpeg', '.gif', 'email.com', 'example.com')):
            found_emails.append(cleaned)
            
    # 2. Obfuscated emails: e.g. name [at] domain.com, name (at) domain . com, name at domain dot com
    # We match name, then an at indicator, then domain, then a dot indicator, then suffix
    obf_patterns = [
        r'\b([a-zA-Z0-9_.+-]+)\s*(?:\[at\]|\(at\)|at|@)\s*([a-zA-Z0-9-]+)\s*(?:\.|\[dot\]|\(dot\)|dot)\s*([a-zA-Z0-9-.]+)\b'
    ]
    for pattern in obf_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for m in matches:
            username, domain, suffix = m
            suffix_clean = suffix.replace(' ', '').replace('dot', '.').lower()
            domain_clean = domain.replace(' ', '').lower()
            username_clean = username.strip().lower()
            
            if username_clean in ['at', 'dot', 'http', 'www', 'image', 'img'] or suffix_clean in ['png', 'jpg', 'jpeg', 'gif']:
                continue
                
            email_reconstructed = f"{username_clean}@{domain_clean}.{suffix_clean}"
            if email_reconstructed not in found_emails:
                found_emails.append(email_reconstructed)
                
    return list(set(found_emails))


async def lookup_startup_website(startup_name: str) -> str:
    """
    Queries search engines to find the official website URL of a startup.
    This works without any API keys!
    """
    if (not startup_name) or ("startup" in startup_name.lower() and len(startup_name) < 10):
        return ""
        
    query = f"{startup_name} startup website"
    logger.info(f"Looking up official website URL for '{startup_name}' on search engines...")
    try:
        urls = await search_query(query)
        skip_domains = [
            "duckduckgo.com", "yahoo.com", "reddit.com", "linkedin.com", "twitter.com", 
            "x.com", "producthunt.com", "betalist.com", "facebook.com", 
            "youtube.com", "github.com", "medium.com", "crunchbase.com",
            "instagram.com", "pinterest.com", "glassdoor.com", "indeed.com", "yimg.com"
        ]
        for url in urls:
            url_lower = url.lower()
            if url.startswith("http") and not any(dom in url_lower for dom in skip_domains):
                logger.info(f"Found website domain for '{startup_name}': {url}")
                return url
    except Exception as e:
        logger.error(f"Error looking up website for '{startup_name}': {str(e)}")
    return ""

async def fetch_duckduckgo_signals(skills: list[str] = None):
    """
    Performs targeted web searches to find startup leads, questions, or freelancer hiring posts.
    """
    queries = []
    if skills:
        for skill in skills:
            queries.append(f"startup looking for {skill} developer")
            queries.append(f"hiring freelancer {skill}")
            queries.append(f"looking for {skill} landing page")
            queries.append(f"help with {skill}")
    else:
        queries = [
            "startup looking for developer",
            "hiring freelancer SaaS",
            "looking for agency webflow shopify landing page"
        ]
        
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    if skills:
        for skill in skills:
            keywords.append(skill.lower())
    
    for q in queries:
        try:
            logger.info(f"Fetching DuckDuckGo search signals for '{q}'...")
            results = await search_query_with_details(q)
            for res in results:
                combined_text = (res["title"] + " " + res["snippet"]).lower()
                matched_keywords = [kw for kw in keywords if kw in combined_text]
                if matched_keywords:
                    signals.append({
                        "source": "DuckDuckGo Search",
                        "title": res["title"],
                        "text": res["snippet"],
                        "url": res["url"],
                        "author": "Search Result",
                        "created_utc": datetime.now(timezone.utc).timestamp(),
                        "signals_matched": matched_keywords
                    })
        except Exception as e:
            logger.error(f"Error fetching DuckDuckGo signals for '{q}': {str(e)}")
            
    return signals

async def fetch_github_signals():
    """
    Fetches open issues labeled 'help wanted' from GitHub, indicating projects looking for developer support.
    """
    url = 'https://api.github.com/search/issues?q=label:"help%20wanted"+state:open&sort=created&per_page=30'
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    
    logger.info("Fetching GitHub signals...")
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                for item in items:
                    title = item.get("title", "")
                    body = item.get("body", "") or ""
                    combined_text = (title + " " + body).lower()
                    
                    matched_keywords = [kw for kw in keywords if kw in combined_text]
                    if matched_keywords:
                        repo_name = "Unknown Repo"
                        html_url = item.get("html_url", "")
                        parts = html_url.split("/")
                        if len(parts) >= 5:
                            repo_name = f"{parts[3]}/{parts[4]}"
                            
                        created_at = item.get("created_at")
                        timestamp = datetime.now(timezone.utc).timestamp()
                        if created_at:
                            try:
                                timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
                            except Exception:
                                pass
                                
                        signals.append({
                            "source": "GitHub",
                            "title": f"[{repo_name}] {title}",
                            "text": body[:800] + ("..." if len(body) > 800 else ""),
                            "url": html_url,
                            "author": item.get("user", {}).get("login", "Unknown"),
                            "created_utc": timestamp,
                            "signals_matched": matched_keywords
                        })
            else:
                logger.error(f"GitHub API returned status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Error fetching GitHub signals: {str(e)}")
        
    return signals

async def fetch_indiehackers_signals(skills: list[str] = None):
    """
    Queries IndieHackers posts via search engines to find founders discussing launches, help needed, or problems.
    """
    if skills:
        skills_query = " OR ".join(f'"{s}"' for s in skills)
        query = f"site:indiehackers.com/post OR site:indiehackers.com/p ({skills_query}) looking for OR hiring OR feedback OR help"
    else:
        query = "site:indiehackers.com/post OR site:indiehackers.com/p looking for OR hiring OR feedback OR help"
        
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    if skills:
        for skill in skills:
            keywords.append(skill.lower())
            
    try:
        logger.info("Fetching IndieHackers signals via search...")
        results = await search_query_with_details(query)
        for res in results:
            combined_text = (res["title"] + " " + res["snippet"]).lower()
            matched_keywords = [kw for kw in keywords if kw in combined_text]
            if matched_keywords:
                signals.append({
                    "source": "IndieHackers",
                    "title": res["title"].replace(" | Indie Hackers", ""),
                    "text": res["snippet"],
                    "url": res["url"],
                    "author": "Indie Hackers Post",
                    "created_utc": datetime.now(timezone.utc).timestamp(),
                    "signals_matched": matched_keywords
                })
    except Exception as e:
        logger.error(f"Error fetching IndieHackers signals: {str(e)}")
        
    return signals

async def fetch_devto_signals():
    """
    Fetches articles from Dev.to under tags 'startup' and 'saas' to identify building founders or tools.
    """
    tags = ["startup", "saas"]
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
        for tag in tags:
            url = f"https://dev.to/api/articles?tag={tag}&per_page=30"
            try:
                logger.info(f"Fetching Dev.to articles for tag '{tag}'...")
                response = await client.get(url)
                if response.status_code == 200:
                    articles = response.json()
                    for art in articles:
                        title = art.get("title", "")
                        desc = art.get("description", "") or ""
                        combined_text = (title + " " + desc).lower()
                        
                        matched_keywords = [kw for kw in keywords if kw in combined_text]
                        if matched_keywords:
                            published_at = art.get("published_at")
                            timestamp = datetime.now(timezone.utc).timestamp()
                            if published_at:
                                try:
                                    timestamp = datetime.fromisoformat(published_at.replace("Z", "+00:00")).timestamp()
                                except Exception:
                                    pass
                                    
                            signals.append({
                                "source": "Dev.to",
                                "title": title,
                                "text": desc[:800],
                                "url": art.get("url", ""),
                                "author": art.get("user", {}).get("name", "Unknown"),
                                "created_utc": timestamp,
                                "signals_matched": matched_keywords
                            })
            except Exception as e:
                logger.error(f"Error fetching Dev.to signals for tag '{tag}': {str(e)}")
                
    return signals

async def fetch_google_news_signals():
    """
    Fetches startup news from Google News RSS feeds to identify newly funded or launched startups.
    """
    queries = [
        "startup funding round",
        "startup launched product"
    ]
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
        for q in queries:
            encoded_query = urllib.parse.quote_plus(q)
            url = f"https://news.google.com/rss/search?q={encoded_query}"
            try:
                logger.info(f"Fetching Google News signals for '{q}'...")
                response = await client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "xml")
                    items = soup.find_all("item")
                    for item in items[:25]:
                        title_el = item.find("title")
                        link_el = item.find("link")
                        desc_el = item.find("description")
                        source_el = item.find("source")
                        pub_date_el = item.find("pubDate")
                        
                        title = title_el.text if title_el else "No Title"
                        link = link_el.text if link_el else ""
                        desc = desc_el.text if desc_el else ""
                        source = source_el.text if source_el else "Google News"
                        
                        clean_desc = BeautifulSoup(desc, "html.parser").get_text() if desc else ""
                        combined_text = (title + " " + clean_desc).lower()
                        
                        matched_keywords = [kw for kw in keywords if kw in combined_text]
                        if matched_keywords:
                            timestamp = datetime.now(timezone.utc).timestamp()
                            if pub_date_el:
                                try:
                                    dt = datetime.strptime(pub_date_el.text, "%a, %d %b %Y %H:%M:%S %Z")
                                    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
                                except Exception:
                                    pass
                                    
                            signals.append({
                                "source": "Google News",
                                "title": title,
                                "text": clean_desc[:800],
                                "url": link.strip(),
                                "author": source,
                                "created_utc": timestamp,
                                "signals_matched": matched_keywords
                            })
            except Exception as e:
                logger.error(f"Error fetching Google News signals for '{q}': {str(e)}")
                
    return signals

async def enrich_contact_info(startup_name: str, website_url: str = "") -> dict:
    """
    Enriches contact info for a startup by searching LinkedIn, Twitter, and contact pages.
    """
    logger.info(f"Enriching contact info for startup '{startup_name}'...")
    enriched = {
        "linkedin": "",
        "twitter": "",
        "email": "",
        "contact_page": ""
    }
    
    # Tomba.io API Integration (Alternative that allows Gmail signups)
    tomba_key = os.getenv("TOMBA_KEY", "")
    tomba_secret = os.getenv("TOMBA_SECRET", "")
    if tomba_key and tomba_secret and website_url:
        parsed = urllib.parse.urlparse(website_url)
        domain = parsed.netloc or parsed.path
        if domain.startswith("www."):
            domain = domain[4:]
        logger.info(f"Enrichment: Searching domain {domain} using Tomba.io API...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "X-Tomba-Key": tomba_key,
                    "X-Tomba-Secret": tomba_secret
                }
                resp = await client.get(f"https://api.tomba.io/v1/domain-search?domain={domain}", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    emails = data.get("data", {}).get("emails", [])
                    if emails:
                        best_email = None
                        highest_score = 0
                        for email in emails:
                            score = email.get("score", 0)
                            email_val = email.get("email", "")
                            if score > highest_score:
                                highest_score = score
                                best_email = email_val
                        
                        if best_email:
                            logger.info(f"Enrichment: Tomba.io API successfully found: {best_email}")
                            enriched["email"] = best_email
        except Exception as e:
            logger.error(f"Tomba.io search failed: {str(e)}")

    # Hunter.io API Integration (run only if Tomba didn't find an email)
    if not enriched["email"]:
        hunter_key = os.getenv("HUNTER_API_KEY", "")
        if hunter_key and website_url:
            parsed = urllib.parse.urlparse(website_url)
            domain = parsed.netloc or parsed.path
            if domain.startswith("www."):
                domain = domain[4:]
            logger.info(f"Enrichment: Searching domain {domain} using Hunter.io B2B Email API...")
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={hunter_key}")
                    if resp.status_code == 200:
                        data = resp.json()
                        emails = data.get("data", {}).get("emails", [])
                        if emails:
                            best_email = None
                            highest_confidence = 0
                            for email in emails:
                                confidence = email.get("confidence", 0)
                                email_val = email.get("value", "")
                                email_type = email.get("type", "")
                                
                                # Prefer B2B personal email (e.g. founder/ceo)
                                if email_type == "personal" and confidence > 70:
                                    best_email = email_val
                                    break
                                if confidence > highest_confidence:
                                    highest_confidence = confidence
                                    best_email = email_val
                            
                            if best_email:
                                logger.info(f"Enrichment: Hunter.io B2B Email API successfully found: {best_email}")
                                enriched["email"] = best_email
            except Exception as e:
                logger.error(f"Hunter.io search failed: {str(e)}")
    
    if not startup_name:
        return enriched
        
    q_linkedin = f'"{startup_name}" site:linkedin.com/company'
    q_twitter = f'"{startup_name}" (site:twitter.com OR site:x.com)'
    
    q_contact = f'"{startup_name}" founder email contact'
    if website_url:
        parsed = urllib.parse.urlparse(website_url)
        domain = parsed.netloc or parsed.path
        if domain.startswith("www."):
            domain = domain[4:]
        q_contact = f'site:{domain} "email" OR "contact" OR "founder" OR "@"'
    
    results = await asyncio.gather(
        search_query(q_linkedin),
        search_query(q_twitter),
        search_query_with_details(q_contact),
        return_exceptions=True
    )
    
    if isinstance(results[0], list):
        for url in results[0]:
            if "linkedin.com/company/" in url:
                enriched["linkedin"] = url.split("?")[0].rstrip("/")
                break
                
    if isinstance(results[1], list):
        for url in results[1]:
            if ("twitter.com/" in url or "x.com/" in url) and not any(x in url for x in ["/status/", "/intent/", "/share", "/hashtag/"]):
                enriched["twitter"] = url.split("?")[0].rstrip("/")
                break
                
    if isinstance(results[2], list):
        # 1. Scan snippets for emails first
        for item in results[2]:
            snippet = item.get("snippet", "")
            title = item.get("title", "")
            combined = snippet + " " + title
            found_emails = extract_emails_from_html(combined)
            if found_emails:
                enriched["email"] = found_emails[0]
                break
                
        # 2. Extract contact page URL
        for item in results[2]:
            url = item.get("url", "")
            url_lower = url.lower()
            if any(k in url_lower for k in ["contact", "support", "about", "team", "info"]):
                enriched["contact_page"] = url
                break
        
        if not enriched["contact_page"] and results[2]:
            # Fallback to the first URL from search results if no explicit contact page
            first_url = results[2][0].get("url", "")
            if first_url.startswith("http"):
                enriched["contact_page"] = first_url
                
        # 3. If email still not found, fetch and scrape the contact page!
        if not enriched["email"] and enriched["contact_page"]:
            try:
                logger.info(f"Enrichment: Scrape discovered contact page: {enriched['contact_page']}")
                async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=8.0) as client:
                    resp = await client.get(enriched["contact_page"])
                    if resp.status_code == 200:
                        sub_emails = extract_emails_from_html(resp.text)
                        if sub_emails:
                            enriched["email"] = sub_emails[0]
                            logger.info(f"Enrichment: Found email {sub_emails[0]} on contact page")
            except Exception as e:
                logger.warning(f"Enrichment: Failed to scrape {enriched['contact_page']}: {str(e)}")
        # 4. If email is still not found and website_url is present, run SMTP verifier
        if not enriched["email"] and website_url:
            parsed = urllib.parse.urlparse(website_url)
            domain = parsed.netloc or parsed.path
            if domain.startswith("www."):
                domain = domain[4:]
            try:
                import email_verifier
                logger.info(f"Enrichment: Running SMTP verification for {domain}...")
                verified = await email_verifier.guess_and_verify_emails(domain, startup_name)
                if verified:
                    enriched["email"] = verified[0]
                    logger.info(f"Enrichment: Verified guessed email: {verified[0]}")
                else:
                    enriched["email"] = f"contact@{domain}"
                    logger.info(f"Enrichment: SMTP verification failed. Fallback guess: contact@{domain}")
            except Exception as ev_ex:
                logger.warning(f"Enrichment: SMTP verification failed: {str(ev_ex)}")
                enriched["email"] = f"contact@{domain}"
                
    return enriched

async def fetch_reddit_signals(subreddits=None):
    """
    Fetches raw posts from specified subreddits and filters them for high-intent signals.
    """
    if subreddits is None:
        subreddits = ["saas", "startups", "SideProject"]
        
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched", 
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    
    async with httpx.AsyncClient(headers=REDDIT_HEADERS, follow_redirects=True, timeout=12.0) as client:
        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=50"
            try:
                logger.info(f"Fetching Reddit signals from /r/{sub}...")
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    for post in posts:
                        pdata = post.get("data", {})
                        title = pdata.get("title", "")
                        selftext = pdata.get("selftext", "")
                        combined_text = (title + " " + selftext).lower()
                        
                        matched_keywords = [kw for kw in keywords if kw in combined_text]
                        if matched_keywords:
                            signals.append({
                                "source": f"Reddit (/r/{sub})",
                                "title": title,
                                "text": selftext[:1200] + ("..." if len(selftext) > 1200 else ""),
                                "url": f"https://reddit.com{pdata.get('permalink', '')}",
                                "author": pdata.get("author", "Unknown"),
                                "created_utc": pdata.get("created_utc"),
                                "signals_matched": matched_keywords
                            })
                else:
                    logger.warning(f"Reddit JSON returned status {response.status_code}. Trying RSS fallback...")
                    rss_url = f"https://www.reddit.com/r/{sub}.rss"
                    rss_response = await client.get(rss_url)
                    if rss_response.status_code == 200:
                        soup = BeautifulSoup(rss_response.content, "xml")
                        entries = soup.find_all("entry")
                        for entry in entries[:30]:
                            title_el = entry.find("title")
                            link_el = entry.find("link", href=True)
                            content_el = entry.find("content")
                            author_el = entry.find("author")
                            
                            title = title_el.text if title_el else "No Title"
                            link = link_el["href"] if link_el else ""
                            content = content_el.text if content_el else ""
                            
                            author_name = "Unknown"
                            if author_el:
                                name_el = author_el.find("name")
                                if name_el:
                                    author_name = name_el.text.replace("/u/", "")
                            
                            clean_text = BeautifulSoup(content, "html.parser").get_text() if content else ""
                            combined_text = (title + " " + clean_text).lower()
                            
                            matched_keywords = [kw for kw in keywords if kw in combined_text]
                            if matched_keywords:
                                signals.append({
                                    "source": f"Reddit RSS (/r/{sub})",
                                    "title": title,
                                    "text": clean_text[:1200] + ("..." if len(clean_text) > 1200 else ""),
                                    "url": link,
                                    "author": author_name,
                                    "created_utc": datetime.now(timezone.utc).timestamp(),
                                    "signals_matched": matched_keywords
                                })
                    else:
                        logger.error(f"Reddit RSS fallback also failed with code {rss_response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching Reddit signals from /r/{sub}: {str(e)}")
                
    return signals

async def fetch_rss_signals():
    """
    Fetches raw posts from RSS feeds including BetaList and Hacker News Show HN.
    """
    feeds = {
        "Product Hunt Launches": "https://www.producthunt.com/feed",
        "BetaList Early Startups": "https://betalist.com/rss",
        "Hacker News Show HN": "https://news.ycombinator.com/showhn.rss",
        "Hacker News Newest": "https://news.ycombinator.com/rss"
    }
    
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
        for name, url in feeds.items():
            try:
                logger.info(f"Fetching RSS feed from {name}...")
                response = await client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "xml")
                    items = soup.find_all("item")
                    
                    if not items:
                        items = soup.find_all("entry")
                        
                    for item in items[:30]:
                        title_el = item.find("title")
                        link_el = item.find("link") or item.find("link", href=True)
                        desc_el = item.find("description") or item.find("summary") or item.find("content")
                        
                        title = title_el.text if title_el else "No Title"
                        link = ""
                        if link_el:
                            link = link_el.get("href", "") or link_el.text or ""
                            if not link.strip() and link_el.next_sibling and hasattr(link_el.next_sibling, 'strip'):
                                link = link_el.next_sibling.strip()
                        desc = desc_el.text if desc_el else ""
                        
                        clean_desc = BeautifulSoup(desc, "html.parser").get_text() if desc else ""
                        combined_text = (title + " " + clean_desc).lower()
                        
                        matched_keywords = [kw for kw in keywords if kw in combined_text]
                        if matched_keywords:
                            signals.append({
                                "source": name,
                                "title": title,
                                "text": clean_desc[:800],
                                "url": link.strip(),
                                "author": "System Feed",
                                "created_utc": datetime.now(timezone.utc).timestamp(),
                                "signals_matched": matched_keywords
                            })
            except Exception as e:
                logger.error(f"Error fetching RSS feed {name}: {str(e)}")
                
    return signals

async def audit_via_pagespeed_api(url: str, pagespeed_key: str = "") -> dict:
    """
    Queries Google PageSpeed Insights API to get real Lighthouse Performance, SEO, and Mobile scores.
    """
    # We run it for mobile strategy to check performance, mobile compliance, and SEO
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={urllib.parse.quote(url)}&strategy=mobile&category=performance&category=seo"
    if pagespeed_key:
        api_url += f"&key={pagespeed_key}"
        
    async with httpx.AsyncClient(follow_redirects=True, timeout=12.0) as client:
        response = await client.get(api_url)
        if response.status_code == 200:
            data = response.json()
            lh = data.get("lighthouseResult", {})
            categories = lh.get("categories", {})
            
            perf_score = int(categories.get("performance", {}).get("score", 1.0) * 100)
            seo_score = int(categories.get("seo", {}).get("score", 1.0) * 100)
            
            audits = lh.get("audits", {})
            viewport_audit = audits.get("viewport", {})
            viewport_pass = viewport_audit.get("score") == 1
            
            mobile_score = 100 if viewport_pass else 50
            
            # Extract specific audit issues
            issues = []
            if perf_score < 70:
                for audit_name in ["bootup-time", "speed-index", "interactive", "render-blocking-resources"]:
                    audit_val = audits.get(audit_name, {})
                    if audit_val.get("score", 1.0) < 0.9:
                        issues.append(f"Lighthouse Performance: {audit_val.get('title')} is low ({audit_val.get('displayValue', '')}).")
            if seo_score < 90:
                for audit_name in ["meta-description", "image-alt", "link-text"]:
                    audit_val = audits.get(audit_name, {})
                    if audit_val.get("score", 1.0) < 0.9:
                        issues.append(f"Lighthouse SEO: {audit_val.get('title')} is failing.")
                        
            return {
                "seo_score": seo_score,
                "performance_score": perf_score,
                "mobile_score": mobile_score,
                "issues": issues,
                "pagespeed_api_used": True
            }
    raise Exception("PageSpeed Insights API failed or returned non-200")


async def audit_website(url: str, api_key: str = ""):
    """
    Scrapes a startup's website and does a technical audit to detect opportunities.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc or parsed_url.path
    
    audit_results = {
        "domain": domain,
        "url": url,
        "success": False,
        "seo_score": 100,
        "performance_score": 100,
        "mobile_score": 100,
        "issues": [],
        "tech_stack": [],
        "meta_title": "",
        "meta_description": "",
        "contact_info": {}
    }
    
    # Try PageSpeed API first
    pagespeed_success = False
    pagespeed_key = os.getenv("PAGESPEED_API_KEY", "")
    try:
        logger.info(f"Attempting PageSpeed Insights API audit for {url}...")
        api_results = await audit_via_pagespeed_api(url, pagespeed_key)
        audit_results.update(api_results)
        pagespeed_success = True
        logger.info("PageSpeed Insights API audit succeeded.")
    except Exception as e:
        logger.warning(f"PageSpeed API audit failed: {str(e)}. Falling back to local BeautifulSoup audit.")
        
    start_time = datetime.now()
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
            response = await client.get(url)
            load_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if response.status_code != 200:
                # If PageSpeed succeeded, we still count it as a partial success
                if not pagespeed_success:
                    audit_results["issues"].append(f"Website returned status code {response.status_code}.")
                    return audit_results
                else:
                    response_text = ""
            else:
                response_text = response.text
                
            audit_results["success"] = True
            html = response_text
            soup = BeautifulSoup(html, "html.parser") if html else None
            
            # --- 1. LOCAL SEO/PERFORMANCE/MOBILE AUDITS (Only run if PageSpeed failed) ---
            if not pagespeed_success and soup:
                title_tag = soup.find("title")
                if title_tag and title_tag.text.strip():
                    audit_results["meta_title"] = title_tag.text.strip()
                else:
                    audit_results["seo_score"] -= 30
                    audit_results["issues"].append("Missing website title (<title> tag).")
                    
                desc_tag = soup.find("meta", attrs={"name": "description"})
                if desc_tag and desc_tag.get("content", "").strip():
                    audit_results["meta_description"] = desc_tag["content"].strip()
                else:
                    audit_results["seo_score"] -= 25
                    audit_results["issues"].append("Missing meta description tag.")
                    
                # Check for OpenGraph tags
                og_title = soup.find("meta", attrs={"property": "og:title"})
                og_desc = soup.find("meta", attrs={"property": "og:description"})
                if not og_title or not og_desc:
                    audit_results["seo_score"] -= 15
                    audit_results["issues"].append("Missing OpenGraph social share meta tags (og:title / og:description).")
                    
                # Check image alt tags
                images = soup.find_all("img")
                missing_alts = sum(1 for img in images if not img.get("alt"))
                if images and missing_alts > 0:
                    pct = int((missing_alts / len(images)) * 100)
                    if pct > 30:
                        audit_results["seo_score"] -= 15
                        audit_results["issues"].append(f"High number of images missing alt tags ({missing_alts} out of {len(images)} images).")

                # PERFORMANCE
                script_tags = len(soup.find_all("script"))
                stylesheet_tags = len(soup.find_all("link", rel="stylesheet"))
                
                if load_time_ms > 2500:
                    audit_results["performance_score"] -= 30
                    audit_results["issues"].append(f"Slow server response time: Landing page took {load_time_ms}ms to respond.")
                elif load_time_ms > 1200:
                    audit_results["performance_score"] -= 15
                    audit_results["issues"].append(f"Moderate response time: Landing page loaded in {load_time_ms}ms.")
                    
                if script_tags > 25:
                    audit_results["performance_score"] -= 15
                    audit_results["issues"].append(f"High density of javascript resources ({script_tags} script tags). Could cause latency.")

                # MOBILE
                viewport_tag = soup.find("meta", attrs={"name": "viewport"})
                if not viewport_tag:
                    audit_results["mobile_score"] -= 50
                    audit_results["issues"].append("Missing viewport meta tag. Website may render poorly on mobile screens.")
            elif soup:
                # PageSpeed succeeded, but let's grab title/desc for metadata if not filled
                title_tag = soup.find("title")
                if title_tag and title_tag.text.strip():
                    audit_results["meta_title"] = title_tag.text.strip()
                desc_tag = soup.find("meta", attrs={"name": "description"})
                if desc_tag and desc_tag.get("content", "").strip():
                    audit_results["meta_description"] = desc_tag["content"].strip()
            
            # --- 2. TECH STACK DETECTION (Always run locally if HTML is available) ---
            if html:
                tech_signatures = {
                    "WordPress": ["wp-content", "wp-includes", "wordpress"],
                    "Shopify": ["shopify.com", "cdn.shopify.com"],
                    "Webflow": ["webflow.com", "data-wf-page", "w-slider"],
                    "Next.js": ["_next/static", "__NEXT_DATA__"],
                    "React": ["react.development.js", "react.production.min.js", "react-dom"],
                    "TailwindCSS": ["tailwind.config", "tailwind.min.css"],
                    "Wix": ["wix.com", "wix-image"],
                    "Squarespace": ["squarespace.com", "static1.squarespace.com"],
                    "HubSpot": ["js.hs-scripts.com", "hubspot.com"],
                    "Vue.js": ["vue.js", "vue.min.js", "vue-router", "vue-next"],
                    "Nuxt.js": ["__NUXT__", "nuxt.js"],
                    "Angular": ["ng-version", "ng-app"],
                    "Svelte": ["svelte-"],
                    "Gatsby": ["gatsby-image", "GATSBY_"],
                    "Bootstrap": ["bootstrap.min.css", "bootstrap.min.js", "bootstrap.css"],
                    "jQuery": ["jquery.min.js", "jquery.js"],
                    "Intercom": ["widget.intercom.io", "intercomSettings"],
                    "Stripe": ["js.stripe.com", "stripe-checkout"],
                    "Google Analytics": ["google-analytics.com", "gtag.js", "analytics.js", "googletagmanager.com"],
                    "Hotjar": ["static.hotjar.com", "hotjar-"],
                    "Mixpanel": ["cdn.mxpnl.com", "mixpanel"],
                    "Sentry": ["sentry.io", "browser.sentry-cdn.com"],
                    "Firebase": ["firebaseapp.com", "firebase.js", "firebase-app"]
                }
                
                for tech, sigs in tech_signatures.items():
                    for sig in sigs:
                        if sig in html:
                            audit_results["tech_stack"].append(tech)
                            break

                # Wappalyzer API Integration
                wappalyzer_key = os.getenv("WAPPALYZER_API_KEY", "")
                if wappalyzer_key:
                    logger.info(f"Auditing tech stack for {url} using Wappalyzer API...")
                    try:
                        async with httpx.AsyncClient(headers={"x-api-key": wappalyzer_key}, timeout=10.0) as client:
                            resp = await client.get(f"https://api.wappalyzer.com/v2/lookup/?urls={urllib.parse.quote_plus(url)}")
                            if resp.status_code == 200:
                                data = resp.json()
                                techs = []
                                if isinstance(data, list) and len(data) > 0:
                                    techs = data[0].get("technologies", [])
                                elif isinstance(data, dict):
                                    techs = data.get("technologies", [])
                                    
                                for tech in techs:
                                    tech_name = tech.get("name")
                                    if tech_name and tech_name not in audit_results["tech_stack"]:
                                        audit_results["tech_stack"].append(tech_name)
                                logger.info(f"Wappalyzer API successfully found: {audit_results['tech_stack']}")
                    except Exception as e:
                        logger.error(f"Wappalyzer API query failed: {str(e)}")

            # --- 3. CONTACT INFO EXTRACTION (Always run locally if HTML is available) ---
            if html and soup:
                emails = extract_emails_from_html(html)
                if emails:
                    audit_results["contact_info"]["email"] = emails[0]
                        
                links = soup.find_all("a", href=True)
                contact_candidate_urls = []
                for link in links:
                    href = link["href"].lower()
                    if "twitter.com/" in href or "x.com/" in href:
                        audit_results["contact_info"]["twitter"] = link["href"]
                    elif "linkedin.com/company/" in href or "linkedin.com/in/" in href:
                        audit_results["contact_info"]["linkedin"] = link["href"]
                    elif "github.com/" in href:
                        audit_results["contact_info"]["github"] = link["href"]
                    elif any(k in href for k in ["contact", "support", "about", "team", "info"]):
                        full_href = urllib.parse.urljoin(url, link["href"])
                        if full_href.startswith(("http://", "https://")) and full_href not in contact_candidate_urls:
                            contact_candidate_urls.append(full_href)
                            
                # Set default contact page if found
                if contact_candidate_urls:
                    audit_results["contact_info"]["contact_page"] = contact_candidate_urls[0]
                    
                # If no email is found, crawl the candidates and typical fallback subpages
                if not audit_results["contact_info"].get("email"):
                    # Form typical subpages
                    parsed_base = urllib.parse.urlparse(url)
                    base_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"
                    common_paths = ["/contact", "/about", "/contact-us", "/about-us", "/team", "/support"]
                    for path in common_paths:
                        full_path = base_origin + path
                        if full_path not in contact_candidate_urls:
                            contact_candidate_urls.append(full_path)
                    
                    # Fetch up to 3 distinct subpages
                    crawled_count = 0
                    for subpage_url in contact_candidate_urls:
                        if crawled_count >= 3:
                            break
                        # Avoid crawling the home page again
                        if subpage_url.rstrip("/") == url.rstrip("/"):
                            continue
                        try:
                            logger.info(f"Crawling subpage for contact info: {subpage_url}...")
                            sub_response = await client.get(subpage_url, timeout=6.0)
                            if sub_response.status_code == 200:
                                crawled_count += 1
                                sub_emails = extract_emails_from_html(sub_response.text)
                                if sub_emails:
                                    audit_results["contact_info"]["email"] = sub_emails[0]
                                    logger.info(f"Found email {sub_emails[0]} on subpage {subpage_url}")
                                    break
                                
                                # Also collect social links if not found on home page
                                sub_soup = BeautifulSoup(sub_response.text, "html.parser")
                                sub_links = sub_soup.find_all("a", href=True)
                                for sl in sub_links:
                                    s_href = sl["href"].lower()
                                    if ("twitter.com/" in s_href or "x.com/" in s_href) and not audit_results["contact_info"].get("twitter"):
                                        audit_results["contact_info"]["twitter"] = sl["href"]
                                    elif ("linkedin.com/company/" in s_href or "linkedin.com/in/" in s_href) and not audit_results["contact_info"].get("linkedin"):
                                        audit_results["contact_info"]["linkedin"] = sl["href"]
                                    elif "github.com/" in s_href and not audit_results["contact_info"].get("github"):
                                        audit_results["contact_info"]["github"] = sl["href"]
                        except Exception as sub_ex:
                            logger.warning(f"Failed to crawl subpage {subpage_url}: {str(sub_ex)}")
                        
                    # If still no email found, run SMTP guesser & verifier as fallback
                    if not audit_results["contact_info"].get("email"):
                        try:
                            import email_verifier
                            logger.info(f"No email crawled. Running SMTP verification for {domain}...")
                            verified = await email_verifier.guess_and_verify_emails(domain)
                            if verified:
                                audit_results["contact_info"]["email"] = verified[0]
                                logger.info(f"Verified guessed email: {verified[0]}")
                            else:
                                audit_results["contact_info"]["email"] = f"contact@{domain}"
                                logger.info(f"SMTP verify failed. Fallback to default guess: contact@{domain}")
                        except Exception as ev_ex:
                            logger.warning(f"SMTP verification failed: {str(ev_ex)}")
                            # Hard fallback
                            audit_results["contact_info"]["email"] = f"contact@{domain}"
            elif not audit_results["contact_info"].get("email"):
                # If we couldn't fetch local HTML but got PageSpeed, fall back to default email guess
                audit_results["contact_info"]["email"] = f"contact@{domain}"
                        
            audit_results["seo_score"] = max(0, audit_results["seo_score"])
            audit_results["performance_score"] = max(0, audit_results["performance_score"])
            audit_results["mobile_score"] = max(0, audit_results["mobile_score"])

    except Exception as e:
        logger.error(f"Error auditing website {url}: {str(e)}")
        if not pagespeed_success:
            audit_results["issues"].append(f"Crawl failed: {str(e)}")
            
    return audit_results

async def fetch_hackernews_signals() -> list[dict]:
    """
    Fetches raw posts from Hacker News via the official Algolia API.
    Specifically Show HN posts and Ask HN hiring threads.
    """
    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "designer", "agency", "freelancer",
        "onboarding", "slow", "bug", "struggle", "pain", "failed", "help with",
        "redesign", "marketing", "seo", "conversion", "landing page", "launched",
        "feedback", "rate my", "criticize", "optimize", "wordpress", "webflow", "shopify"
    ]
    
    # 1. Fetch Show HN posts
    show_hn_url = "https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&hitsPerPage=40"
    # 2. Fetch Search queries for Hiring
    hiring_url = "https://hn.algolia.com/api/v1/search_by_date?query=hiring&tags=story&hitsPerPage=30"
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
        # Show HN
        try:
            logger.info("Fetching Hacker News Show HN signals...")
            response = await client.get(show_hn_url)
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                for hit in hits:
                    title = hit.get("title", "")
                    text = hit.get("story_text", "") or ""
                    url = hit.get("url", "")
                    
                    # If it's Show HN, the URL is the project's actual website. If missing, it points to HN.
                    hn_item_url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    target_url = url if url else hn_item_url
                    
                    combined_text = (title + " " + text).lower()
                    matched_keywords = [kw for kw in keywords if kw in combined_text]
                    if matched_keywords:
                        signals.append({
                            "source": "Hacker News (Show HN)",
                            "title": title,
                            "text": text[:1200] + ("..." if len(text) > 1200 else ""),
                            "url": target_url,
                            "author": hit.get("author", "Unknown"),
                            "created_utc": hit.get("created_at_i"),
                            "signals_matched": matched_keywords
                        })
            else:
                logger.error(f"Hacker News API (Show HN) returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching HN Show HN signals: {str(e)}")
            
        # Ask HN / Hiring search
        try:
            logger.info("Fetching Hacker News Hiring signals...")
            response = await client.get(hiring_url)
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                for hit in hits:
                    title = hit.get("title", "")
                    text = hit.get("story_text", "") or ""
                    url = hit.get("url", "")
                    hn_item_url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    target_url = url if url else hn_item_url
                    
                    combined_text = (title + " " + text).lower()
                    matched_keywords = [kw for kw in keywords if kw in combined_text]
                    if matched_keywords:
                        signals.append({
                            "source": "Hacker News (Hiring)",
                            "title": title,
                            "text": text[:1200] + ("..." if len(text) > 1200 else ""),
                            "url": target_url,
                            "author": hit.get("author", "Unknown"),
                            "created_utc": hit.get("created_at_i"),
                            "signals_matched": matched_keywords
                        })
            else:
                logger.error(f"Hacker News API (Hiring) returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching HN Hiring signals: {str(e)}")
            
    return signals



async def fetch_serpapi_signals(skills: list[str] = None):
    """
    Queries Google Search via SerpAPI for real-time startup pain points, technical debt,
    founder complaints, and engineering bottlenecks across the internet.
    """
    serpapi_key = os.getenv("SERPAPI_KEY", "")
    if not serpapi_key or "placeholder" in serpapi_key.lower():
        return []

    queries = [
        "startup (technical bottleneck OR scaling issue OR looking for developer) site:reddit.com/r/startups",
        "site:news.ycombinator.com (Ask HN Who is hiring OR Freelancer OR looking for developer)",
        "startup (slow database OR microservices migration OR technical debt bottleneck)",
        "site:indiehackers.com (need developer OR struggling with tech OR landing page churn)",
    ]
    if skills:
        for skill in skills[:3]:
            queries.append(f"startup looking for {skill} engineer OR freelancer")

    signals = []
    keywords = [
        "hiring", "hire", "looking for", "developer", "engineer", "contractor", "freelancer",
        "slow", "bottleneck", "scaling", "architecture", "bug", "struggle", "pain", "failed",
        "migration", "latency", "optimizing", "cloud", "security", "ai", "llm"
    ]

    async with httpx.AsyncClient(timeout=12.0) as client:
        for q in queries:
            try:
                resp = await client.get(
                    "https://serpapi.com/search.json",
                    params={"engine": "google", "q": q, "api_key": serpapi_key, "num": 8}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for r in data.get("organic_results", []):
                        title = r.get("title", "")
                        snippet = r.get("snippet", "")
                        link = r.get("link", "")
                        if not link:
                            continue
                        combined = (title + " " + snippet).lower()
                        matched = [kw for kw in keywords if kw in combined]
                        signals.append({
                            "source": "SerpAPI (Google Search)",
                            "title": title,
                            "text": snippet,
                            "url": link,
                            "author": r.get("source", "Web Founder"),
                            "created_utc": datetime.now(timezone.utc).timestamp(),
                            "signals_matched": matched or ["startup_pain_point"]
                        })
            except Exception as e:
                logger.debug(f"SerpAPI query error for '{q}': {e}")

    logger.info(f"[SerpAPI Scraper] Fetched {len(signals)} live internet startup pain points.")
    return signals
