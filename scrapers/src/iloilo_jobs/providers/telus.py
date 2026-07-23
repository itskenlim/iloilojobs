from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

# Broad Iloilo search (includes Pavia). Narrow /search/jobs/in/iloilo misses most roles.
TELUS_SEARCH_URL = "https://jobs.telusdigital.com/search/jobs"
TELUS_JOB_BASE = "https://jobs.telusdigital.com/jobs"

# Cloudflare blocks document navigations; Talemetry serves JSON to XHR clients.
TELUS_XHR_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/139.0.7258.5 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
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
    """TELUS Digital / Talemetry Iloilo search (XHR JSON, no Playwright)."""

    company_id = "telus"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        search_url: str = TELUS_SEARCH_URL,
        location: str = "iloilo",
        per_page: int = 50,
    ) -> None:
        self.search_url = search_url
        self.location = location
        self.per_page = per_page
        self._http = http or HttpClient(headers=TELUS_XHR_HEADERS)
        self._owns_http = http is None

    def fetch_raw(self) -> dict[str, Any]:
        # Cloudflare often 403s the first HTML hit but still sets __cf_bm.
        # Reuse that cookie jar for the Talemetry XHR JSON call.
        warm_url = f"{self.search_url}?location={self.location}"
        self._http.get(warm_url, raise_for_status=False)

        response = self._http.get(
            self.search_url,
            params={"location": self.location, "per_page": self.per_page},
        )
        data = response.json()
        if not isinstance(data, dict):
            raise TypeError("TELUS API did not return a JSON object")
        return data

    def parse(self, raw: Any) -> list[Job]:
        return parse_telus_payload(raw)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
