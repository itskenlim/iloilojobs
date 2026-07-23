from __future__ import annotations

from iloilo_jobs.models.job import Job


def matches_employment(
    job: Job,
    *,
    types: list[str] | None = None,
) -> bool:
    """Filter by employment_type. Empty types → allow all."""
    if not types:
        return True
    if not job.employment_type:
        return False
    wanted = {t.lower() for t in types}
    return job.employment_type.lower() in wanted
