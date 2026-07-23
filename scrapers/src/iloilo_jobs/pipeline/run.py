from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from iloilo_jobs.models.job import Job
from iloilo_jobs.models.scrape_result import PipelineStats
from iloilo_jobs.pipeline.collect import collect
from iloilo_jobs.pipeline.deduplicate import deduplicate
from iloilo_jobs.pipeline.normalize import normalize
from iloilo_jobs.pipeline.validate import validate
from iloilo_jobs.pipeline.writer import write_outputs
from iloilo_jobs.protocols.provider import JobProvider
from iloilo_jobs.registry import get_providers

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_pipeline(
    *,
    providers: list[JobProvider] | None = None,
    company_ids: list[str] | None = None,
    cache_dir: Path,
    jobs_path: Path,
    metadata_path: Path,
    apply_location_filter: bool = True,
    location_keywords: list[str] | None = None,
    keep_history: bool = True,
) -> tuple[list[Job], PipelineStats]:
    """Orchestrate collect → normalize → dedupe → validate → writer."""
    started = time.perf_counter()
    generated_at = _utc_now_iso()

    # Ensure provider modules are imported for @provider registration
    import iloilo_jobs.providers  # noqa: F401

    active = providers if providers is not None else get_providers(
        enabled_only=True,
        company_ids=company_ids,
    )

    if not active:
        logger.warning("No providers to run")
        stats = PipelineStats(generated_at=generated_at, duration_ms=0)
        write_outputs([], stats, jobs_path=jobs_path, metadata_path=metadata_path)
        return [], stats

    collected = collect(active, cache_dir=cache_dir, keep_history=keep_history)
    normalized = normalize(
        collected.jobs,
        apply_location_filter=apply_location_filter,
        location_keywords=location_keywords,
    )
    unique, duplicates_removed = deduplicate(normalized)
    valid, validation_dropped = validate(unique)

    duration_ms = int((time.perf_counter() - started) * 1000)
    stats = PipelineStats(
        providers=len(active),
        successful_providers=collected.successful_providers,
        failed_providers=collected.failed_providers,
        failed_provider_ids=collected.failed_provider_ids,
        total_jobs=len(valid),
        duplicates_removed=duplicates_removed,
        validation_dropped=validation_dropped,
        duration_ms=duration_ms,
        generated_at=generated_at,
    )

    write_outputs(valid, stats, jobs_path=jobs_path, metadata_path=metadata_path)
    logger.info("Final dataset: %d jobs (%dms)", len(valid), duration_ms)
    return valid, stats
