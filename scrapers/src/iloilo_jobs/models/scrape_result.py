from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from iloilo_jobs.models.job import Job


@dataclass(slots=True)
class ProviderResult:
    company_id: str
    ok: bool
    jobs: list[Job] = field(default_factory=list)
    error: str | None = None
    duration_ms: int = 0
    raw: Any = None


@dataclass(slots=True)
class CollectResult:
    results: list[ProviderResult] = field(default_factory=list)

    @property
    def jobs(self) -> list[Job]:
        out: list[Job] = []
        for result in self.results:
            out.extend(result.jobs)
        return out

    @property
    def successful_providers(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def failed_providers(self) -> int:
        return sum(1 for r in self.results if not r.ok)

    @property
    def failed_provider_ids(self) -> list[str]:
        return [r.company_id for r in self.results if not r.ok]


@dataclass(slots=True)
class PipelineStats:
    providers: int = 0
    successful_providers: int = 0
    failed_providers: int = 0
    failed_provider_ids: list[str] = field(default_factory=list)
    total_jobs: int = 0
    duplicates_removed: int = 0
    validation_dropped: int = 0
    duration_ms: int = 0
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "providers": self.providers,
            "successful_providers": self.successful_providers,
            "failed_providers": self.failed_providers,
            "failed_provider_ids": self.failed_provider_ids,
            "total_jobs": self.total_jobs,
            "duplicates_removed": self.duplicates_removed,
            "validation_dropped": self.validation_dropped,
            "duration_ms": self.duration_ms,
        }
