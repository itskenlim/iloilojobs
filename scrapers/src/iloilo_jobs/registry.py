from __future__ import annotations

import logging
from typing import TypeVar

from iloilo_jobs.models.company import load_company
from iloilo_jobs.protocols.provider import JobProvider

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, type] = {}

T = TypeVar("T")


def provider(cls: type[T]) -> type[T]:
    """Register a JobProvider class for auto-discovery."""
    company_id = getattr(cls, "company_id", None)
    if not company_id or not isinstance(company_id, str):
        raise TypeError(f"{cls.__name__} must define a string company_id")
    if company_id in _REGISTRY:
        existing = _REGISTRY[company_id].__name__
        raise ValueError(
            f"Duplicate provider for company_id={company_id!r}: "
            f"{existing} and {cls.__name__}"
        )
    _REGISTRY[company_id] = cls
    return cls


def clear_registry() -> None:
    """Clear registered providers (tests only)."""
    _REGISTRY.clear()


def registered_ids() -> list[str]:
    return sorted(_REGISTRY.keys())


def get_provider_class(company_id: str) -> type:
    if company_id not in _REGISTRY:
        raise KeyError(f"No provider registered for {company_id!r}")
    return _REGISTRY[company_id]


def get_providers(
    *,
    enabled_only: bool = True,
    company_ids: list[str] | None = None,
) -> list[JobProvider]:
    """
    Instantiate registered providers.

    Import iloilo_jobs.providers before calling so decorators have run.
    """
    ids = company_ids if company_ids is not None else registered_ids()
    providers: list[JobProvider] = []
    for company_id in ids:
        if company_id not in _REGISTRY:
            logger.warning("No provider registered for %s — skipped", company_id)
            continue
        if enabled_only:
            try:
                company = load_company(company_id)
            except FileNotFoundError:
                logger.warning("Missing company metadata for %s — skipped", company_id)
                continue
            if not company.enabled:
                logger.info("%s skipped (disabled in company metadata)", company.name)
                continue
        cls = _REGISTRY[company_id]
        providers.append(cls())  # type: ignore[call-arg]
    return providers
