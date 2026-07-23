from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.transcom import (
    map_transcom_item,
    parse_transcom_payload,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_transcom_jsonapi_fixture():
    raw = json.loads((FIXTURES / "transcom_jsonapi.json").read_text(encoding="utf-8"))
    jobs = parse_transcom_payload(raw)
    assert len(jobs) == 3
    assert all(j.company_id == "transcom" for j in jobs)
    assert all(j.source == "drupal_jsonapi" for j in jobs)
    assert all(j.city == "Iloilo" for j in jobs)


def test_parse_transcom_pageprops_fixture():
    """Matches the DevTools capture shape in webdata/transcom.txt."""
    raw = json.loads((FIXTURES / "transcom_pageprops.json").read_text(encoding="utf-8"))
    jobs = parse_transcom_payload(raw)
    assert len(jobs) >= 1
    iloilo = [j for j in jobs if j.city == "Iloilo"]
    assert len(iloilo) >= 1
    assert iloilo[0].title and "Iloilo" in iloilo[0].title


def test_transcom_mapper_fields():
    raw = json.loads((FIXTURES / "transcom_jsonapi.json").read_text(encoding="utf-8"))
    item = raw["data"][0]
    job = map_transcom_item(item)
    assert job.id.startswith("transcom:")
    assert job.raw_id == item["id"]
    assert "Iloilo" in job.title
    assert job.source_url.startswith("https://careers.transcom.com/")
    assert job.apply_url and "avature.net" in job.apply_url
