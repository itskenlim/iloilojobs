from __future__ import annotations

import logging

from iloilo_jobs.models.job import Job

logger = logging.getLogger(__name__)


def deduplicate(jobs: list[Job]) -> tuple[list[Job], int]:
    """Collapse jobs by id; keep first occurrence."""
    seen: set[str] = set()
    unique: list[Job] = []
    removed = 0

    for job in jobs:
        if job.id in seen:
            removed += 1
            continue
        seen.add(job.id)
        unique.append(job)

    if removed:
        logger.info("Deduplicated %d jobs", removed)
    return unique, removed
