from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.iqor import map_iqor_item, parse_iqor_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_iqor_fixture():
    raw = json.loads((FIXTURES / "iqor_listdata.json").read_text(encoding="utf-8"))
    jobs = parse_iqor_payload(raw)
    assert len(jobs) >= 1
    assert all(j.company_id == "iqor" for j in jobs)
    assert all(j.source == "next_data" for j in jobs)
    assert all(j.city and "Iloilo" in j.city for j in jobs)


def test_iqor_mapper_fields():
    raw = json.loads((FIXTURES / "iqor_listdata.json").read_text(encoding="utf-8"))
    item = raw["pageProps"]["listData"][0]
    job = map_iqor_item(item)
    assert job.id.startswith("iqor:")
    assert job.raw_id == str(item["jobPostingID"])
    assert job.title == item["jobTitleName"]
    assert job.city and "Iloilo" in job.city
    assert job.source_url.endswith(f"/jobs/{item['jobPostingID']}")
