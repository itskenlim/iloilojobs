from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from iloilo_jobs.models.job import Job


@runtime_checkable
class JobProvider(Protocol):
    """Fetch and parse jobs for a single company source."""

    company_id: str

    def fetch_raw(self) -> Any:
        """Return the source payload; pipeline persists it under cache/raw/."""
        ...

    def parse(self, raw: Any) -> list[Job]:
        """Map raw payload → Job list. company_name is filled during normalize."""
        ...
