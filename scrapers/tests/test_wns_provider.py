from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.wns import map_wns_posting, parse_wns_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_wns_fixture():
    raw = json.loads((FIXTURES / "wns_postings.json").read_text(encoding="utf-8"))
    jobs = parse_wns_payload(raw)
    assert len(jobs) == 6
    assert all(j.company_id == "wns" for j in jobs)
    assert all(j.source == "smartrecruiters" for j in jobs)
    assert all(j.city and "Iloilo" in j.city for j in jobs)


def test_wns_mapper_fields():
    raw = json.loads((FIXTURES / "wns_postings.json").read_text(encoding="utf-8"))
    item = raw["content"][0]
    job = map_wns_posting(item)
    assert job.id == f"wns:{item['id']}"
    assert job.raw_id == str(item["id"])
    assert "Iloilo" in (job.title + (job.location or ""))
    assert job.source_url == f"https://jobs.smartrecruiters.com/WNSGlobalServices144/{item['id']}"
    assert job.employment_type == "Full-time"
