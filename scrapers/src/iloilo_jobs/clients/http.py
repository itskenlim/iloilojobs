from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; IloiloJobsBot/0.1; "
        "+https://github.com/iloilojobs)"
    ),
    "Accept": "application/json, text/html, */*",
}


class HttpClient:
    """Thin httpx wrapper with shared defaults."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout,
            headers={**DEFAULT_HEADERS, **(headers or {})},
            follow_redirects=True,
        )

    def get(
        self,
        url: str,
        *,
        raise_for_status: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        response = self._client.get(url, **kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response

    def post(
        self,
        url: str,
        *,
        raise_for_status: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        response = self._client.post(url, **kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
