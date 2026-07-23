from __future__ import annotations

from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.clients.workday import WorkdayCxsClient
from iloilo_jobs.mappers.workday_cxs import map_workday_cxs_posting, parse_workday_cxs_payload
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

ASURION_HOST = "https://asurion.wd5.myworkdayjobs.com"
ASURION_TENANT = "asurion"
ASURION_SITE = "Asurion_Careers"
ASURION_SITE_BASE = f"{ASURION_HOST}/{ASURION_SITE}"


def map_asurion_posting(posting: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    return map_workday_cxs_posting(
        posting,
        company_id="asurion",
        site_base_url=ASURION_SITE_BASE,
        scraped_at=scraped_at,
    )


def parse_asurion_payload(raw: dict[str, Any], *, scraped_at: str | None = None) -> list[Job]:
    return parse_workday_cxs_payload(
        raw,
        company_id="asurion",
        site_base_url=ASURION_SITE_BASE,
        scraped_at=scraped_at,
    )


@provider
class AsurionProvider:
    """Asurion Iloilo roles via Workday CXS (Phenom UI is a veneer over the same board)."""

    company_id = "asurion"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        search_text: str = "Iloilo",
        client: WorkdayCxsClient | None = None,
    ) -> None:
        self.search_text = search_text
        self._client = client or WorkdayCxsClient(
            base_host=ASURION_HOST,
            tenant=ASURION_TENANT,
            site=ASURION_SITE,
            http=http,
        )

    def fetch_raw(self) -> dict[str, Any]:
        return self._client.fetch_all(search_text=self.search_text)

    def parse(self, raw: Any) -> list[Job]:
        if not isinstance(raw, dict):
            raise TypeError("Asurion raw payload must be a dict")
        return parse_asurion_payload(raw)
