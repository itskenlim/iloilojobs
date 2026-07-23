from __future__ import annotations

from typing import Any

from iloilo_jobs.clients.http import HttpClient
from iloilo_jobs.clients.workday import WorkdayCxsClient
from iloilo_jobs.mappers.workday_cxs import parse_workday_cxs_payload
from iloilo_jobs.models.job import Job
from iloilo_jobs.registry import provider

CARELON_HOST = "https://elevancehealth.wd1.myworkdayjobs.com"
CARELON_TENANT = "elevancehealth"
CARELON_SITE = "carelonglobal_ph"
CARELON_SITE_BASE = f"{CARELON_HOST}/{CARELON_SITE}"


def map_carelon_posting(posting: dict[str, Any], *, scraped_at: str | None = None) -> Job:
    from iloilo_jobs.mappers.workday_cxs import map_workday_cxs_posting

    return map_workday_cxs_posting(
        posting,
        company_id="carelon",
        site_base_url=CARELON_SITE_BASE,
        scraped_at=scraped_at,
    )


def parse_carelon_payload(raw: dict[str, Any], *, scraped_at: str | None = None) -> list[Job]:
    return parse_workday_cxs_payload(
        raw,
        company_id="carelon",
        site_base_url=CARELON_SITE_BASE,
        scraped_at=scraped_at,
    )


@provider
class CarelonProvider:
    company_id = "carelon"

    def __init__(
        self,
        *,
        http: HttpClient | None = None,
        search_text: str = "Iloilo",
        client: WorkdayCxsClient | None = None,
    ) -> None:
        self.search_text = search_text
        self._client = client or WorkdayCxsClient(
            base_host=CARELON_HOST,
            tenant=CARELON_TENANT,
            site=CARELON_SITE,
            http=http,
        )

    def fetch_raw(self) -> dict[str, Any]:
        return self._client.fetch_all(search_text=self.search_text)

    def parse(self, raw: Any) -> list[Job]:
        if not isinstance(raw, dict):
            raise TypeError("Carelon raw payload must be a dict")
        return parse_carelon_payload(raw)
