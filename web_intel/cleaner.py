import json
import re

from bs4 import BeautifulSoup, Comment

from .config import MAX_CONTENT_CHARS

STRIP_TAGS = ["script", "style", "noscript", "svg", "img", "video", "audio", "iframe", "canvas"]


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(STRIP_TAGS):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    meta = {}
    for tag in soup.find_all("meta"):
        name = tag.get("name", tag.get("property", ""))
        content = tag.get("content", "")
        if name and content:
            meta[name] = content

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)

    links = {}
    for a in soup.find_all("a", href=True):
        label = a.get_text(strip=True)
        if label and a["href"].startswith("http"):
            links[label] = a["href"]

    parts = []
    if meta:
        parts.append("META TAGS:\n" + json.dumps(meta, indent=2))
    parts.append("PAGE TEXT:\n" + text[:MAX_CONTENT_CHARS])
    if links:
        parts.append("LINKS FOUND:\n" + json.dumps(links, indent=2))
    return "\n\n".join(parts)
