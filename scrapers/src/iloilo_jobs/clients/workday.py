from __future__ import annotations

from typing import Any

from iloilo_jobs.clients.http import HttpClient


class WorkdayCxsClient:
    """Client for Workday Career Site Experience (CXS) job search API."""

    def __init__(
        self,
        *,
        base_host: str,
        tenant: str,
        site: str,
        http: HttpClient | None = None,
    ) -> None:
        self.base_host = base_host.rstrip("/")
        self.tenant = tenant
        self.site = site
        self._http = http or HttpClient()
        self._owns_http = http is None

    @property
    def jobs_url(self) -> str:
        return f"{self.base_host}/wday/cxs/{self.tenant}/{self.site}/jobs"

    def search_jobs(
        self,
        *,
        search_text: str = "",
        limit: int = 20,
        offset: int = 0,
        applied_facets: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            "appliedFacets": applied_facets or {},
            "limit": limit,
            "offset": offset,
            "searchText": search_text,
        }
        response = self._http.post(
            self.jobs_url,
            json=body,
            headers={"Content-Type": "application/json"},
        )
        return response.json()

    def fetch_all(
        self,
        *,
        search_text: str = "",
        page_size: int = 20,
        max_pages: int = 50,
    ) -> dict[str, Any]:
        """Paginate and merge jobPostings into a single CXS-shaped payload."""
        offset = 0
        all_postings: list[dict[str, Any]] = []
        facets: list[Any] = []
        total = 0

        for _ in range(max_pages):
            page = self.search_jobs(
                search_text=search_text,
                limit=page_size,
                offset=offset,
            )
            postings = page.get("jobPostings") or []
            total = int(page.get("total") or total)
            if page.get("facets"):
                facets = page["facets"]
            all_postings.extend(postings)
            offset += page_size
            if offset >= total or not postings:
                break

        return {
            "total": total or len(all_postings),
            "jobPostings": all_postings,
            "facets": facets,
            "userAuthenticated": False,
        }

    def close(self) -> None:
        if self._owns_http:
            self._http.close()
