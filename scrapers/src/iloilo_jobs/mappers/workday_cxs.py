from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from iloilo_jobs.models.job import Job


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_posted_text(posted_on: str | None) -> str | None:
    if not posted_on:
        return None
    text = posted_on.strip().lower()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if "today" in text:
        return now.isoformat().replace("+00:00", "Z")
    m = re.search(r"(\d+)\s+day", text)
    if m:
        days = int(m.group(1))
        return (now - timedelta(days=days)).isoformat().replace("+00:00", "Z")
    if "30+" in text:
        return (now - timedelta(days=30)).isoformat().replace("+00:00", "Z")
    return None


def extract_iloilo_city(location_text: str | None, path: str | None) -> str | None:
    blob = f"{location_text or ''} {path or ''}"
    if re.search(r"iloilo|phl-ilo|/iloilo", blob, re.I):
        return "Iloilo"
    return None


def map_workday_cxs_posting(
    posting: dict[str, Any],
    *,
    company_id: str,
    site_base_url: str,
    scraped_at: str | None = None,
) -> Job:
    """Map a Workday CXS jobPosting to Job for any tenant/site."""
    scraped_at = scraped_at or _utc_now_iso()
    bullets = posting.get("bulletFields") or []
    raw_id = str(bullets[0]) if bullets else ""
    external_path = posting.get("externalPath") or ""
    if not raw_id:
        m = re.search(r"(JR\d+|R\d+)", external_path)
        raw_id = m.group(1) if m else external_path.rstrip("/").split("/")[-1]

    source_url = f"{site_base_url.rstrip('/')}{external_path}"
    location = posting.get("locationsText")
    city = extract_iloilo_city(location, external_path)

    return Job(
        id=f"{company_id}:{raw_id}",
        title=posting.get("title") or "",
        company_id=company_id,
        company_name="",
        raw_id=raw_id,
        source="workday",
        scraped_at=scraped_at,
        location=location,
        city=city,
        province="Iloilo" if city else None,
        employment_type=posting.get("timeType"),
        posted_at=parse_posted_text(posting.get("postedOn")),
        source_url=source_url,
        apply_url=source_url,
        remote=None,
        extra={"posted_text": posting.get("postedOn")},
    )


def parse_workday_cxs_payload(
    raw: dict[str, Any],
    *,
    company_id: str,
    site_base_url: str,
    scraped_at: str | None = None,
) -> list[Job]:
    scraped_at = scraped_at or _utc_now_iso()
    postings = raw.get("jobPostings") or []
    return [
        map_workday_cxs_posting(
            p,
            company_id=company_id,
            site_base_url=site_base_url,
            scraped_at=scraped_at,
        )
        for p in postings
    ]
