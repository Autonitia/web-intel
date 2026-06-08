import csv
import json
from pathlib import Path

from .models import CompanyIntel

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def to_json(data: CompanyIntel, filename: str | None = None) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    name = filename or f"{data.company_name or 'result'}.json"
    name = name.replace("/", "_").replace(" ", "_")
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(data.model_dump(), indent=4))
    return path


def to_csv_row(data: CompanyIntel) -> dict:
    d = data.model_dump()
    flat = {
        "company_name": d["company_name"],
        "description": d["description"],
        "founders": "; ".join(f"{f['name']} ({f['role']})" for f in d["founders"]),
        "linkedin": d["social_media_links"].get("linkedin", ""),
        "twitter": d["social_media_links"].get("twitter", ""),
        "github": d["social_media_links"].get("github", ""),
        "features": "; ".join(d["features"]),
        "integrations": "; ".join(d["integrations"]),
        "email": d["contact"]["email"],
        "year_founded": d["year_founded"],
        "headquarters": d["headquarters"],
        "is_open_source": d["is_open_source"],
    }
    return flat


def batch_to_csv(results: list[CompanyIntel], filename: str = "batch_results.csv") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    if not results:
        return path
    rows = [to_csv_row(r) for r in results]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path
