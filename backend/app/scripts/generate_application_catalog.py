"""Generate data/graph/applications_catalog.json and CSV reference export."""

import argparse
import csv
import json
from pathlib import Path

from app.graph.application_catalog import generate_catalog, save_catalog


def write_csv(catalog: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "application_name",
        "description",
        "domain",
        "tier",
        "criticality",
        "sme_name",
        "sme_email",
        "eng_manager_name",
        "eng_manager_email",
        "product_manager_name",
        "product_manager_email",
        "director_name",
        "director_email",
        "director_title",
        "depends_on",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for app in catalog["applications"]:
            writer.writerow(
                {
                    "application_name": app["name"],
                    "description": app["description"],
                    "domain": app["domain"],
                    "tier": app["tier"],
                    "criticality": app["criticality"],
                    "sme_name": app["sme"]["name"],
                    "sme_email": app["sme"]["email"],
                    "eng_manager_name": app["eng_manager"]["name"],
                    "eng_manager_email": app["eng_manager"]["email"],
                    "product_manager_name": app["product_manager"]["name"],
                    "product_manager_email": app["product_manager"]["email"],
                    "director_name": app["director"]["name"],
                    "director_email": app["director"]["email"],
                    "director_title": app["director"].get("title", "Director"),
                    "depends_on": "|".join(app.get("depends_on") or []),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "data" / "graph" / "applications_catalog.json",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "data" / "graph" / "applications_reference.csv",
    )
    args = parser.parse_args()

    json_path = save_catalog(args.out_json)
    catalog = json.loads(json_path.read_text(encoding="utf-8"))
    write_csv(catalog, args.out_csv)
    print(f"Wrote {json_path} ({catalog['application_count']} applications)")
    print(f"Wrote {args.out_csv}")


if __name__ == "__main__":
    main()
