import requests

from . import cache
from .config import REQUEST_TIMEOUT

# Full browser-like headers to avoid basic bot detection
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def _is_blocked(html: str, status: int) -> bool:
    """Detect if the response is a bot-block page rather than real content."""
    if status in (403, 503):
        return True
    snippet = html[:3000].lower()
    blocked_signals = [
        "just a moment", "captcha", "enable javascript",
        "challenge-platform", "cf-browser-verification",
        "attention required", "ray id",
    ]
    return any(s in snippet for s in blocked_signals)


def _fetch_with_cloudscraper(url: str) -> str:
    """Use cloudscraper to bypass Cloudflare JS challenges."""
    import cloudscraper
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )
    resp = scraper.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def _fetch_with_playwright(url: str) -> str:
    """Use Playwright for full JS rendering."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "Playwright not installed. Run:\n"
            "  pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=BROWSER_HEADERS["User-Agent"],
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()
    return html


def fetch_html(url: str, use_cache: bool = True) -> str:
    """
    Fetch strategy (automatic escalation):
      1. Plain requests with browser headers
      2. cloudscraper (handles Cloudflare JS challenges)
      3. Playwright (full headless browser)
    """
    if use_cache:
        cached = cache.get(url)
        if cached:
            return cached

    # Strategy 1: plain requests
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if not _is_blocked(resp.text, resp.status_code):
            resp.raise_for_status()
            html = resp.text
            if use_cache:
                cache.put(url, html)
            return html
        print(f"       ⚠ Blocked by bot protection, trying cloudscraper ...")
    except requests.RequestException:
        print(f"       ⚠ Request failed, trying cloudscraper ...")

    # Strategy 2: cloudscraper
    try:
        html = _fetch_with_cloudscraper(url)
        if not _is_blocked(html, 200):
            if use_cache:
                cache.put(url, html)
            return html
        print(f"       ⚠ Cloudscraper still blocked, trying Playwright ...")
    except Exception:
        print(f"       ⚠ Cloudscraper failed, trying Playwright ...")

    # Strategy 3: Playwright
    html = _fetch_with_playwright(url)
    if use_cache:
        cache.put(url, html)
    return html


def fetch_with_js(url: str, use_cache: bool = True) -> str:
    """Explicitly use Playwright (--js flag)."""
    if use_cache:
        cached = cache.get(url)
        if cached:
            return cached

    html = _fetch_with_playwright(url)
    if use_cache:
        cache.put(url, html)
    return html
