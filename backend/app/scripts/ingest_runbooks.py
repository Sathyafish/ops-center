"""CLI: ingest data/runbooks markdown into Chroma vector store."""

import argparse
import json
from pathlib import Path

from app.ingestion.pipeline import default_runbooks_dir, ingest_runbooks_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest runbook markdown into Chroma")
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Runbooks directory (default: RUNBOOKS_DIR or repo data/runbooks)",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append chunks instead of rebuilding the collection (may duplicate)",
    )
    args = parser.parse_args()

    directory = args.dir or default_runbooks_dir()
    result = ingest_runbooks_directory(directory, rebuild=not args.append)
    print(json.dumps(result, indent=2))
    if result.get("status") != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
