from __future__ import annotations

from typing import Any

from iloilo_jobs.clients.http import HttpClient


class SmartRecruitersClient:
    """Public SmartRecruiters postings API."""

    BASE = "https://api.smartrecruiters.com/v1/companies"

    def __init__(
        self,
        company_identifier: str,
        *,
        http: HttpClient | None = None,
    ) -> None:
        self.company_identifier = company_identifier
        self._http = http or HttpClient()
        self._owns_http = http is None

    @property
    def postings_url(self) -> str:
        return f"{self.BASE}/{self.company_identifier}/postings"

    def list_postings(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        country: str | None = None,
        q: str | None = None,
        city: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if country:
            params["country"] = country
        if q:
            params["q"] = q
        if city:
            params["city"] = city
        response = self._http.get(self.postings_url, params=params)
        return response.json()

    def fetch_all(
        self,
        *,
        country: str | None = "ph",
        q: str | None = "Iloilo",
        city: str | None = None,
        page_size: int = 100,
        max_pages: int = 20,
    ) -> dict[str, Any]:
        offset = 0
        content: list[dict[str, Any]] = []
        total_found = 0

        for _ in range(max_pages):
            page = self.list_postings(
                offset=offset,
                limit=page_size,
                country=country,
                q=q,
                city=city,
            )
            batch = page.get("content") or []
            total_found = int(page.get("totalFound") or total_found)
            content.extend(batch)
            offset += page_size
            if offset >= total_found or not batch:
                break

        return {
            "offset": 0,
            "limit": len(content),
            "totalFound": total_found or len(content),
            "content": content,
        }

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
