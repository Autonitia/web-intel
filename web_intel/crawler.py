from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

SUBPAGE_KEYWORDS = ["about", "team", "founder", "contact", "pricing", "company", "leadership", "people", "our-story"]


def discover_subpages(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    found = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()
        if any(kw in href or kw in text for kw in SUBPAGE_KEYWORDS):
            full = urljoin(base_url, a["href"])
            if urlparse(full).netloc == base_domain:
                found.add(full)
    return sorted(found)
