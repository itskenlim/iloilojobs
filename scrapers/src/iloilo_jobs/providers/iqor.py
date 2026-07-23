from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

IQOR_JOBS_URL = "https://apply.iqor.com/jobs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _strip_html(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _detail_url(job_posting_id: int | str) -> str:
    return f"https://apply.iqor.com/jobs/{job_posting_id}"


def map_iqor_item(item: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    scraped_at = scraped_at or _utc_now_iso()
    raw_id = str(item.get("jobPostingID") or item.get("jobReqID") or "")
    city = item.get("jobPostingCity")
    location = item.get("location") or (
        f"{city}, {item.get('jobPostingStateName')}" if city else None
    )
    remote = None
    if item.get("isWorkInOffice") is True:
        remote = False
    elif item.get("isWorkInOffice") is False:
        remote = True

    posted_at = None
    for key in ("startDt", "createdDt", "updatedDt"):
        val = item.get(key)
        if isinstance(val, str) and val:
            posted_at = val.replace("+00:00", "Z") if val.endswith("+00:00") else val
            if "T" in posted_at and not posted_at.endswith("Z") and "+" not in posted_at:
                posted_at = posted_at + "Z" if False else posted_at
            break

    source_url = _detail_url(raw_id) if raw_id else IQOR_JOBS_URL

    return Job(
        id=f"iqor:{raw_id}",
        title=item.get("jobTitleName") or "",
        company_id="iqor",
        company_name="",
        raw_id=raw_id,
        source="next_data",
        scraped_at=scraped_at,
        location=location,
        city=city,
        province=item.get("jobPostingStateName"),
        employment_type=item.get("jobType") or item.get("jobPostingType"),
        department=item.get("jobCategory") or item.get("laborCategory"),
        description=_strip_html(item.get("jobDescription") or item.get("jobHeader")),
        posted_at=posted_at,
        source_url=source_url,
        apply_url=source_url,
        remote=remote,
    )


def extract_list_data(raw: Any) -> list[dict[str, Any]]:
    """Accept pageProps payload, full __NEXT_DATA__, or bare listData list."""
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, dict):
        raise TypeError("iQor raw payload must be a dict or list")

    if "listData" in raw:
        return list(raw["listData"] or [])

    page_props = raw.get("pageProps")
    if isinstance(page_props, dict) and "listData" in page_props:
        return list(page_props["listData"] or [])

    props = raw.get("props")
    if isinstance(props, dict):
        page_props = props.get("pageProps")
        if isinstance(page_props, dict) and "listData" in page_props:
            return list(page_props["listData"] or [])

    raise ValueError("Could not find listData in iQor payload")


def parse_iqor_payload(raw: Any, *, scraped_at: str | None = None) -> list[Job]:
    scraped_at = scraped_at or _utc_now_iso()
    items = extract_list_data(raw)
    return [map_iqor_item(item, scraped_at=scraped_at) for item in items]


def parse_next_data_html(html: str) -> dict[str, Any]:
    """Extract __NEXT_DATA__ JSON from an SSR HTML page."""
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        raise ValueError("No __NEXT_DATA__ script found in HTML")
    return json.loads(match.group(1))


@provider
class IQorProvider:
    company_id = "iqor"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        jobs_url: str = IQOR_JOBS_URL,
    ) -> None:
        self.jobs_url = jobs_url
        self._http = http or HttpClient()
        self._owns_http = http is None

    def fetch_raw(self) -> dict[str, Any]:
        response = self._http.get(self.jobs_url)
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            data = response.json()
            if isinstance(data, dict):
                return data
            return {"listData": data}

        next_data = parse_next_data_html(response.text)
        # Prefer the pageProps slice for a smaller cache payload
        props = next_data.get("props") or {}
        page_props = props.get("pageProps")
        if isinstance(page_props, dict):
            return {"pageProps": page_props}
        return next_data

    def parse(self, raw: Any) -> list[Job]:
        return parse_iqor_payload(raw)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
