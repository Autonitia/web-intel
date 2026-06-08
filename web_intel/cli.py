"""
CLI entry point.

Usage:
    python -m web_intel https://example.com
    python -m web_intel --batch urls.csv
    python -m web_intel https://example.com --js
    python -m web_intel --clear-cache
"""

import argparse
import csv
import json
import sys

from .cache import clear as clear_cache
from .export import batch_to_csv, to_json
from .pipeline import scrape


def main():
    parser = argparse.ArgumentParser(description="Extract structured company intel from any website.")
    parser.add_argument("url", nargs="?", help="URL to scrape")
    parser.add_argument("--batch", metavar="FILE", help="CSV file with a 'url' column for batch processing")
    parser.add_argument("--js", action="store_true", help="Use Playwright for JS-rendered pages")
    parser.add_argument("--no-cache", action="store_true", help="Skip the HTML cache")
    parser.add_argument("--output", choices=["json", "csv", "both"], default="json", help="Output format")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress logs")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cached HTML and exit")
    args = parser.parse_args()

    if args.clear_cache:
        n = clear_cache()
        print(f"Cleared {n} cached files.")
        return

    if args.batch:
        with open(args.batch) as f:
            reader = csv.DictReader(f)
            urls = [row["url"].strip() for row in reader if row.get("url", "").strip()]
        if not urls:
            print("No URLs found in CSV.", file=sys.stderr)
            sys.exit(1)

        results = []
        for url in urls:
            try:
                result = scrape(url, js=args.js, use_cache=not args.no_cache, verbose=not args.quiet)
                results.append(result)
                if args.output in ("json", "both"):
                    path = to_json(result)
                    print(f"  → {path}")
            except Exception as e:
                print(f"  ✗ {url}: {e}", file=sys.stderr)

        if args.output in ("csv", "both"):
            path = batch_to_csv(results)
            print(f"\nCSV saved: {path}")

        print(f"\nDone. {len(results)}/{len(urls)} succeeded.")
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    result = scrape(args.url, js=args.js, use_cache=not args.no_cache, verbose=not args.quiet)

    if args.output in ("json", "both"):
        path = to_json(result)
        print(f"\nSaved: {path}")
    if args.output in ("csv", "both"):
        path = batch_to_csv([result])
        print(f"\nCSV saved: {path}")

    print("\n" + json.dumps(result.model_dump(), indent=4))


if __name__ == "__main__":
    main()
