from __future__ import annotations

import argparse
import sys
from pathlib import Path

from iloilo_jobs.logging_config import setup_logging
from iloilo_jobs.pipeline.run import run_pipeline


def _repo_root() -> Path:
    # scrapers/src/iloilo_jobs/cli.py → repo root is parents[3]
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Iloilo BPO job scraper")
    sub = parser.add_subparsers(dest="command", required=True)

    scrape = sub.add_parser("scrape", help="Run the scrape pipeline")
    scrape.add_argument(
        "--providers",
        nargs="*",
        default=None,
        help="Company ids to scrape (default: all enabled)",
    )
    scrape.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Path to jobs.json (default: web/public/data/jobs.json)",
    )
    scrape.add_argument(
        "--metadata",
        type=Path,
        default=None,
        help="Path to metadata.json (default: beside jobs.json)",
    )
    scrape.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Raw response cache directory (default: cache/raw)",
    )
    scrape.add_argument(
        "--no-location-filter",
        action="store_true",
        help="Skip Iloilo location filtering",
    )
    scrape.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Directory for scraper.log (default: logs/)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = _repo_root()

    if args.command == "scrape":
        log_dir = args.log_dir or (root / "logs")
        setup_logging(log_dir=log_dir)

        jobs_path = args.out or (root / "web" / "public" / "data" / "jobs.json")
        metadata_path = args.metadata or jobs_path.with_name("metadata.json")
        cache_dir = args.cache_dir or (root / "cache" / "raw")

        jobs, stats = run_pipeline(
            company_ids=args.providers,
            cache_dir=cache_dir,
            jobs_path=jobs_path,
            metadata_path=metadata_path,
            apply_location_filter=not args.no_location_filter,
        )

        if stats.providers > 0 and stats.successful_providers == 0:
            return 1
        if not jobs and stats.successful_providers == 0:
            return 1
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
