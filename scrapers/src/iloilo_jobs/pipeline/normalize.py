from __future__ import annotations

import logging
from datetime import datetime, timezone

from iloilo_jobs.filters.location import DEFAULT_ILOILO_KEYWORDS, matches_location
from iloilo_jobs.models.company import load_company
from iloilo_jobs.models.job import Job

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(
    jobs: list[Job],
    *,
    location_keywords: list[str] | None = None,
    location_cities: list[str] | None = None,
    apply_location_filter: bool = True,
) -> list[Job]:
    """Attach company metadata and optionally filter by location."""
    keywords = (
        location_keywords
        if location_keywords is not None
        else list(DEFAULT_ILOILO_KEYWORDS)
    )
    cities = location_cities or []
    scraped_at = _utc_now_iso()
    normalized: list[Job] = []

    for job in jobs:
        try:
            company = load_company(job.company_id)
        except FileNotFoundError:
            logger.warning("Missing metadata for company_id=%s — keeping job as-is", job.company_id)
            company_name = job.company_name or job.company_id
        else:
            company_name = company.name

        job.company_name = company_name
        if not job.scraped_at:
            job.scraped_at = scraped_at
        if job.apply_url is None and job.source_url:
            job.apply_url = job.source_url

        if apply_location_filter and not matches_location(
            job, cities=cities, keywords=keywords
        ):
            continue

        normalized.append(job)

    logger.info("Normalized to %d jobs (location filter=%s)", len(normalized), apply_location_filter)
    return normalized
