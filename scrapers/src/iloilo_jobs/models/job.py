from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Job:
    id: str
    title: str
    company_id: str
    company_name: str
    raw_id: str
    source: str
    scraped_at: str
    location: str | None = None
    city: str | None = None
    province: str | None = None
    employment_type: str | None = None
    department: str | None = None
    salary: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    description: str | None = None
    requirements: str | None = None
    posted_at: str | None = None
    expires_at: str | None = None
    source_url: str | None = None
    apply_url: str | None = None
    remote: bool | None = None
    extra: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("extra", None)
        return data
