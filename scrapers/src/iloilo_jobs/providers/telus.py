from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from curl_cffi import requests as curl_requests

from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

logger = logging.getLogger(__name__)

# Broad Iloilo search (includes Pavia). Narrow /search/jobs/in/iloilo misses most roles.
TELUS_SEARCH_URL = "https://jobs.telusdigital.com/search/jobs"
TELUS_JOB_BASE = "https://jobs.telusdigital.com/jobs"

# Cloudflare blocks plain httpx; Chrome TLS impersonation via curl_cffi works.
TELUS_IMPERSONATE = "chrome131"
TELUS_XHR_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://jobs.telusdigital.com/search/jobs?location=iloilo",
    "X-Requested-With": "XMLHttpRequest",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def map_telus_entry(entry: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    scraped_at = scraped_at or _utc_now_iso()
    raw_id = str(entry.get("id") or entry.get("talemetry_job_id") or "")
    loc = entry.get("location") or {}
    city = loc.get("locality")
    region = loc.get("region_full") or loc.get("region_abbr")
    location = loc.get("name") or (
        f"{city}, {loc.get('country')}" if city else loc.get("country")
    )

    # Pavia is in Iloilo province; region_full is often "Iloilo"
    province = None
    blob = f"{city or ''} {region or ''} {location or ''}".lower()
    if "iloilo" in blob or "pavia" in blob or "ili" == str(loc.get("region_abbr") or "").lower():
        province = "Iloilo"

    permalink = str(entry.get("permalink") or raw_id).strip("/")
    # Multiple requisitions can share a permalink — keep id in the URL.
    source_url = f"{TELUS_JOB_BASE}/{permalink}?jid={raw_id}" if raw_id else f"{TELUS_JOB_BASE}/{permalink}"

    return Job(
        id=f"telus:{raw_id}",
        title=entry.get("title") or "",
        company_id="telus",
        company_name="",
        raw_id=raw_id,
        source="talemetry",
        scraped_at=scraped_at,
        location=location,
        city=city,
        province=province,
        source_url=source_url,
        apply_url=source_url,
    )


def parse_telus_payload(raw: Any, *, scraped_at: str | None = None) -> list[Job]:
    scraped_at = scraped_at or _utc_now_iso()
    if isinstance(raw, list):
        entries = raw
    elif isinstance(raw, dict):
        entries = raw.get("entries") or []
    else:
        raise TypeError("TELUS raw payload must be a dict or list")
    return [map_telus_entry(item, scraped_at=scraped_at) for item in entries]


@provider
class TelusProvider:
    """TELUS Digital / Talemetry Iloilo search (XHR JSON via curl_cffi, no Playwright)."""

    company_id = "telus"

    def __init__(
        self,
        *,
        search_url: str = TELUS_SEARCH_URL,
        location: str = "iloilo",
        per_page: int = 50,
        impersonate: str = TELUS_IMPERSONATE,
    ) -> None:
        self.search_url = search_url
        self.location = location
        self.per_page = per_page
        self.impersonate = impersonate

    def fetch_raw(self) -> dict[str, Any]:
        # curl_cffi impersonates Chrome TLS/JA3 so Cloudflare allows the Talemetry XHR.
        with curl_requests.Session(impersonate=self.impersonate) as session:
            warm = session.get(
                self.search_url,
                params={"location": self.location},
                timeout=30,
            )
            logger.info(
                "telus warm %s (cookies=%s)",
                warm.status_code,
                sorted(session.cookies.keys()),
            )

            response = session.get(
                self.search_url,
                params={"location": self.location, "per_page": self.per_page},
                headers=TELUS_XHR_HEADERS,
                timeout=30,
            )
            logger.info("telus xhr %s", response.status_code)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, dict):
            raise TypeError("TELUS API did not return a JSON object")
        return data

    def parse(self, raw: Any) -> list[Job]:
        return parse_telus_payload(raw)
