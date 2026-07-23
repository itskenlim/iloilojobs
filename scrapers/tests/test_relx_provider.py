from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.relx import map_relx_posting, parse_relx_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_relx_fixture():
    raw = json.loads((FIXTURES / "relx_cxs.json").read_text(encoding="utf-8"))
    jobs = parse_relx_payload(raw)
    assert len(jobs) >= 1
    assert all(j.company_id == "relx" for j in jobs)
    assert all(j.source == "workday" for j in jobs)


def test_relx_mapper_fields():
    raw = json.loads((FIXTURES / "relx_cxs.json").read_text(encoding="utf-8"))
    posting = raw["jobPostings"][0]
    job = map_relx_posting(posting)
    assert job.id.startswith("relx:")
    assert job.title
    assert job.source_url.startswith("https://relx.wd3.myworkdayjobs.com/relx/")
    assert job.raw_id
