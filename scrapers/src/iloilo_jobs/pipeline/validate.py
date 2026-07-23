from __future__ import annotations

import logging

from iloilo_jobs.models.job import Job

logger = logging.getLogger(__name__)


def validate(jobs: list[Job]) -> tuple[list[Job], int]:
    """Keep jobs with required fields and at least one URL."""
    valid: list[Job] = []
    dropped = 0

    for job in jobs:
        if not job.id or not job.title or not job.company_id or not job.raw_id:
            dropped += 1
            logger.warning("Validation dropped job (missing required fields): %s", job.id or "<no-id>")
            continue
        if not job.source_url and not job.apply_url:
            dropped += 1
            logger.warning("Validation dropped job (no URL): %s", job.id)
            continue
        valid.append(job)

    if dropped:
        logger.info("Validation dropped %d job(s)", dropped)
    return valid, dropped
