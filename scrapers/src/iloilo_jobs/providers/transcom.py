from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

TRANSCOM_API = "https://backend.transcom.com/api/v1/node/job_offering"
TRANSCOM_SITE = "https://careers.transcom.com"
CAREERS_PAGE = f"{TRANSCOM_SITE}/ph/job-openings/"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _strip_html(value: str | None) -> str | None:
    if not value:
        return None
    if isinstance(value, dict):
        value = value.get("processed") or value.get("value") or ""
    text = re.sub(r"<[^>]+>", " ", str(value))
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _city_from_title(title: str) -> str | None:
    if re.search(r"iloilo", title, re.I):
        return "Iloilo"
    return None


def _source_url(item: dict[str, Any]) -> str:
    attrs = item.get("attributes") or {}
    path = attrs.get("path") or {}
    alias = path.get("alias") if isinstance(path, dict) else None
    if alias:
        return f"{TRANSCOM_SITE}{alias}"
    # og:url sometimes points at backend
    for meta in attrs.get("metatag") or []:
        meta_attrs = meta.get("attributes") or {}
        if meta_attrs.get("property") == "og:url" and meta_attrs.get("content"):
            return str(meta_attrs["content"]).replace(
                "https://backend.transcom.com",
                TRANSCOM_SITE,
            )
    return CAREERS_PAGE


def _apply_url(item: dict[str, Any]) -> str | None:
    attrs = item.get("attributes") or {}
    link = attrs.get("link") or {}
    if isinstance(link, dict):
        return link.get("url") or link.get("uri")
    return None


def map_transcom_item(item: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    scraped_at = scraped_at or _utc_now_iso()
    attrs = item.get("attributes") or {}
    raw_id = str(item.get("id") or "")
    title = attrs.get("title") or ""
    city = _city_from_title(title)
    body = attrs.get("body")
    description = _strip_html(body if isinstance(body, str) else None)
    if description is None and isinstance(body, dict):
        description = _strip_html(body)

    source_url = _source_url(item)
    apply_url = _apply_url(item) or source_url

    return Job(
        id=f"transcom:{raw_id}",
        title=title,
        company_id="transcom",
        company_name="",
        raw_id=raw_id,
        source="drupal_jsonapi",
        scraped_at=scraped_at,
        location=f"{city}, Philippines" if city else None,
        city=city,
        province="Iloilo" if city == "Iloilo" else None,
        description=description,
        posted_at=attrs.get("created"),
        expires_at=attrs.get("apply_before"),
        source_url=source_url,
        apply_url=apply_url,
    )


def extract_transcom_jobs(raw: Any) -> list[dict[str, Any]]:
    """
    Accept:
    - Drupal JSON:API {data: [...]}
    - Next.js pageProps capture (webdata/transcom.txt shape)
    - Full __NEXT_DATA__
    - Bare jobsList array
    """
    if isinstance(raw, list):
        return raw

    if not isinstance(raw, dict):
        raise TypeError("Transcom raw payload must be a dict or list")

    if isinstance(raw.get("data"), list):
        return list(raw["data"])

    # pageProps / __NEXT_DATA__
    page_props = raw.get("pageProps")
    if page_props is None and isinstance(raw.get("props"), dict):
        page_props = raw["props"].get("pageProps")

    if isinstance(page_props, dict):
        initial = page_props.get("initialState")
        if isinstance(initial, str):
            initial = json.loads(initial)
        if isinstance(initial, dict):
            careers = initial.get("careers") or {}
            jobs_list = careers.get("jobsList") or careers.get("foundJobs") or []
            if isinstance(jobs_list, list):
                return list(jobs_list)

    if isinstance(raw.get("jobsList"), list):
        return list(raw["jobsList"])

    raise ValueError("Could not find Transcom job offerings in payload")


def parse_transcom_payload(raw: Any, *, scraped_at: str | None = None) -> list[Job]:
    scraped_at = scraped_at or _utc_now_iso()
    return [map_transcom_item(item, scraped_at=scraped_at) for item in extract_transcom_jobs(raw)]


@provider
class TranscomProvider:
    company_id = "transcom"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        api_url: str = TRANSCOM_API,
        search_text: str = "Iloilo",
    ) -> None:
        self.api_url = api_url
        self.search_text = search_text
        self._http = http or HttpClient(
            headers={"Accept": "application/vnd.api+json"},
        )
        self._owns_http = http is None

    def fetch_raw(self) -> dict[str, Any]:
        """Prefer Drupal JSON:API filtered by title (Iloilo)."""
        params = {
            "filter[title][operator]": "CONTAINS",
            "filter[title][value]": self.search_text,
            "page[limit]": 50,
        }
        response = self._http.get(self.api_url, params=params)
        data = response.json()
        if not isinstance(data, dict):
            raise TypeError("Transcom API did not return a JSON object")
        return data

    def parse(self, raw: Any) -> list[Job]:
        return parse_transcom_payload(raw)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
