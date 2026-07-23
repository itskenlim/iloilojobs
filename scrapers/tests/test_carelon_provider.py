from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.carelon import map_carelon_posting, parse_carelon_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_carelon_fixture_count():
    raw = json.loads((FIXTURES / "carelon_cxs.json").read_text(encoding="utf-8"))
    jobs = parse_carelon_payload(raw)
    assert len(jobs) == 14
    assert all(j.company_id == "carelon" for j in jobs)
    assert all(j.source == "workday" for j in jobs)


def test_carelon_mapper_fields():
    raw = json.loads((FIXTURES / "carelon_cxs.json").read_text(encoding="utf-8"))
    posting = raw["jobPostings"][0]
    job = map_carelon_posting(posting)
    assert job.id == "carelon:JR199853"
    assert job.raw_id == "JR199853"
    assert "Customer Care" in job.title
    assert job.location and "Iloilo" in job.location
    assert job.city == "Iloilo"
    assert job.employment_type == "Full time"
    assert job.source_url and job.source_url.startswith("https://elevancehealth.wd1.myworkdayjobs.com/")
    assert job.apply_url == job.source_url
