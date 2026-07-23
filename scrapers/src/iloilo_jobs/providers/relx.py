from __future__ import annotations

from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.clients.workday import WorkdayCxsClient
from iloilo_jobs.mappers.workday_cxs import map_workday_cxs_posting, parse_workday_cxs_payload
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

RELX_HOST = "https://relx.wd3.myworkdayjobs.com"
RELX_TENANT = "relx"
RELX_SITE = "relx"
RELX_SITE_BASE = f"{RELX_HOST}/{RELX_SITE}"


def map_relx_posting(posting: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    return map_workday_cxs_posting(
        posting,
        company_id="relx",
        site_base_url=RELX_SITE_BASE,
        scraped_at=scraped_at,
    )


def parse_relx_payload(raw: dict[str, Any], *, scraped_at: str | None = None) -> list[Job]:
    return parse_workday_cxs_payload(
        raw,
        company_id="relx",
        site_base_url=RELX_SITE_BASE,
        scraped_at=scraped_at,
    )


@provider
class RelxProvider:
    """Reed Elsevier / RELX Philippines shared-services board (Workday)."""

    company_id = "relx"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        search_text: str = "Iloilo",
        client: WorkdayCxsClient | None = None,
    ) -> None:
        self.search_text = search_text
        self._client = client or WorkdayCxsClient(
            base_host=RELX_HOST,
            tenant=RELX_TENANT,
            site=RELX_SITE,
            http=http,
        )

    def fetch_raw(self) -> dict[str, Any]:
        return self._client.fetch_all(search_text=self.search_text)

    def parse(self, raw: Any) -> list[Job]:
        if not isinstance(raw, dict):
            raise TypeError("RELX raw payload must be a dict")
        return parse_relx_payload(raw)
