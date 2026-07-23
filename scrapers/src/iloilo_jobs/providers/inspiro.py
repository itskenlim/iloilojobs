from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from selectolax.parser import HTMLParser

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

INSPIRO_CAREERS_URL = "https://inspiro.com/careers"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug_from_url(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def parse_inspiro_careers_html(html: str, *, scraped_at: str | None = None) -> list[Job]:
    """
    Parse Inspiro careers index HTML.

    Listings rarely tag city; Inspiro PH ops are Iloilo-based (Molo), so we
    stamp city=Iloilo so the generic location filter can keep them.
    """
    scraped_at = scraped_at or _utc_now_iso()
    tree = HTMLParser(html)
    seen: set[str] = set()
    jobs: list[Job] = []

    for anchor in tree.css("a"):
        href = anchor.attributes.get("href") or ""
        if not re.match(r"https?://inspiro\.com/careers/.+", href):
            continue
        if href.rstrip("/") == INSPIRO_CAREERS_URL.rstrip("/"):
            continue
        if href in seen:
            continue
        seen.add(href)

        title = None
        node = anchor
        for _ in range(8):
            if node is None:
                break
            heading = node.css_first("h1, h2, h3, h4")
            if heading:
                title = heading.text(strip=True)
                break
            node = node.parent
        if not title:
            title = _slug_from_url(href).replace("-", " ").title()

        raw_id = _slug_from_url(href)
        jobs.append(
            Job(
                id=f"inspiro:{raw_id}",
                title=title,
                company_id="inspiro",
                company_name="",
                raw_id=raw_id,
                source="html",
                scraped_at=scraped_at,
                location="Iloilo, Philippines",
                city="Iloilo",
                province="Iloilo",
                source_url=href,
                apply_url=href,
            )
        )

    return jobs


def parse_inspiro_payload(raw: Any, *, scraped_at: str | None = None) -> list[Job]:
    if isinstance(raw, dict) and "html" in raw:
        return parse_inspiro_careers_html(raw["html"], scraped_at=scraped_at)
    if isinstance(raw, str):
        return parse_inspiro_careers_html(raw, scraped_at=scraped_at)
    raise TypeError("Inspiro raw payload must be HTML string or {html: ...}")


@provider
class InspiroProvider:
    company_id = "inspiro"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        careers_url: str = INSPIRO_CAREERS_URL,
    ) -> None:
        self.careers_url = careers_url
        self._http = http or HttpClient()
        self._owns_http = http is None

    def fetch_raw(self) -> dict[str, Any]:
        response = self._http.get(self.careers_url)
        return {
            "url": str(response.url),
            "html": response.text,
        }

    def parse(self, raw: Any) -> list[Job]:
        return parse_inspiro_payload(raw)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
