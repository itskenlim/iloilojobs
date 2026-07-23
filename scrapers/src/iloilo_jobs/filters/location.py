from __future__ import annotations

from iloilo_jobs.models.job import Job

# Default Iloilo-focused keywords (PHL-ILO Workday paths, Pavia TELUS, etc.)
DEFAULT_ILOILO_KEYWORDS = (
    "iloilo",
    "ilo",
    "pavia",
    "mandurriao",
)


def matches_location(
    job: Job,
    *,
    cities: list[str] | None = None,
    keywords: list[str] | None = None,
) -> bool:
    """
    Return True if the job matches any city or keyword.

    Searches location, city, province, title, source_url, and apply_url.
    """
    cities = [c.lower() for c in (cities or [])]
    keywords = [k.lower() for k in (keywords if keywords is not None else DEFAULT_ILOILO_KEYWORDS)]

    haystack_parts = [
        job.location or "",
        job.city or "",
        job.province or "",
        job.title or "",
        job.source_url or "",
        job.apply_url or "",
    ]
    haystack = " ".join(haystack_parts).lower()

    for city in cities:
        if city and city in haystack:
            return True

    for keyword in keywords:
        if not keyword:
            continue
        # Avoid matching short tokens as bare substrings of unrelated words
        # except known Workday path markers like "ilo" / "phl-ilo".
        if keyword == "ilo":
            if "phl-ilo" in haystack or "-ilo-" in haystack or "/iloilo" in haystack:
                return True
            continue
        if keyword in haystack:
            return True

    return False
