import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

CACHE_DIR = Path(__file__).parent.parent / "output" / ".cache"
REQUEST_TIMEOUT = 15
MAX_CONTENT_CHARS = 15_000
MAX_SUBPAGES = 3
SEARCH_DELAY = 0.5
