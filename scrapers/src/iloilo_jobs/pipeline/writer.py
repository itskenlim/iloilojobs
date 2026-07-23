from __future__ import annotations

import json
import logging
from pathlib import Path

from iloilo_jobs.models.job import Job
from iloilo_jobs.models.scrape_result import PipelineStats

logger = logging.getLogger(__name__)


def write_outputs(
    jobs: list[Job],
    stats: PipelineStats,
    *,
    jobs_path: Path,
    metadata_path: Path,
) -> None:
    """Write jobs.json and metadata.json."""
    jobs_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    company_ids = sorted({job.company_id for job in jobs})
    envelope = {
        "generated_at": stats.generated_at,
        "job_count": len(jobs),
        "companies": company_ids,
        "jobs": [job.to_dict() for job in jobs],
    }

    jobs_path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata_path.write_text(
        json.dumps(stats.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote %d jobs → %s", len(jobs), jobs_path)
    logger.info("Wrote metadata → %s", metadata_path)
