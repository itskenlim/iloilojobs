from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.clients.smartrecruiters import SmartRecruitersClient
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

WNS_COMPANY_ID = "WNSGlobalServices144"
WNS_JOBS_BASE = f"https://jobs.smartrecruiters.com/{WNS_COMPANY_ID}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def map_wns_posting(posting: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    scraped_at = scraped_at or _utc_now_iso()
    raw_id = str(posting.get("id") or posting.get("uuid") or "")
    loc = posting.get("location") or {}
    city = loc.get("city")
    location = loc.get("fullLocation") or city
    employment = posting.get("typeOfEmployment") or {}
    department = posting.get("department") or {}
    dept_label = department.get("label") if isinstance(department, dict) else None

    remote = loc.get("remote")
    if remote is None:
        remote_flag = None
    else:
        remote_flag = bool(remote)

    source_url = f"{WNS_JOBS_BASE}/{raw_id}" if raw_id else WNS_JOBS_BASE

    return Job(
        id=f"wns:{raw_id}",
        title=posting.get("name") or "",
        company_id="wns",
        company_name="",
        raw_id=raw_id,
        source="smartrecruiters",
        scraped_at=scraped_at,
        location=location,
        city=city,
        province=loc.get("region"),
        employment_type=employment.get("label") if isinstance(employment, dict) else None,
        department=dept_label,
        posted_at=posting.get("releasedDate"),
        source_url=source_url,
        apply_url=source_url,
        remote=remote_flag,
        extra={"ref_number": posting.get("refNumber"), "uuid": posting.get("uuid")},
    )


def parse_wns_payload(raw: dict[str, Any], *, scraped_at: str | None = None) -> list[Job]:
    scraped_at = scraped_at or _utc_now_iso()
    content = raw.get("content") or []
    return [map_wns_posting(item, scraped_at=scraped_at) for item in content]


@provider
class WNSProvider:
    company_id = "wns"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        country: str | None = "ph",
        q: str | None = "Iloilo",
        client: SmartRecruitersClient | None = None,
    ) -> None:
        self.country = country
        self.q = q
        self._client = client or SmartRecruitersClient(WNS_COMPANY_ID, http=http)

    def fetch_raw(self) -> dict[str, Any]:
        return self._client.fetch_all(country=self.country, q=self.q)

    def parse(self, raw: Any) -> list[Job]:
        if not isinstance(raw, dict):
            raise TypeError("WNS raw payload must be a dict")
        return parse_wns_payload(raw)
