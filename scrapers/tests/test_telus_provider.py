from __future__ import annotations

import json
from pathlib import Path

from iloilo_jobs.providers.telus import map_telus_entry, parse_telus_payload

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_telus_fixture():
    raw = json.loads((FIXTURES / "telus_talemetry.json").read_text(encoding="utf-8"))
    jobs = parse_telus_payload(raw)
    assert len(jobs) == 9
    assert all(j.company_id == "telus" for j in jobs)
    assert all(j.source == "talemetry" for j in jobs)
    assert all(j.province == "Iloilo" for j in jobs)


def test_telus_includes_pavia_roles():
    raw = json.loads((FIXTURES / "telus_talemetry.json").read_text(encoding="utf-8"))
    jobs = parse_telus_payload(raw)
    titles = {j.title for j in jobs}
    assert "Operations CSR II" in titles
    assert "Real Time Analyst" in titles
    assert "Customer Experience Manager" in titles
    pavia = [j for j in jobs if j.city == "Pavia"]
    assert len(pavia) >= 5


def test_telus_mapper_fields():
    raw = json.loads((FIXTURES / "telus_talemetry.json").read_text(encoding="utf-8"))
    entry = next(e for e in raw["entries"] if e["title"] == "Operations CSR")
    job = map_telus_entry(entry)
    assert job.id == f"telus:{entry['id']}"
    assert job.title == "Operations CSR"
    assert job.city == "Iloilo"
    assert job.location == "PH - Iloilo"
    assert job.source_url.endswith(f"?jid={entry['id']}")
