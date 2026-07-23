from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class Company:
    id: str
    name: str
    website: str | None = None
    careers_url: str | None = None
    logo: str | None = None
    city: str | None = None
    enabled: bool = True
    source_kind: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Company:
        return cls(
            id=data["id"],
            name=data["name"],
            website=data.get("website"),
            careers_url=data.get("careers_url"),
            logo=data.get("logo"),
            city=data.get("city"),
            enabled=bool(data.get("enabled", True)),
            source_kind=data.get("source_kind"),
        )


def _load_company_dict(company_id: str) -> dict[str, Any]:
    package = "iloilo_jobs.companies"
    resource_name = f"{company_id}.json"
    try:
        text = resources.files(package).joinpath(resource_name).read_text(encoding="utf-8")
        return json.loads(text)
    except (FileNotFoundError, TypeError, ModuleNotFoundError):
        # Fallback for editable installs / source tree
        path = Path(__file__).resolve().parent.parent / "companies" / resource_name
        return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=64)
def load_company(company_id: str) -> Company:
    return Company.from_dict(_load_company_dict(company_id))


def list_company_ids() -> list[str]:
    try:
        root = resources.files("iloilo_jobs.companies")
        return sorted(
            p.name.removesuffix(".json")
            for p in root.iterdir()
            if p.name.endswith(".json")
        )
    except (FileNotFoundError, TypeError, ModuleNotFoundError):
        path = Path(__file__).resolve().parent.parent / "companies"
        return sorted(p.stem for p in path.glob("*.json"))
