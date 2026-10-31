# Startup Intelligence — Source-by-Source Audit
## Workstream A Specification

- **Module:** `startup-intelligence`
- **Status:** COMPLETED & VERIFIED
- **Audit Date:** 2026-10-31

---

## 1. Overview & Classification Framework

The `Startups-problrms-hunter` satellite service aggregates observations across 12 distinct discovery channels. To maintain strict governance, every source is classified according to the RIGHT FIT Source Governance Taxonomy:

1. `OFFICIAL_API`: Direct public or authenticated REST/GraphQL API with clear rate limits and machine-readable schema.
2. `OFFICIAL_FEED`: Public syndication feed (RSS/Atom) intended for syndication.
3. `PERMITTED_PUBLIC_SOURCE`: Publicly accessible websites or web services queried under standard terms.
4. `DISCOVERY_ONLY`: Ephemeral search engine or crawler discovery queries; observations require separate corroboration.

---

## 2. Comprehensive 12-Source Inventory

### Source 1: Reddit RSS (`/r/saas`)
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://www.reddit.com/r/saas/new.rss`
- **Access Method:** Public HTTP GET with custom `User-Agent` header (`REDDIT_HEADERS`)
- **Fields Collected:** Title, post permalink, author, pubDate, raw text excerpt.
- **Reliability & Limitations:** High signal for bootstrap founder discussions; anonymous authors; self-reported claims.
- **Rate Limit Policy:** Max 1 request every 5 seconds.
- **Failure Behavior:** Returns empty list on 429 or 503; does not interrupt other sources.

### Source 2: Reddit RSS (`/r/startups`)
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://www.reddit.com/r/startups/new.rss`
- **Access Method:** Public HTTP GET with custom `User-Agent`.
- **Fields Collected:** Title, permalink, author, pubDate, text content.
- **Reliability & Limitations:** Strict moderation filters; founder feedback and technical hiring questions.

### Source 3: Reddit RSS (`/r/SideProject`)
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://www.reddit.com/r/SideProject/new.rss`
- **Access Method:** Public HTTP GET.
- **Fields Collected:** Early launch posts, demo links, tech stack details.

### Source 4: Product Hunt Launches RSS
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://www.producthunt.com/feed`
- **Access Method:** HTTP GET RSS feed parser (`BeautifulSoup` with `xml` parser).
- **Fields Collected:** Product name, tagline, description, permalink, launch date.
- **Reliability & Limitations:** Clean marketing copy; requires secondary crawling for official startup domain.

### Source 5: Hacker News Newest RSS
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://news.ycombinator.com/newest` / RSS mirror.
- **Access Method:** HTTP GET Atom/RSS feed parser.
- **Fields Collected:** Story title, comments URL, outbound link, submission timestamp.

### Source 6: Hacker News (Show HN)
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://news.ycombinator.com/show` RSS feed.
- **Fields Collected:** Project title, direct site link, submitter, problem statement.
- **Reliability & Limitations:** High engineering credibility; direct founder participation.

### Source 7: Hacker News (Hiring & Freelance)
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** Monthly "Ask HN: Who wants to be hired? / Who is hiring?" thread scraper.
- **Fields Collected:** Comment text, role requirements, contact email/handle, tech stack.
- **Reliability & Limitations:** High intent signal for contract or engineering capacity needs.

### Source 8: GitHub "Help Wanted" Issues API
- **Source Type:** `OFFICIAL_API`
- **Endpoint/URL:** `https://api.github.com/search/issues?q=label:"help+wanted"+state:open+type:issue`
- **Access Method:** GitHub REST API v3 with `Accept: application/vnd.github.v3+json`.
- **Fields Collected:** Issue title, repository name, issue URL, labels, body markdown, created_at.
- **Reliability & Limitations:** 100% verified technical need; rate limit: 60 unauthenticated requests/hr.

### Source 9: Dev.to Articles API
- **Source Type:** `OFFICIAL_API` / `OFFICIAL_FEED`
- **Endpoint/URL:** `https://dev.to/api/articles?tag=startup&per_page=15`
- **Access Method:** Public JSON REST API.
- **Fields Collected:** Article title, description, canonical_url, published_at, tags.
- **Reliability & Limitations:** Developer-written retrospectives and technical post-mortems.

### Source 10: Google News RSS Feeds
- **Source Type:** `OFFICIAL_FEED`
- **Endpoint/URL:** `https://news.google.com/rss/search?q=startup+launch+funding&hl=en-US`
- **Access Method:** Public Google News RSS feed parser.
- **Fields Collected:** Headline, news publisher, redirect URL, publication date.
- **Reliability & Limitations:** Broad coverage; redirect URLs require link resolution.

### Source 11: IndieHackers Discussions
- **Source Type:** `DISCOVERY_ONLY`
- **Endpoint/URL:** `https://www.indiehackers.com/` search and public feeds.
- **Access Method:** Web search and crawler queries.
- **Fields Collected:** Discussion title, author, problem thread excerpt, URL.

### Source 12: DuckDuckGo / Yahoo Search Fallback Engine
- **Source Type:** `DISCOVERY_ONLY`
- **Access Method:** `duckduckgo_search` library with automatic Yahoo Search redirect fallback on captcha challenges.
- **Fields Collected:** Query title, snippet, destination URL.
- **Reliability & Limitations:** Untrusted web text; requires corroboration before treating as fact.

