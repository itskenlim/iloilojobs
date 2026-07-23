from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.models.job import Job
from iloilo_jobs.pipeline.collect import collect
from iloilo_jobs.pipeline.deduplicate import deduplicate
from iloilo_jobs.pipeline.normalize import normalize
from iloilo_jobs.pipeline.run import run_pipeline
from iloilo_jobs.pipeline.validate import validate
from iloilo_jobs.providers.carelon import parse_carelon_payload
from iloilo_jobs.providers.iqor import parse_iqor_payload

FIXTURES = Path(__file__).parent / "fixtures"


class FixtureProvider:
    def __init__(self, company_id: str, raw: dict, parser):
        self.company_id = company_id
        self._raw = raw
        self._parser = parser

    def fetch_raw(self):
        return self._raw

    def parse(self, raw):
        return self._parser(raw)


class FailingProvider:
    company_id = "broken"

    def fetch_raw(self):
        raise RuntimeError("boom")

    def parse(self, raw):
        return []


def test_collect_isolates_failures(tmp_path: Path):
    carelon_raw = json.loads((FIXTURES / "carelon_cxs.json").read_text(encoding="utf-8"))
    providers = [
        FixtureProvider("carelon", carelon_raw, parse_carelon_payload),
        FailingProvider(),
    ]
    result = collect(providers, cache_dir=tmp_path / "raw", keep_history=False)
    assert result.successful_providers == 1
    assert result.failed_providers == 1
    assert "broken" in result.failed_provider_ids
    assert len(result.jobs) == 14
    assert (tmp_path / "raw" / "carelon.json").exists()


def test_deduplicate_and_validate():
    jobs = [
        Job(
            id="a:1",
            title="A",
            company_id="a",
            company_name="A",
            raw_id="1",
            source="t",
            scraped_at="2026-07-23T00:00:00Z",
            source_url="https://example.com/1",
        ),
        Job(
            id="a:1",
            title="A dup",
            company_id="a",
            company_name="A",
            raw_id="1",
            source="t",
            scraped_at="2026-07-23T00:00:00Z",
            source_url="https://example.com/1",
        ),
        Job(
            id="a:2",
            title="No url",
            company_id="a",
            company_name="A",
            raw_id="2",
            source="t",
            scraped_at="2026-07-23T00:00:00Z",
        ),
    ]
    unique, removed = deduplicate(jobs)
    assert removed == 1
    assert len(unique) == 2
    valid, dropped = validate(unique)
    assert dropped == 1
    assert len(valid) == 1


def test_normalize_filters_non_iloilo():
    jobs = [
        Job(
            id="carelon:JR1",
            title="Iloilo Role",
            company_id="carelon",
            company_name="",
            raw_id="JR1",
            source="workday",
            scraped_at="",
            location="PHL-ILO-One Fintech Place",
            source_url="https://example.com/ilo",
        ),
        Job(
            id="carelon:JR2",
            title="Taguig Role",
            company_id="carelon",
            company_name="",
            raw_id="JR2",
            source="workday",
            scraped_at="",
            location="Taguig - BGC",
            source_url="https://example.com/taguig",
        ),
    ]
    out = normalize(jobs, apply_location_filter=True)
    assert len(out) == 1
    assert out[0].raw_id == "JR1"
    assert out[0].company_name == "Carelon Global Solutions"


def test_run_pipeline_with_fixtures(tmp_path: Path):
    carelon_raw = json.loads((FIXTURES / "carelon_cxs.json").read_text(encoding="utf-8"))
    iqor_raw = json.loads((FIXTURES / "iqor_listdata.json").read_text(encoding="utf-8"))
    providers = [
        FixtureProvider("carelon", carelon_raw, parse_carelon_payload),
        FixtureProvider("iqor", iqor_raw, parse_iqor_payload),
        FailingProvider(),
    ]
    jobs_path = tmp_path / "jobs.json"
    meta_path = tmp_path / "metadata.json"
    jobs, stats = run_pipeline(
        providers=providers,
        cache_dir=tmp_path / "raw",
        jobs_path=jobs_path,
        metadata_path=meta_path,
        apply_location_filter=True,
        keep_history=False,
    )
    assert stats.providers == 3
    assert stats.successful_providers == 2
    assert stats.failed_providers == 1
    assert stats.total_jobs == len(jobs)
    assert jobs_path.exists()
    assert meta_path.exists()
    envelope = json.loads(jobs_path.read_text(encoding="utf-8"))
    assert envelope["job_count"] == len(jobs)
    assert all(
        "iloilo" in (j.get("location") or j.get("city") or "").lower()
        or "ilo" in (j.get("location") or "").lower()
        or "iloilo" in (j.get("source_url") or "").lower()
        or "phl-ilo" in (j.get("source_url") or "").lower()
        for j in envelope["jobs"]
    )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["failed_provider_ids"] == ["broken"]
    assert meta["total_jobs"] == len(jobs)
