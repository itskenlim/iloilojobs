from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.concentrix import map_concentrix_posting, parse_concentrix_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_concentrix_fixture():
    raw = json.loads((FIXTURES / "concentrix_cxs.json").read_text(encoding="utf-8"))
    jobs = parse_concentrix_payload(raw)
    assert len(jobs) == 15
    assert all(j.company_id == "concentrix" for j in jobs)
    assert all(j.source == "workday" for j in jobs)


def test_concentrix_mapper_fields():
    raw = json.loads((FIXTURES / "concentrix_cxs.json").read_text(encoding="utf-8"))
    posting = next(p for p in raw["jobPostings"] if "Iloilo" in (p.get("title") or "") + (p.get("externalPath") or ""))
    job = map_concentrix_posting(posting)
    assert job.id.startswith("concentrix:")
    assert job.raw_id
    assert "Iloilo" in (job.title + (job.source_url or "") + (job.location or ""))
    assert job.source_url.startswith("https://cnx.wd1.myworkdayjobs.com/external_global/")
    assert job.apply_url == job.source_url
