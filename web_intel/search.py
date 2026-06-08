"""
Multi-engine LinkedIn profile search.

Strategies (tried in order, first success wins):
  1. DuckDuckGo — free, no API key, generous limits
  2. Brave Search — free tier (2000 req/month), needs API key
  3. Google via SearXNG — if you self-host a SearXNG instance

All engines are optional; if a library/key is missing, it's skipped.
"""

import time
from urllib.parse import quote_plus

import requests

from .config import HEADERS, SEARCH_DELAY


def _search_duckduckgo(query: str, max_results: int = 3) -> list[dict]:
    try:
        from ddgs import DDGS
        ddgs = DDGS()
        return [{"title": r["title"], "url": r["href"]} for r in ddgs.text(query, max_results=max_results)]
    except Exception:
        return []


def _search_brave(query: str, max_results: int = 3) -> list[dict]:
    import os
    key = os.getenv("BRAVE_API_KEY", "")
    if not key:
        return []
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": key, "Accept": "application/json"},
            params={"q": query, "count": max_results},
            timeout=10,
        )
        resp.raise_for_status()
        return [{"title": r["title"], "url": r["url"]} for r in resp.json().get("web", {}).get("results", [])]
    except Exception:
        return []


def _search_searxng(query: str, max_results: int = 3) -> list[dict]:
    import os
    base = os.getenv("SEARXNG_URL", "")
    if not base:
        return []
    try:
        resp = requests.get(
            f"{base}/search",
            params={"q": query, "format": "json", "categories": "general"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        return [{"title": r["title"], "url": r["url"]} for r in resp.json().get("results", [])[:max_results]]
    except Exception:
        return []


ENGINES = [_search_duckduckgo, _search_brave, _search_searxng]


def search_web(query: str, max_results: int = 3) -> list[dict]:
    for engine in ENGINES:
        results = engine(query, max_results)
        if results:
            return results
    return []


def search_linkedin(name: str, company: str) -> str | None:
    query = f"site:linkedin.com/in {name} {company}"
    hits = search_web(query)
    for h in hits:
        if "linkedin.com/in/" in h["url"]:
            return h["url"]
    return None


def enrich_founders(founders: list[dict], company_name: str) -> list[dict]:
    for founder in founders:
        name = founder.get("name", "")
        if not name or founder.get("linkedin"):
            continue
        url = search_linkedin(name, company_name)
        if url:
            founder["linkedin"] = url
        time.sleep(SEARCH_DELAY)
    return founders
