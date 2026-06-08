# web-intel

Extract structured company intelligence from any website — no paid scraping APIs needed.

Built with **Pydantic** schemas + **OpenAI structured outputs**, so the extraction schema lives in code, not in prompts. Adding a new field = adding one line to `models.py`. Zero prompt changes.

## Features

- **3-Tier Fetch** — automatic escalation: `requests` → `cloudscraper` (Cloudflare bypass) → `Playwright` (full headless browser)
- **Auto Sub-Page Discovery** — finds and crawls `/about`, `/team`, `/pricing`, `/contact` pages automatically
- **Pydantic-Driven Extraction** — schema defined as Python models, enforced by OpenAI structured outputs
- **Multi-Engine LinkedIn Search** — DuckDuckGo → Brave Search → SearXNG fallback chain for founder profiles
- **HTML Caching** — 24-hour local cache to avoid redundant fetches during development
- **Batch Mode** — scrape a CSV of URLs and export results as JSON or CSV
- **JS Rendering** — optional Playwright support for JavaScript-heavy SPAs

## Quickstart

```bash
# Clone
git clone https://github.com/Autonitia/web-intel.git
cd web-intel

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run
python -m web_intel https://example.com
```

## Usage

```bash
# Single URL
python -m web_intel https://scrapegraphai.com

# Batch mode (CSV with a 'url' column)
python -m web_intel --batch examples/batch_urls.csv

# Export as CSV
python -m web_intel https://example.com --output csv

# Export both JSON and CSV
python -m web_intel https://example.com --output both

# Force JS rendering via Playwright
python -m web_intel https://spa-heavy-site.com --js

# Skip cache
python -m web_intel https://example.com --no-cache

# Clear all cached HTML
python -m web_intel --clear-cache

# Quiet mode (no progress logs)
python -m web_intel https://example.com --quiet
```

## Example Output

```json
{
    "company_name": "ScrapeGraphAI",
    "description": "The web scraping API built for the AI era. Extract structured data from any website — no proxies, no selectors, no maintenance needed.",
    "founders": [],
    "social_media_links": {
        "linkedin": "https://www.linkedin.com/company/scrapegraphai",
        "twitter": "https://x.com/scrapegraphai",
        "github": "https://github.com/ScrapeGraphAI",
        "discord": "https://discord.gg/JqvBb7wV8j",
        "reddit": "https://www.reddit.com/r/scrapegraphai/",
        "medium": "https://medium.com/@scrapegraphai",
        "website": "https://scrapegraphai.com"
    },
    "pricing": [
        {"plan": "Free", "price": "$0/mo", "features": ["500 credits/month", "10 req/min"]},
        {"plan": "Starter", "price": "$17/mo", "features": ["10,000 credits/month", "100 req/min"]},
        {"plan": "Growth", "price": "$85/mo", "features": ["100,000 credits/month", "500 req/min"]},
        {"plan": "Pro", "price": "$425/mo", "features": ["750,000 credits/month", "5,000 req/min"]}
    ],
    "features": [
        "AI-Powered Extraction",
        "Zero Maintenance",
        "JavaScript Rendering",
        "Auto-Adapts to Changes",
        "Built-in Rate Limiting"
    ],
    "integrations": ["LangChain", "CrewAI", "LlamaIndex", "n8n", "Zapier", "Make"],
    "contact": {"email": "support@scrapegraphai.com"},
    "year_founded": "",
    "is_open_source": true
}
```

## Project Structure

```
web-intel/
├── .env.example          # API key template
├── requirements.txt
├── examples/
│   └── batch_urls.csv    # Sample batch input
├── output/               # JSON + CSV exports
└── web_intel/
    ├── models.py         # Pydantic schema — the single source of truth
    ├── config.py         # Settings loaded from .env
    ├── fetcher.py        # 3-tier fetch with auto-escalation
    ├── cleaner.py        # HTML → clean text + meta tags + links
    ├── crawler.py        # Auto-discover relevant sub-pages
    ├── search.py         # Multi-engine LinkedIn search
    ├── extractor.py      # OpenAI structured outputs via Pydantic
    ├── export.py         # JSON + CSV export
    ├── cache.py          # 24hr HTML cache
    ├── pipeline.py       # Orchestrates the full pipeline
    └── cli.py            # CLI entry point
```

## How It Works

1. **Fetch** — tries plain HTTP, escalates to cloudscraper (Cloudflare bypass), then Playwright (headless browser)
2. **Discover** — scans links for relevant sub-pages (`/about`, `/team`, `/pricing`, `/contact`)
3. **Clean** — strips scripts, styles, and noise; extracts meta tags and all links
4. **Extract** — sends cleaned content to OpenAI with the Pydantic schema enforced via structured outputs
5. **Enrich** — searches DuckDuckGo/Brave/SearXNG for founder LinkedIn profiles

## Optional: Extra Search Engines

Add to `.env` for broader founder LinkedIn search coverage:

```bash
# Brave Search — free tier, 2000 queries/month
BRAVE_API_KEY=your-key

# SearXNG — self-hosted meta-search engine
SEARXNG_URL=http://localhost:8080
```

## License

MIT
