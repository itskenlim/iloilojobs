from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from iloilo_jobs.models.scrape_result import CollectResult, ProviderResult
from iloilo_jobs.protocols.provider import JobProvider

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def save_raw_cache(
    company_id: str,
    payload: Any,
    *,
    cache_dir: Path,
    ok: bool = True,
    error: str | None = None,
    keep_history: bool = True,
) -> Path:
    """Write latest raw payload (+ optional timestamped history copy)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fetched_at = _utc_now_iso()
    envelope = {
        "company_id": company_id,
        "fetched_at": fetched_at,
        "ok": ok,
        "error": error,
        "payload": payload,
    }
    latest_path = cache_dir / f"{company_id}.json"
    latest_path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")

    if keep_history:
        stamp = fetched_at.replace(":", "").replace("-", "")
        history_dir = cache_dir / company_id
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path = history_dir / f"{stamp}.json"
        history_path.write_text(
            json.dumps(envelope, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return latest_path


def collect(
    providers: list[JobProvider],
    *,
    cache_dir: Path,
    keep_history: bool = True,
) -> CollectResult:
    """Fetch + parse each provider; isolate failures."""
    results: list[ProviderResult] = []

    for provider in providers:
        company_id = provider.company_id
        started = time.perf_counter()
        try:
            raw = provider.fetch_raw()
            save_raw_cache(
                company_id,
                raw,
                cache_dir=cache_dir,
                ok=True,
                keep_history=keep_history,
            )
            jobs = provider.parse(raw)
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "%s fetched %d jobs (%dms)",
                company_id,
                len(jobs),
                duration_ms,
            )
            results.append(
                ProviderResult(
                    company_id=company_id,
                    ok=True,
                    jobs=jobs,
                    duration_ms=duration_ms,
                    raw=raw,
                )
            )
        except Exception as exc:  # noqa: BLE001 — isolate provider failures
            duration_ms = int((time.perf_counter() - started) * 1000)
            error = f"{type(exc).__name__}: {exc}"
            logger.error("%s fetch failed: %s", company_id, error)
            try:
                save_raw_cache(
                    company_id,
                    None,
                    cache_dir=cache_dir,
                    ok=False,
                    error=error,
                    keep_history=keep_history,
                )
            except OSError:
                logger.warning("Could not write raw cache for failed provider %s", company_id)
            results.append(
                ProviderResult(
                    company_id=company_id,
                    ok=False,
                    jobs=[],
                    error=error,
                    duration_ms=duration_ms,
                )
            )

    return CollectResult(results=results)
