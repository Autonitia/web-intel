import hashlib
import json
import time
from pathlib import Path

from .config import CACHE_DIR

TTL_SECONDS = 86400  # 24 hours


def _cache_path(url: str) -> Path:
    slug = hashlib.sha256(url.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{slug}.json"


def get(url: str) -> str | None:
    path = _cache_path(url)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if time.time() - data["ts"] > TTL_SECONDS:
        path.unlink()
        return None
    return data["html"]


def put(url: str, html: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(url).write_text(json.dumps({"ts": time.time(), "url": url, "html": html}))


def clear() -> int:
    if not CACHE_DIR.exists():
        return 0
    files = list(CACHE_DIR.glob("*.json"))
    for f in files:
        f.unlink()
    return len(files)
