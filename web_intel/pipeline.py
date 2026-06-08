"""
Main scraping pipeline. Orchestrates: fetch → discover → clean → extract → enrich.
"""

from urllib.parse import urlparse

from .cleaner import clean_html
from .config import MAX_SUBPAGES
from .crawler import discover_subpages
from .extractor import extract
from .fetcher import fetch_html, fetch_with_js
from .models import CompanyIntel
from .search import enrich_founders


def scrape(url: str, js: bool = False, use_cache: bool = True, verbose: bool = True) -> CompanyIntel:
    log = print if verbose else lambda *a, **k: None
    if js:
        fetch = lambda u: fetch_with_js(u, use_cache=use_cache)
    else:
        fetch = lambda u: fetch_html(u, use_cache=use_cache)

    log(f"[1/5] Fetching {url} ...")
    main_html = fetch(url)

    log("[2/5] Discovering sub-pages ...")
    subpages = discover_subpages(main_html, url)
    if subpages:
        log(f"       Found: {subpages}")

    log("[3/5] Cleaning HTML ...")
    sections = [f"=== MAIN PAGE: {url} ===\n{clean_html(main_html)}"]
    for sp in subpages[:MAX_SUBPAGES]:
        try:
            sp_html = fetch(sp)
            sections.append(f"\n=== SUB-PAGE: {sp} ===\n{clean_html(sp_html)}")
        except Exception as e:
            log(f"       Skipped {sp}: {e}")
    combined = "\n\n".join(sections)

    log(f"[4/5] Extracting with LLM ({len(combined):,} chars) ...")
    result = extract(combined)

    log("[5/5] Enriching founder LinkedIn profiles ...")
    company = result.company_name or urlparse(url).netloc
    if result.founders:
        enriched = enrich_founders(
            [f.model_dump() for f in result.founders], company
        )
        for founder_model, enriched_data in zip(result.founders, enriched):
            if enriched_data.get("linkedin") and not founder_model.linkedin:
                founder_model.linkedin = enriched_data["linkedin"]

    return result
