from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

NEARSOL_API = "https://nearsol.com/wp-json/wp/v2/careers_nearsol"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _strip_html(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _extract_location(content_html: str) -> tuple[str | None, str | None]:
    """Return (location_display, city) from WP content HTML."""
    m = re.search(r"Location:\s*([^<\n]+)", content_html, re.I)
    if m:
        loc = unescape(m.group(1)).strip()
        city = "Iloilo" if re.search(r"iloilo", loc, re.I) else None
        return loc, city
    if re.search(r"iloilo", content_html, re.I):
        return "Iloilo, Philippines", "Iloilo"
    return None, None


def map_nearsol_item(item: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    scraped_at = scraped_at or _utc_now_iso()
    raw_id = str(item.get("id") or item.get("slug") or "")
    title_obj = item.get("title") or {}
    title = title_obj.get("rendered") if isinstance(title_obj, dict) else str(title_obj or "")
    title = unescape(re.sub(r"<[^>]+>", "", title)).strip()

    content_obj = item.get("content") or {}
    content_html = content_obj.get("rendered") if isinstance(content_obj, dict) else ""
    location, city = _extract_location(content_html or "")
    link = item.get("link") or ""

    return Job(
        id=f"nearsol:{raw_id}",
        title=title,
        company_id="nearsol",
        company_name="",
        raw_id=raw_id,
        source="wordpress",
        scraped_at=scraped_at,
        location=location,
        city=city,
        province="Iloilo" if city == "Iloilo" else None,
        description=_strip_html(content_html),
        posted_at=item.get("date_gmt") or item.get("date"),
        source_url=link,
        apply_url=link,
    )


def parse_nearsol_payload(raw: Any, *, scraped_at: str | None = None) -> list[Job]:
    scraped_at = scraped_at or _utc_now_iso()
    if isinstance(raw, dict) and "items" in raw:
        items = raw["items"]
    elif isinstance(raw, list):
        items = raw
    else:
        raise TypeError("Nearsol raw payload must be a list or {items: [...]}")
    return [map_nearsol_item(item, scraped_at=scraped_at) for item in items]


@provider
class NearsolProvider:
    company_id = "nearsol"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        api_url: str = NEARSOL_API,
    ) -> None:
        self.api_url = api_url
        self._http = http or HttpClient()
        self._owns_http = http is None

    def fetch_raw(self) -> dict[str, Any]:
        response = self._http.get(self.api_url, params={"per_page": 100})
        items = response.json()
        if not isinstance(items, list):
            raise TypeError("Nearsol API did not return a list")
        return {"items": items, "total": len(items)}

    def parse(self, raw: Any) -> list[Job]:
        return parse_nearsol_payload(raw)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
