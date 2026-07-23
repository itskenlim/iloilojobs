from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.asurion import map_asurion_posting, parse_asurion_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_asurion_fixture_count():
    raw = json.loads((FIXTURES / "asurion_cxs.json").read_text(encoding="utf-8"))
    jobs = parse_asurion_payload(raw)
    assert len(jobs) == 4
    assert all(j.company_id == "asurion" for j in jobs)
    assert all(j.source == "workday" for j in jobs)
    assert {j.raw_id for j in jobs} >= {"ASU0014118", "ASU0014119", "ASU0020687"}


def test_asurion_mapper_fields():
    raw = json.loads((FIXTURES / "asurion_cxs.json").read_text(encoding="utf-8"))
    posting = next(p for p in raw["jobPostings"] if "ASU0014118" in (p.get("bulletFields") or []))
    job = map_asurion_posting(posting)
    assert job.id == "asurion:ASU0014118"
    assert job.raw_id == "ASU0014118"
    assert job.title == "Technical Support Representative - Iloilo"
    assert job.location and "Iloilo" in job.location
    assert job.city == "Iloilo"
    assert job.source_url and job.source_url.startswith(
        "https://asurion.wd5.myworkdayjobs.com/Asurion_Careers/"
    )
    assert job.apply_url == job.source_url
